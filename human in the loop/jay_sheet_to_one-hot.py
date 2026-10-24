import pandas as pd
# Load the dataset
file_path = 'event_data_with_assigned_clusters_one-hotV3.xlsx'
data = pd.read_excel(file_path)

# List of categories to check
categories = [
    "Joint Data-Sharing Systems",
    "Cross-Border Basin Agreements",
    "Transboundary Water Quality Standards",
    "Coordinated Hydropower Operations",
    "Joint Water Allocation Models",
    "Collaborative River Basin Planning"
]

# Add new columns for main categories
for category in categories:
    data[category] = data['assigned_clusters'].apply(lambda x: 1 if category in str(x) else 0)

# Additional conditions for marking 1 in specific categories
data['Cross-Border Basin Agreements'] = data.apply(
    lambda row: 1 if "Shared Aquifer Management" in str(row['assigned_clusters']) else row['Cross-Border Basin Agreements'], axis=1
)

data['Joint Water Allocation Models'] = data.apply(
    lambda row: 1 if "Integrated Drought Risk Protocols" in str(row['assigned_clusters']) else row['Joint Water Allocation Models'], axis=1
)

data['Collaborative River Basin Planning'] = data.apply(
    lambda row: 1 if "Adaptive Flood Management" in str(row['assigned_clusters']) else row['Collaborative River Basin Planning'], axis=1
)

# Save the updated dataset to a new file
output_path = 'One_hot.csv'
data.to_csv(output_path, index=False)

print(f"New columns added and dataset saved to {output_path}")
