import pandas as pd
import numpy as np
import openai
from sklearn.metrics.pairwise import cosine_similarity
import re

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "02e96096dcb24ab3b53a63049aa52155"  # Replace with your OpenAI API key


# Refine and merge overlapping labels with a stricter emphasis on specificity
def refine_and_merge_labels(labels_dict):
    all_labels = []
    for scholar_labels in labels_dict.values():
        all_labels.extend(scholar_labels)

    # Combine all labels into a single string for GPT
    label_string = "\n".join(all_labels)

    # Stricter prompt with explicit emphasis on narrow, specific themes
    prompt = (
        "You are an expert in international relations, sustainability, and water diplomacy. "
        "We have 21 labels, each reflecting a scholar’s perspective on recent news clusters. "
        "Your task is to refine these labels aggressively, aiming for fewer than 10 highly specific and narrowly defined labels. "
        "Each label should be no more than 4-5 words and focus on a distinct, tangible aspect of transboundary water management, such as 'joint data-sharing systems,' 'cross-border basin agreements,' 'adaptive flood management,' or 'integrated drought risk protocols.' "
        "Avoid broad or vague terms like 'environmental peacebuilding,' 'conflict resolution,' or 'water diplomacy,' and do not use general terms like 'frameworks' or 'initiatives.' "
        "Labels should clearly reflect precise mechanisms, governance approaches, collaborative models, or technical measures related to water cooperation. "
        "Ensure that the labels do not refer to any specific region, time frame, or controversial case, like the Colorado River Compact, Murray-Darling Basin Plan, Three Gorges Dam, or GERD. "
        "The final list should feature distinctive and non-overlapping labels that capture unique aspects of transboundary cooperation."
        "Return only the refined list of concise, specific labels, without explanations or additional text."
        "\n\nHere are the labels:\n\n" + label_string
    )

    try:
        # Call GPT to refine the labels
        response = openai.ChatCompletion.create(
            engine="rag",  # Use GPT-4 or the model you're working with
            messages=[
                {"role": "system", "content": "You are a content expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500  # Adjust the token limit for concise responses
        )

        # Extract the condensed labels from GPT response
        final_portfolio = response['choices'][0]['message']['content'].strip().split("\n")
        return final_portfolio

    except Exception as e:
        print(f"Error refining labels: {e}")
        return []


# Initialize cache for similarity checks
similarity_cache = {}


# Extract event titles specifically from example lines
def extract_example_titles(examples_text):
    """
    Extract titles from lines that are likely to be examples.
    Examples are assumed to start with numbering like '1.', '2.', etc.
    """
    example_titles = []
    lines = examples_text.split("\n")

    for line in lines:
        # Use regex to find lines that start with a number (e.g., '1.', '2.', etc.)
        match = re.match(r'^\d+\.\s\*\*(.+?)\*\*', line)
        if match:
            title = match.group(1).strip()  # Extract the event title
            example_titles.append(title)

    return example_titles


# Check if a new example's title is the same as any of the existing example titles
def is_semantically_same_event(new_example_title, existing_titles, relaxed=False):
    # Prepare the similarity checking prompt
    system_message = (
        "You are an expert in identifying if two event titles refer to the same underlying case, even if worded differently. "
        "If the new event title refers to the same event as any of the existing titles, respond with 'Yes'. Otherwise, respond with 'No'."
    )

    user_note = "Consider examples similar only if they are exact matches." if relaxed else "Consider examples similar even if they share overlapping themes."

    user_template = (
        f"{user_note}\n\n"
        f"New event title: {new_example_title}\n\n"
        f"Existing event titles:\n"
        + "\n".join(existing_titles) +
        "\n\nIs the new event title the same as any of the existing ones? Respond with 'Yes' or 'No' only."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_template}
    ]

    try:
        response = openai.ChatCompletion.create(
            engine="rag",  # Azure deployment name for GPT-4
            messages=messages,
            temperature=0,
            max_tokens=5  # Minimal tokens for 'Yes' or 'No' response
        )

        similarity_response = response['choices'][0]['message']['content'].strip().lower()
        print(f"Checked semantic similarity for title '{new_example_title}': {similarity_response.capitalize()}")
        return similarity_response == "yes"

    except Exception as e:
        print(f"Failed to check semantic similarity for title '{new_example_title}'. Error: {e}")
        return True  # Assume same if check fails, to be conservative


# Generate descriptions and broader batches of examples, with partial retry logic# Generate descriptions and broader batches of examples, with partial retry logic
def generate_description_and_examples(label, used_examples, all_generated_examples, max_retries=10):
    system_message = (
        "You are an international relations expert specializing in water diplomacy, sustainability science, and hydrology. "
        "Ensure that all examples reflect cooperative transboundary water management, are highly specific, and do not include references to contentious cases."
    )

    final_titles = []  # To hold the successfully generated example titles
    retry_count = 0

    while len(final_titles) < 3 and retry_count < max_retries:
        print(f"\nGenerating new examples for label '{label}' (Attempt {retry_count + 1})")

        # Generate a larger batch of examples for better variety
        batch_size = max(5, 3 - len(final_titles))  # Generate at least 5 examples
        user_template = (
            f"Based on the following label, write a detailed description and provide {batch_size} unique examples of real-world events or cases that match this label."
            f" Make sure that no example refers to the same event as any previously generated example."
            f" Exclude examples like the Colorado River Compact (1922), Murray-Darling Basin Plan (Australia), Three Gorges Dam (China), and Grand Ethiopian Renaissance Dam (GERD, Ethiopia)."
            f" Ensure that the examples are distinct, specific, and relevant to transboundary cooperation.\n\n"
            f"Label: {label}\n\n"
            f"Write a paragraph explaining what this label means, followed by {batch_size} relevant examples."
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_template}
        ]

        try:
            response = openai.ChatCompletion.create(
                engine="rag",  # Azure deployment name for GPT-4
                messages=messages,
                temperature=0.7,
                max_tokens=1000  # Adjusted for broader generation
            )

            if 'choices' not in response or not response['choices']:
                raise ValueError("No response received from GPT.")

            description_and_examples = response['choices'][0]['message']['content'].strip()

            # Extract titles from the generated examples
            new_example_titles = extract_example_titles(description_and_examples)

            # Check each new example title individually
            for title in new_example_titles:
                if title not in all_generated_examples and not is_semantically_same_event(title, used_examples, relaxed=retry_count >= max_retries // 2):
                    final_titles.append(title)
                    used_examples.add(title)  # Add to label-specific list
                    all_generated_examples.add(title)  # Add to global list
                    print(f"Accepted example title: '{title}'")
                else:
                    print(f"Rejected as duplicate or semantically same: '{title}'")

                # If 3 unique examples are found, break out of the loop
                if len(final_titles) == 3:
                    break

            # If fewer than 3 unique titles are found, increment retry count
            if len(final_titles) < 3:
                retry_count += 1
                print(f"Retrying to generate more unique examples for label '{label}' (Attempt {retry_count}/{max_retries})")
                continue

        except Exception as e:
            print(f"Failed to generate description and examples for label '{label}'. Error: {e}")
            return f"Description and examples could not be generated for label: {label}"

    # Update description with only 3 unique examples
    if len(final_titles) == 3:
        unique_description = (
            f"{description_and_examples.split('Write a paragraph explaining')[0]}"
            f"Write a paragraph explaining what this label means, followed by these three relevant examples:\n"
            f"1. {final_titles[0]}\n"
            f"2. {final_titles[1]}\n"
            f"3. {final_titles[2]}"
        )
        print(f"Successfully generated 3 unique example titles for label '{label}'")
        return unique_description
    else:
        print(f"Could not generate 3 unique examples for label '{label}' after {max_retries} attempts.")
        return f"Label: {label} (Not enough unique examples generated)"

# Generate labels for all clusters, merge them, and create final portfolio with descriptions and examples
def generate_labels_for_all_clusters(labels):

    used_examples = set()  # Track examples used for the current label
    all_generated_examples = set()  # Track all examples globally across labels

    with open(labels, "r") as file:
        raw_labels = file.readlines()

    # Step 2: Process the raw labels to create labels_dict
    labels_dict = {}
    current_scholar = None

    for line in raw_labels:
        # Detect new scholar section
        if line.startswith("Scholar"):
            current_scholar = line.strip()
            labels_dict[current_scholar] = []
        elif current_scholar:
            labels_dict[current_scholar].append(line.strip())

    with open("final_portfolio.txt", "w") as output_file:
        merged_labels = refine_and_merge_labels(labels_dict)

        output_file.write("\nFinal Merged Labels with Descriptions and Examples:\n")
        for merged_label in merged_labels:
            # Now passing the global all_generated_examples argument
            description_and_examples = generate_description_and_examples(merged_label, used_examples, all_generated_examples)
            output_file.write(f"Final Label: {merged_label}\n")
            output_file.write(f"{description_and_examples}\n\n")

    print("Cluster labels, descriptions, and unique examples have been generated and saved to 'final_portfolio.txt'.")

if __name__ == "__main__":
    generate_labels_for_all_clusters('cluster_labels_and_descriptions.txt')
