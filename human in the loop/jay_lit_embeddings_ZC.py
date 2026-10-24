"""
import os
import openai
import numpy as np
import pandas as pd
import time
import tiktoken  # Import OpenAI tokenizer library

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"  # Should be KTH Azure OpenAI API address.
openai.api_version = "2023-03-15-preview"
openai.api_key = "KEY"  # Replace with your OpenAI API key

# Define the folder containing the text files
txt_folder = 'pdf_texts'  # Update this path to where the .txt files are stored

# Load the tokenizer for the model you're using
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")  # Or another appropriate tokenizer for your model

# Function to read text from a .txt file
def read_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text from file: {e}")
        return ""

# Function to chunk text based on token count to stay within the model's token limits
def chunk_text(text, max_tokens=8192):
    tokens = tokenizer.encode(text)  # Tokenize the text
    chunks = []

    # Split the tokens into chunks that are within the max_tokens limit
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunks.append(tokenizer.decode(chunk))  # Decode back to text for embedding
    print(f"Text has been chunked into {len(chunks)} parts.")
    return chunks

# Function to create embeddings for a list of texts using OpenAI API
def create_embeddings(texts, max_tokens=8192):
    embeddings = []
    for text in texts:
        # Chunk text if it exceeds the max token limit
        text_chunks = chunk_text(text, max_tokens=max_tokens)

        for chunk in text_chunks:
            retries = 0
            while retries < 5:  # Retry up to 5 times
                try:
                    response = openai.Embedding.create(input=chunk, engine="conflict")
                    embeddings.append(response['data'][0]['embedding'])
                    break
                except openai.error.RateLimitError as e:
                    wait_time = int(e.headers.get("Retry-After", 20))  # Use Retry-After header if available
                    print(f"Rate limit exceeded. Retrying after {wait_time} seconds.")
                    time.sleep(wait_time)
                    retries += 1
                except Exception as e:
                    print(f"Error generating embedding: {e}")
                    embeddings.append(None)
                    break
    return embeddings

# Read text from all .txt files
txt_files = [os.path.join(txt_folder, f) for f in os.listdir(txt_folder) if f.endswith('.txt')]
texts = [read_text_from_file(txt_file) for txt_file in txt_files]

print(f"Read {len(txt_files)} files.")

# Combine all texts into a single input
combined_text = "\n\n".join(texts)
print("Combined all text from PDFs.")

# Generate embeddings for all the text
print("Generating embeddings for each .txt file...")
embeddings = create_embeddings(texts)

# Filter out any None values from the embeddings list
clean_embeddings = [embed for embed in embeddings if embed is not None]

# Convert embeddings to a DataFrame and save to a CSV file
df_embeddings = pd.DataFrame(clean_embeddings)
output_embeddings_file = 'embeddings_per_txt_file.csv'
df_embeddings.to_csv(output_embeddings_file, index=False)
print(f"Embeddings have been saved to {output_embeddings_file}")


import os
import openai
import numpy as np
import pandas as pd
import time
import tiktoken

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "key"  # Replace with your OpenAI API key

# Define the folder containing the text files
txt_folder = 'pdf_texts'

# Load the tokenizer for the model you're using
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

# Function to read text from a .txt file
def read_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text from file: {e}")
        return ""

# Function to chunk text based on token count to stay within the model's token limits
def chunk_text(text, max_tokens=8192):
    tokens = tokenizer.encode(text)  # Tokenize the text
    chunks = []

    # Split the tokens into chunks that are within the max_tokens limit
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunks.append(tokenizer.decode(chunk))  # Decode back to text for embedding
    print(f"Text has been chunked into {len(chunks)} parts.")
    return chunks

# Function to create embeddings for a list of texts using OpenAI API
def create_embeddings(texts, max_tokens=8192):
    embeddings = []
    texts_with_embeddings = []  # To store original texts with embeddings

    for text in texts:
        # Chunk text if it exceeds the max token limit
        text_chunks = chunk_text(text, max_tokens=max_tokens)

        for chunk in text_chunks:
            retries = 0
            while retries < 5:  # Retry up to 5 times
                try:
                    response = openai.Embedding.create(input=chunk, engine="conflict")
                    embedding = response['data'][0]['embedding']
                    embeddings.append(embedding)
                    texts_with_embeddings.append({"text": chunk, "embedding": embedding})
                    break
                except openai.error.RateLimitError as e:
                    wait_time = int(e.headers.get("Retry-After", 20))  # Use Retry-After header if available
                    print(f"Rate limit exceeded. Retrying after {wait_time} seconds.")
                    time.sleep(wait_time)
                    retries += 1
                except Exception as e:
                    print(f"Error generating embedding: {e}")
                    embeddings.append(None)
                    texts_with_embeddings.append({"text": chunk, "embedding": None})
                    break
    return texts_with_embeddings

# Read text from all .txt files
txt_files = [os.path.join(txt_folder, f) for f in os.listdir(txt_folder) if f.endswith('.txt')]
texts = [read_text_from_file(txt_file) for txt_file in txt_files]

print(f"Read {len(txt_files)} files.")

# Generate embeddings for all the text
print("Generating embeddings for each .txt file...")
texts_with_embeddings = create_embeddings(texts)

# Create a DataFrame with both texts and embeddings
df_embeddings = pd.DataFrame(texts_with_embeddings)
output_embeddings_file = 'embeddings_with_text.csv'
df_embeddings.to_csv(output_embeddings_file, index=False)
print(f"Embeddings with original texts have been saved to {output_embeddings_file}")
"""

