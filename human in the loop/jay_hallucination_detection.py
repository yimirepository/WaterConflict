import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import openai
import time

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "02e96096dcb24ab3b53a63049aa52155"  # Replace with your Azure OpenAI API key
re_augmentation_engine = "rag"  # Azure deployment name for GPT-4 or GPT-3.5-turbo

# Load the CSV file
df = pd.read_csv('hallucination.csv')

# Filter out rows with 'NA' and separate out 'tbd' rows for prediction
df_train = df[df['Hallucination'].isin(['Y', 'N', 'maybe'])]  # Training data
df_predict = df[df['Hallucination'] == 'tbd']  # Rows to make predictions on

# Map Hallucination labels to binary classes for training
df_train['hallucination_label'] = df_train['Hallucination'].map({'N': 0, 'Y': 1, 'maybe': 1})

# Address class imbalance by upsampling hallucination entries ('Y' and 'maybe')
df_hallucinate = df_train[df_train['hallucination_label'] == 1]
df_no_hallucinate = df_train[df_train['hallucination_label'] == 0]
df_hallucinate_upsampled = df_hallucinate.sample(len(df_no_hallucinate), replace=True, random_state=42)
df_train_balanced = pd.concat([df_no_hallucinate, df_hallucinate_upsampled])

# Split the balanced training data into features and target
X_train = df_train_balanced['augmentbyllm']
y_train = df_train_balanced['hallucination_label']

# Convert the augmentbyllm text to TF-IDF features
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X_train_tfidf = vectorizer.fit_transform(X_train)

# Train a Random Forest classifier on the balanced dataset
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train_tfidf, y_train)

# Define a function for re-augmentation using Azure OpenAI
def re_augment(event_text, year, country1, country2):
    prompt = f"""
    You are a political scientist with expertise in historical data, particularly in water cooperation, conflict, environmental peacebuilding, and water diplomacy. Your task is to enrich the description of a provided Water Resources Collaborative event to help analyze aspects such as technical assistance, diplomatic measures, and stakeholder participation.

    Ensure all details are factual and grounded in the provided event description. Avoid adding unverified information or hallucinations.

    Year: {year}
    Event_text: '{event_text}'

    For each event, expand the description by focusing on:
    1. Forms of water cooperation
    2. Key actors and their roles
    3. Technical assistance
    4. Diplomatic measures
    5. Stakeholder participation

    Respond with an expanded, accurate description:
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant with expertise in historical and political science data."},
        {"role": "user", "content": prompt}
    ]

    retries = 0
    while retries < 5:
        try:
            response = openai.ChatCompletion.create(
                engine=re_augmentation_engine,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            wait_time = int(e.headers.get("Retry-After", 20))
            print(f"Rate limit exceeded. Retrying after {wait_time} seconds.")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            print(f"Error during re-augmentation: {e}")
            break
    return "Failed to re-augment"


# Define a function to run the iterative hallucination check
def iterative_hallucination_check(df_predict, clf, vectorizer):
    # Transform and predict initial probabilities
    X_predict_tfidf = vectorizer.transform(df_predict['augmentbyllm'])
    df_predict['hallucination_probability'] = clf.predict_proba(X_predict_tfidf)[:, 1]

    for index, row in df_predict[df_predict['hallucination_probability'] >= 0.2].iterrows():
        event_text = row['event_text']
        year = row['year']
        country1 = row['country1']
        country2 = row['country2']

        # Run re-augmentation until probability drops below 0.2
        probability = 1  # Initialize with a high value to enter the loop
        while probability >= 0.2:
            augmented_text = re_augment(event_text, year, country1, country2)

            # Check the new probability
            augmented_tfidf = vectorizer.transform([augmented_text])
            probability = clf.predict_proba(augmented_tfidf)[:, 1][0]

            # Update in DataFrame
            df_predict.at[index, 'augmentbyllm'] = augmented_text
            df_predict.at[index, 'hallucination_probability'] = probability

            print(f"Event at index {index} re-augmented with hallucination probability: {probability}")

# Run the iterative hallucination check on 'tbd' entries
iterative_hallucination_check(df_predict, clf, vectorizer)

# Save the final results
df_predict[['event_text', 'augmentbyllm', 'hallucination_probability']].to_csv('tbd_hallucination_predictions_final.csv', index=False)
print("Final predictions for 'tbd' rows saved to 'tbd_hallucination_predictions_final.csv'")
