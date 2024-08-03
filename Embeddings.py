import os
import csv
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']


def read_articles_from_csv(filename="cleaned_articles.csv"):
    articles = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            articles.append(row)
    return articles


def store_embeddings_in_csv(articles):
    rows = []
    for article in articles:
        title_embedding = generate_embedding(article['title'])
        summary_embedding = generate_embedding(article['summary'])
        article['title_embedding'] = title_embedding
        article['summary_embedding'] = summary_embedding
        rows.append(article)
    
    keys = articles[0].keys()
    with open("cleaned_articles_with_embeddings.csv", mode='w', newline='', encoding='utf-8') as file:
        dict_writer = csv.DictWriter(file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(rows)


if __name__ == "__main__":
    articles = read_articles_from_csv()
    store_embeddings_in_csv(articles)
