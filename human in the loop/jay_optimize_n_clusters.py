import openai
import matplotlib.pyplot as plt
from jay_cluster_analysis_ZC import load_data, get_embeddings, get_placeholder_embeddings, perform_clustering
from sklearn.preprocessing import StandardScaler
import numpy as np

# Main optimization script
def optimize_n_clusters(file_path, n_clusters_range):
    event_data = load_data(file_path)

    embedding_deployment_name = 'conflict'

    if openai.api_key:
        embeddings = get_embeddings(event_data['augment by llm'].tolist(), embedding_deployment_name)
    else:
        embeddings = get_placeholder_embeddings(event_data['augment by llm'].tolist())

    # Standardize the embeddings
    scaler = StandardScaler()
    embeddings_scaled = scaler.fit_transform(embeddings)

    inertia_values = []

    # Iterate over different n_clusters
    for n_clusters in n_clusters_range:
        inertia, _ = perform_clustering(embeddings_scaled, n_clusters)
        inertia_values.append(inertia)
        print(f"Inertia for {n_clusters} clusters: {inertia}")

    # Calculate slopes (differences) between consecutive inertia values
    slopes = np.diff(inertia_values)  # Using numpy's diff function to calculate differences

    # Plot inertia vs number of clusters
    plt.figure(figsize=(10, 6))
    plt.plot(n_clusters_range, inertia_values, marker='o')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.title('Inertia vs Number of Clusters')
    plt.grid(True)

    # Plot slopes vs number of clusters (n_clusters_range[:-1] because diff reduces length by 1)
    plt.figure(figsize=(10, 6))
    plt.plot(n_clusters_range[:-1], slopes, marker='o', color='red')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Slope of Inertia')
    plt.title('Slope of Inertia vs Number of Clusters')
    plt.grid(True)

    # Save the graphs as images
    plt.savefig('inertia_and_slope_graphs.png')
    print("Graphs have been saved as 'inertia_and_slope_graphs.png'")

if __name__ == "__main__":
    optimize_n_clusters('data.xlsx', range(1, 25))
