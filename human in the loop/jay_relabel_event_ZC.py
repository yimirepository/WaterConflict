import openai
import pandas as pd
import logging

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"  # Replace with your Azure OpenAI API base URL
openai.api_version = "2023-03-15-preview"
openai.api_key = ""

# Load the cluster labels and descriptions
cluster_labels_file_path = 'cluster_labels.txt'
with open(cluster_labels_file_path, 'r', encoding='utf-8') as file:
    cluster_labels_text = file.read()

# Load the Excel file with event data
file_path = 'event_data_with_assigned_clusters_v2_UPDATEDFORHALLUCINATIONS.xlsx'
event_data = pd.read_excel(file_path)

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to generate relevant cluster labels for each event using OpenAI API
def assign_cluster_labels_to_events(event_data, cluster_labels_text):
    for index, row in event_data.iterrows():
        event_description = row['event_text']

        messages = [
            {"role": "system", "content": "You're a Hydrology scholar with expertise in international water conflict and cooperation."},
            {"role": "user", "content": f"For the given event description, identify 2-5 relevant clusters from the list below that best match the themes and topics discussed in the event. In your output, list the cluster titles only, and do not change the wording at all. The clusters should be distinct and accurately reflect the core issues of the event.\n\nCLUSTER LABELS AND DESCRIPTIONS: {cluster_labels_text}\n\nEVENT DESCRIPTION:\n{event_description}\n\nRELEVANT CLUSTER LABELS (List 2-5):"}
        ]

        response = openai.ChatCompletion.create(
            engine="rag",  # Use the deployment name "rag" for your Azure OpenAI GPT-4 model
            messages=messages,
            temperature=0,
            max_tokens=512  # Adjusted max_tokens to allow for the cluster label generation
        )

        result = response['choices'][0]['message']['content']
        cluster_labels = result.split(', ')  # Assuming the response will be a comma-separated list of cluster labels

        # Assign the relevant clusters to the event
        event_data.at[index, 'assigned_clusters'] = ', '.join(cluster_labels[:5])  # Limiting to the first 5 clusters if more are provided

        # Print assigned clusters to the terminal
        print(f"Event {index + 1}: {event_data.at[index, 'assigned_clusters']}")
        logging.info(f"Assigned clusters to event {index}: {event_data.at[index, 'assigned_clusters']}")

# Assign cluster labels to events
assign_cluster_labels_to_events(event_data, cluster_labels_text)

# Save the cleaned data with new cluster labels
output_file_path_with_labels = 'event_data_with_assigned_clusters_one-hotV3.xlsx'
event_data.to_excel(output_file_path_with_labels, index=False)

logging.info("Files have been saved:")
logging.info(f" - Event Data with Assigned Clusters: {output_file_path_with_labels}")
