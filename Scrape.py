import time
import datetime
import logging
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_all_articles(driver, load_more_selector, date_limit):
    while True:
        try:
            
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_selector))
            )
            load_more_button.click()
            logging.info("Clicked 'More News' button")
            time.sleep(2)  
  
            soup = BeautifulSoup(driver.page_source, "html.parser")
            last_article_date_str = soup.find_all("div", class_="typeAndTime___3oQRN")[-1].text.strip()
            last_article_date_part = " ".join(last_article_date_str.split()[:3])
            last_article_date = datetime.datetime.strptime(last_article_date_part, "%b %d, %Y")

            if last_article_date < date_limit:
                logging.info("Last article date is older than date limit, stopping load")
                break
        except Exception as e:
            logging.error(f"Error clicking 'More News' button or parsing date: {e}")
            break


def scrape_articles():
    url = "https://news.metal.com/list/industry/aluminium"
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
 
    service = Service(executable_path="C:\\Users\\Yukthamukhi\\webdrivers\\chromedriver.exe")  
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    logging.info("Navigated to URL")
    
    start_date = datetime.datetime.strptime("Jun 18, 2024", "%b %d, %Y")
    end_date = datetime.datetime.strptime("Aug 2, 2024", "%b %d, %Y")
   
    load_more_selector = ".footer___PvIjk"  
    load_all_articles(driver, load_more_selector, start_date)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    articles = []
    
    for item in soup.find_all("div", class_="newsItem___wZtKx"):
        title_tag = item.find("div", class_="title___1baLV")
        date_tag = item.find("div", class_="typeAndTime___3oQRN")
        summary_tag = item.find("div", class_="description___z7ktb descriptionspec___lj3uG")  
        
        if title_tag and date_tag:
            title = title_tag.text.strip()
            link = title_tag.parent["href"]
            date_str = date_tag.text.strip()
            
            date_part = " ".join(date_str.split()[:3])
            date = datetime.datetime.strptime(date_part, "%b %d, %Y") 
            
            if start_date <= date <= end_date:
                summary = summary_tag.text.strip() if summary_tag else "No summary available"
                articles.append({"title": title, "link": link, "date": date_str, "summary": summary})
    
    return articles


def save_articles_to_csv(articles, filename="articles.csv"):

    fieldnames = ["title", "link", "date", "summary"]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)
    logging.info(f"Articles saved to {filename}")


if __name__ == "__main__":
    try:
        articles = scrape_articles()
        for article in articles:
            logging.info(f"Title: {article['title']}")
            logging.info(f"Link: {article['link']}")
            logging.info(f"Date: {article['date']}")
            logging.info(f"Summary: {article['summary']}\n")
        
        save_articles_to_csv(articles)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
