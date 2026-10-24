import pandas as pd
import numpy as np
import openai
from sklearn.metrics.pairwise import cosine_similarity
import ast

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "02e96096dcb24ab3b53a63049aa52155"  # Replace with your OpenAI API key

def summarize_literature(text, max_tokens=2000):
    """
    Summarize a given literature text to reduce its size.
    """
    system_message = "Summarize the following text into a concise paragraph, highlighting only the main points."

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": text}
    ]

    try:
        response = openai.ChatCompletion.create(
            engine="rag",
            messages=messages,
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Failed to summarize literature: {e}")
        return text[:max_tokens]  # Return truncated text if summarization fails

# Load the clustered event data
def load_clustered_data(file_path):
    return pd.read_excel(file_path)

# Load the literature embeddings from a CSV file
def load_literature_embeddings(file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Extract the 1536 embedding columns
        embedding_columns = [f"embedding_{i}" for i in range(1536)]
        embeddings = df[embedding_columns].values

        # Extract the original text
        original_texts = df['text'].tolist()

        return embeddings, original_texts
    except Exception as e:
        print(f"Error loading literature embeddings: {e}")
        return np.array([]), []

# Load the precomputed news embeddings from a CSV file
def load_news_embeddings(news_embeddings_file):
    return pd.read_csv(news_embeddings_file).values

# Randomly sample entries from a specific cluster
def sample_from_cluster(event_data, cluster_label, sample_size=5):
    cluster_data = event_data[event_data['cluster'] == cluster_label]
    sampled_entries = cluster_data.sample(n=sample_size, random_state=42)
    return sampled_entries['augment by llm'].tolist(), sampled_entries.index  # Return text and indices

# Retrieve the most similar literature using cosine similarity
def retrieve_relevant_literature(literature_embeddings, sample_embeddings, original_texts, top_n=5, max_tokens=200):
    sample_embeddings = sample_embeddings[:, :1536]
    summarized_texts = []
    seen_texts = set()

    # Compute similarity matrix for the current set of sample embeddings
    similarity_matrix = cosine_similarity(sample_embeddings, literature_embeddings)

    # Get top_n indices for each sample in the current cluster
    top_literature_indices = []
    for row in similarity_matrix:
        top_indices = np.argsort(-row)[:top_n]
        top_literature_indices.extend(top_indices)

    # Deduplicate indices while preserving order
    unique_indices = list(dict.fromkeys(top_literature_indices))

    # Summarize the selected literature texts
    for idx in unique_indices:
        if idx < len(original_texts) and original_texts[idx] not in seen_texts:
            summary = summarize_literature(original_texts[idx], max_tokens=max_tokens)

            if summary not in seen_texts:
                summarized_texts.append(summary)
                seen_texts.add(summary)

            if len(summarized_texts) >= top_n:
                break

    return unique_indices, summarized_texts


# Generate a label for the cluster using GPT and the retrieved literature
def generate_cluster_label(sampled_entries, summarized_literature_texts, cluster_label, scholar_type):
    if not sampled_entries:
        print(f"No sampled entries for cluster {cluster_label}")
    if not summarized_literature_texts:
        print(f"No summarized literature for cluster {cluster_label}")

    if not sampled_entries or not summarized_literature_texts:
        return f"Cluster {cluster_label}: General Thematic Area (Insufficient context for detailed label)"

    combined_entries = "\n\n".join(sampled_entries)
    literature_texts = "\n\n".join([f"Literature {i+1}: {text}" for i, text in enumerate(summarized_literature_texts)])
    print(literature_texts)

    system_message = f"You're a {scholar_type} scholar specializing in transboundary water management."

    user_template = (
        f"Using the knowledge from the following events and summarized literature, generate a specific label for this news cluster."
        f" The events and literature are provided below:\n\n"
        f"EVENTS:\n\n{combined_entries}\n\n"
        f"LITERATURE:\n\n{literature_texts}\n\n"
        f"Create a concise and descriptive label, a brief description, and 3 examples that reflect the core theme of this cluster."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_template}
    ]

    try:
        response = openai.ChatCompletion.create(
            engine="rag",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Failed to generate a cluster label for Cluster {cluster_label}. Error: {e}")
        return f"Cluster {cluster_label}: General Thematic Area (Insufficient context for detailed label)"

# Generate labels for all clusters, merge them, and create final portfolio with descriptions and examples
def generate_labels_for_all_clusters(event_data_file, literature_embeddings_file, news_embeddings_file, num_clusters=7, sample_size=5, top_n_literature=5):
    event_data = load_clustered_data(event_data_file)
    literature_embeddings, original_texts = load_literature_embeddings(literature_embeddings_file)
    news_embeddings = load_news_embeddings(news_embeddings_file)

    scholar_types = ["International Relations", "Sustainable Science", "Hydrology"]
    labels_dict = {}

    with open("cluster_labels_and_descriptions.txt", "w") as output_file:
        for cluster_label in range(num_clusters):
            sampled_entries, sampled_indices = sample_from_cluster(event_data, cluster_label, sample_size)

            # Check if sampled entries are found, if not, continue to the next cluster
            if not sampled_entries:
                print(f"No entries found for cluster {cluster_label} in sample.")
                continue  # Skip to the next cluster if no entries found

            # Get the embeddings for the sampled entries
            sample_embeddings = news_embeddings[sampled_indices]

            # Retrieve relevant literature
            relevant_literature_indices, relevant_literature_texts = retrieve_relevant_literature(literature_embeddings, sample_embeddings, original_texts, top_n=top_n_literature)

            # Check if any literature is found for the cluster
            if not relevant_literature_texts:
                print(f"No summarized literature for cluster {cluster_label}")
                continue  # Skip to the next cluster if no literature is found

            scholar_labels = []
            for scholar in scholar_types:
                label = generate_cluster_label(sampled_entries, relevant_literature_texts, cluster_label, scholar)
                scholar_labels.append(f"{scholar} Scholar: {label}")

            labels_dict[cluster_label] = scholar_labels

            # Write the scholar labels to the output file
            output_file.write(f"Cluster {cluster_label} - Scholar Opinions:\n")
            for scholar_label in scholar_labels:
                output_file.write(f"{scholar_label}\n")
            output_file.write("\n")

    print("Cluster labels, descriptions, and unique examples have been generated and saved to 'cluster_labels_and_descriptions.txt'.")

if __name__ == "__main__":
    # Example usage
    generate_labels_for_all_clusters('event_data_with_assigned_clusters_v2_UPDATEDFORHALLUCINATIONS.xlsx', 'embeddingsLITERATURE.csv', 'embeddingsNEWS.csv', num_clusters=7, sample_size=5, top_n_literature=5)
