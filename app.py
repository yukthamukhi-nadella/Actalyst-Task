import os
import streamlit as st
import pandas as pd
import openai
import numpy as np
import faiss
from sklearn.metrics.pairwise import cosine_similarity

# Set up OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Function to get embeddings from OpenAI
def get_embeddings(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

# Function to load data and create FAISS index
@st.cache_data
def load_data_and_create_index():
    df = pd.read_csv('cleaned_articles_with_embeddings.csv')
    df['title_embedding'] = df['title_embedding'].apply(eval).apply(np.array)
    df['summary_embedding'] = df['summary_embedding'].apply(eval).apply(np.array)

    # Create FAISS index
    dimension = len(df['title_embedding'].iloc[0])
    index = faiss.IndexFlatL2(dimension)

    # Add embeddings to the index
    embeddings = np.stack(df['title_embedding'].values)
    index.add(embeddings)

    return df, index

# Function to find the most relevant articles using FAISS
def find_relevant_articles(query, data, index, extracted_date=None, top_n=3):
    query_embedding = np.array(get_embeddings(query)).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_n)

    if extracted_date:
        filtered_data = data[data['date'] == extracted_date]
        indices = filtered_data.index[indices[0]]
    else:
        indices = indices[0]

    relevant_articles = data.iloc[indices]
    return relevant_articles

# Function to generate response using GPT-4
def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Streamlit App
def main():
    st.title("Article Chatbot")

    # Load data and create FAISS index
    data, index = load_data_and_create_index()

    # User query input
    query = st.text_input("Enter your query:")
    if st.button("Get Answer"):
        if query:
            # Extract date if mentioned in the query
            extracted_date = None
            for word in query.split():
                try:
                    extracted_date = pd.to_datetime(word).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue

            # Find relevant articles
            relevant_articles = find_relevant_articles(query, data, index, extracted_date)

            st.write("Top relevant articles:")
            for index, row in relevant_articles.iterrows():
                st.write(f"Title: {row['title']}")
                st.write(f"Summary: {row['summary']}")
                st.write(f"Link: {row['link']}")
                st.write(f"Date: {row['date']}")
                st.write("-----")
            
            # Create a prompt for GPT-4 using the most relevant article summaries
            summaries = "\n".join(relevant_articles['summary'].tolist())
            prompt = f"Based on the following summaries, provide a detailed response to the query: {query}\n\nSummaries:\n{summaries}"
            
            # Generate response using GPT-4
            response = generate_response(prompt)
            st.write("Chatbot response:")
            st.write(response)

if __name__ == "__main__":
    main()
