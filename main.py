import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def parse_review_date(date_str):
    """Convert Google review date string to datetime object"""
    try:
        # Handle "X months ago" format
        if 'months ago' in date_str:
            months = int(date_str.split()[0])
            return datetime.now() - timedelta(days=months*30)
        
        # Handle "X weeks ago" format
        elif 'weeks ago' in date_str:
            weeks = int(date_str.split()[0])
            return datetime.now() - timedelta(weeks=weeks)
        
        # Handle "X days ago" format
        elif 'days ago' in date_str:
            days = int(date_str.split()[0])
            return datetime.now() - timedelta(days=days)
        
        # Handle "a month ago", "a week ago", "a day ago"
        elif date_str.startswith('a '):
            if 'month ago' in date_str:
                return datetime.now() - timedelta(days=30)
            elif 'week ago' in date_str:
                return datetime.now() - timedelta(weeks=1)
            elif 'day ago' in date_str:
                return datetime.now() - timedelta(days=1)
        
        # Handle specific date format
        else:
            return datetime.strptime(date_str, '%B %d, %Y')
    except Exception as e:
        logging.error(f"Error parsing date {date_str}: {str(e)}")
        return None

def is_date_in_range(review_date):
    """Check if the review date is between 10 months and 1 year old"""
    if not review_date:
        return False
        
    now = datetime.now()
    ten_months_ago = now - timedelta(days=300)  # approximately 10 months
    one_year_ago = now - timedelta(days=365)
    
    return one_year_ago <= review_date <= ten_months_ago

def setup_driver(chrome_binary_path, chromedriver_path):
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except TimeoutException:
        logging.warning(f"Timeout waiting for element: {selector}")
        return None

def load_reviews_page(driver):
    maps_url = f"https://www.google.com/maps/place/Ganga+Seva+Nidhi/@25.3067739,83.007694,17z/data=!4m8!3m7!1s0x398e31e1eeb5faed:0xe6e05d67d04cbf8e!8m2!3d25.3067739!4d83.0102689!9m1!1b1!16s%2Fg%2F11b6qf900s?entry=ttu&g_ep=EgoyMDI0MTAwMi4xIKXMDSoASAFQAw%3D%3D"
    driver.get(maps_url)
    time.sleep(5)

def scroll_reviews(driver, scroll_times=20):  # Increased scroll_times to ensure we get enough reviews
    try:
        reviews_div = wait_for_element(driver, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        
        if not reviews_div:
            logging.warning("Could not find reviews container")
            return
        
        for i in range(scroll_times):
            try:
                driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollHeight', 
                    reviews_div
                )
                time.sleep(2)
                logging.info(f"Completed scroll {i + 1}/{scroll_times}")
            except Exception as e:
                logging.error(f"Error during scroll {i + 1}: {str(e)}")
                continue
                
    except Exception as e:
        logging.error(f"Error in scroll_reviews: {str(e)}")

def extract_reviews(driver):
    reviews = []
    try:
        review_elements = wait_for_element(driver, 'div.jJc9Ad', timeout=10)
        if not review_elements:
            logging.error("No review elements found")
            return reviews

        review_containers = driver.find_elements(By.CLASS_NAME, 'jJc9Ad')
        
        for review in review_containers:
            try:
                # Extract date first to check if we should process this review
                date_text = review.find_element(By.CLASS_NAME, 'rsqaWe').text
                review_date = parse_review_date(date_text)
                
                # Only process reviews within our date range
                if not is_date_in_range(review_date):
                    continue
                
                # Extract other review data
                author = review.find_element(By.CLASS_NAME, 'd4r55').text
                rating_element = review.find_element(By.CLASS_NAME, 'kvMYJc')
                rating = rating_element.get_attribute('aria-label').split()[0]
                
                # Try to expand the review if possible
                try:
                    more_button = review.find_element(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
                    driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(0.5)
                except:
                    pass

                try:
                    content = review.find_element(By.CLASS_NAME, 'wiI7pd').text
                except:
                    content = ""

                reviews.append({
                    'Author': author,
                    'Rating': rating,
                    'Date': date_text,  # Store original date text
                    'Content': content
                })
                
                logging.info(f"Successfully extracted review by {author} from {date_text}")
                
            except Exception as e:
                logging.error(f"Error extracting individual review: {str(e)}")
                continue
        
    except Exception as e:
        logging.error(f"Error in extract_reviews: {str(e)}")
    
    return reviews

def save_to_csv(reviews, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=['Author', 'Rating', 'Date', 'Content'])
            writer.writeheader()
            writer.writerows(reviews)
        logging.info(f"Successfully saved {len(reviews)} reviews to {filename}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {str(e)}")

def main():
    chrome_binary_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chromedriver_path = "/usr/local/bin/chromedriver"
    
    try:
        driver = setup_driver(chrome_binary_path, chromedriver_path)
        load_reviews_page(driver)
        time.sleep(5)
        
        scroll_reviews(driver)
        reviews = extract_reviews(driver)
        
        if not reviews:
            logging.error("No reviews were extracted")
        else:
            save_to_csv(reviews, "google_reviews.csv")
            logging.info(f"Successfully extracted {len(reviews)} reviews between 10 months and 1 year old")
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()