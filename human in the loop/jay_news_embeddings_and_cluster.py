import pandas as pd
import openai
import hdbscan
import umap
import numpy as np
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import time

# Load the Excel file
def load_data(file_path):
    event_data = pd.read_excel(file_path)
    print("First few rows of the dataset:")
    print(event_data.head())
    return event_data

# Generate embeddings using Azure OpenAI with rate limiting handling
def get_embeddings(text_list, embedding_deployment_name):
    embeddings = []
    max_retries = 5
    for text in text_list:
        retries = 0
        while retries < max_retries:
            try:
                response = openai.Embedding.create(
                    input=text,
                    engine=embedding_deployment_name
                )
                embedding = response['data'][0]['embedding']
                embeddings.append(embedding)
                break
            except openai.error.RateLimitError as e:
                retries += 1
                wait_time = int(e.headers.get("Retry-After", 13))
                print(f"Rate limit exceeded. Retrying after {wait_time} seconds.")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Failed to generate embedding for text: {text}. Error: {e}")
                exit()
        if retries == max_retries:
            print(f"Max retries exceeded for text: {text}. Exiting.")
            exit()
    print("Embeddings generated successfully.")
    return embeddings

def save_embeddings_to_csv(embeddings, file_path):
    # Convert the list of embeddings to a DataFrame
    df_embeddings = pd.DataFrame(embeddings)
    df_embeddings.to_csv(file_path, index=False)
    print(f"Embeddings saved to {file_path}")

# Use placeholder embeddings if no API key is provided
def get_placeholder_embeddings(text_list, dimensions=768):
    np.random.seed(42)
    return np.random.rand(len(text_list), dimensions).tolist()

# Perform K-Means clustering
def perform_clustering(embeddings_scaled, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(embeddings_scaled)

    # Return inertia for optimization
    return kmeans.inertia_, cluster_labels

# Reduce dimensionality for visualization using UMAP
def visualize_clusters(embeddings_scaled, cluster_labels, n_clusters):
    umap_reducer = umap.UMAP(n_neighbors=80, min_dist=0.1, n_components=2, random_state=42)
    umap_embeddings = umap_reducer.fit_transform(embeddings_scaled)

    df_umap = pd.DataFrame(umap_embeddings, columns=['x', 'y']).assign(cluster=cluster_labels.astype(str))

    fig = px.scatter(df_umap, x='x', y='y', color='cluster', title=f"Clusters with {n_clusters} Clusters")
    fig.show()

# Save the result to a new Excel file with cluster labels
def save_results(event_data, cluster_labels, output_file_path):
    event_data['cluster'] = cluster_labels
    event_data.to_excel(output_file_path, index=False)
    print(f"Files have been saved: {output_file_path}")

# Main function for one-time embedding and clustering
def main(file_path, n_clusters=7):
    event_data = load_data(file_path)

    # Azure OpenAI setup
    openai.api_type = "azure"
    openai.api_base = 'https://conflict.openai.azure.com'
    openai.api_version = "2022-12-01"
    openai.api_key = '02e96096dcb24ab3b53a63049aa52155'

    embedding_deployment_name = 'conflict'

    if openai.api_key:
        embeddings = get_embeddings(event_data['augment by llm'].tolist(), embedding_deployment_name)
    else:
        print("No Azure OpenAI API key provided. Generating random placeholder embeddings.")
        embeddings = get_placeholder_embeddings(event_data['augment by llm'].tolist())

    save_embeddings_to_csv(embeddings, 'embeddingsNEWS.csv')

    # Standardize embeddings
    scaler = StandardScaler()
    embeddings_scaled = scaler.fit_transform(embeddings)
    print("First few embeddings:", embeddings_scaled[:5])

    inertia, cluster_labels = perform_clustering(embeddings_scaled, n_clusters)
    visualize_clusters(embeddings_scaled, cluster_labels, n_clusters)
    #save_results(event_data, cluster_labels, 'event_data_with_clusters.xlsx')

if __name__ == "__main__":
    pass
    main('data.xlsx')