import os
import openai
import numpy as np
import pandas as pd
import time
import tiktoken

# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://conflict.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "02e96096dcb24ab3b53a63049aa52155"  # Replace with your OpenAI API key

# Define the folder containing the text files
txt_folder = 'pdf_texts'

# Load the tokenizer for the model you're using
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

# Function to read text from a .txt file
def read_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text from file: {e}")
        return ""

# Function to chunk text based on token count to stay within the model's token limits
def chunk_text(text, max_tokens=8192):
    tokens = tokenizer.encode(text)  # Tokenize the text
    chunks = []

    # Split the tokens into chunks that are within the max_tokens limit
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunks.append(tokenizer.decode(chunk))  # Decode back to text for embedding
    print(f"Text has been chunked into {len(chunks)} parts.")
    return chunks

# Function to create 3072-dimensional embeddings for a list of texts using OpenAI API
def create_3072_embeddings(texts, max_tokens=8192):
    embeddings_data = []  # To store original texts, chunk indices, and 3072-dimensional embeddings

    for text_index, text in enumerate(texts):
        # Chunk text if it exceeds the max token limit
        text_chunks = chunk_text(text, max_tokens=max_tokens)

        for chunk_index, chunk in enumerate(text_chunks):
            retries = 0
            while retries < 5:  # Retry up to 5 times
                try:
                    # Generate the first 1536-dimensional embedding
                    response1 = openai.Embedding.create(input=chunk, engine="conflict")
                    embedding1 = response1['data'][0]['embedding']

                    # Generate the second 1536-dimensional embedding
                    response2 = openai.Embedding.create(input=chunk, engine="conflict")
                    embedding2 = response2['data'][0]['embedding']

                    # Concatenate the two embeddings to create a 3072-dimensional embedding
                    combined_embedding = embedding1 + embedding2

                    # Store text, chunk index, and combined embedding
                    embeddings_data.append({
                        "text": chunk,
                        "chunk_index": chunk_index,
                        "embedding": combined_embedding
                    })
                    break
                except openai.error.RateLimitError as e:
                    wait_time = int(e.headers.get("Retry-After", 20))  # Use Retry-After header if available
                    print(f"Rate limit exceeded. Retrying after {wait_time} seconds.")
                    time.sleep(wait_time)
                    retries += 1
                except Exception as e:
                    print(f"Error generating embedding: {e}")
                    embeddings_data.append({
                        "text": chunk,
                        "chunk_index": chunk_index,
                        "embedding": None
                    })
                    break

    return embeddings_data

# Read text from all .txt files
txt_files = [os.path.join(txt_folder, f) for f in os.listdir(txt_folder) if f.endswith('.txt')]
texts = [read_text_from_file(txt_file) for txt_file in txt_files]

print(f"Read {len(txt_files)} files.")

# Generate 3072-dimensional embeddings for all the text
print("Generating 3072-dimensional embeddings for each .txt file...")
embeddings_data = create_3072_embeddings(texts)

# Create a DataFrame with text, chunk index, and flattened embeddings
flattened_data = []
for data in embeddings_data:
    if data['embedding'] is not None:
        embedding_length = len(data['embedding'])
        if embedding_length == 3072:
            flattened_embedding = data['embedding']
        else:
            print(f"Unexpected embedding length: {embedding_length}")
            flattened_embedding = data['embedding'][:3072]  # Trim if necessary

        flattened_data.append([data['text'], data['chunk_index']] + flattened_embedding)
    else:
        flattened_data.append([data['text'], data['chunk_index']] + [None] * 3072)

# Verify the shape of the flattened_data
print(f"Number of rows in flattened_data: {len(flattened_data)}")
print(f"Number of columns in a row of flattened_data: {len(flattened_data[0])}")

# Column names for the DataFrame
embedding_columns = [f"embedding_{i}" for i in range(3072)]  # Match 3072 embedding dimensions
columns = ["text", "chunk_index"] + embedding_columns

# Create the DataFrame
try:
    df_embeddings = pd.DataFrame(flattened_data, columns=columns)
    print(f"DataFrame created successfully with shape: {df_embeddings.shape}")
except ValueError as e:
    print(f"Error creating DataFrame: {e}")

# Save to CSV
output_embeddings_file = 'embeddingsLITERATURE.csv'
df_embeddings.to_csv(output_embeddings_file, index=False)
print(f"3072-dimensional embeddings with original texts have been saved to {output_embeddings_file}")
