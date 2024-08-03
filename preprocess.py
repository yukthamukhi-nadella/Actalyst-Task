import pandas as pd
import datetime
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_date(date_str):
    try:
      
        cleaned_date = " ".join(date_str.split()[:3])
        return datetime.datetime.strptime(cleaned_date, "%b %d, %Y").strftime("%Y-%m-%d")
    except ValueError as e:
        logging.error(f"Date parsing error: {e}, date_str: {date_str}")
        return None


def preprocess_csv(input_file, output_file):
  
    df = pd.read_csv(input_file)

    df['date'] = df['date'].apply(clean_date)

    df = df.dropna(subset=['date'])

    df.to_csv(output_file, index=False)
    logging.info(f"Cleaned data saved to {output_file}")


if __name__ == "__main__":
    input_file = 'articles.csv'
    output_file = 'cleaned_articles.csv'
    preprocess_csv(input_file, output_file)
