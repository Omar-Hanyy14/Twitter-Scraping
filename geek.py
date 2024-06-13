from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
from datetime import datetime, timedelta

def twitter_login(driver, username, password):
    driver.get("https://twitter.com/login")
    try:
        print("Navigating to Twitter login page...")

        # Wait for the username input to be present and send username
        username_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(username)
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="LoginForm_Login_Button"]')))
        next_button.click()

        print("Entered username and clicked next...")

        # Wait for the password input to be present and send password
        password_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="LoginForm_Login_Button"]')))
        login_button.click()

        print("Entered password and clicked login...")

        # Wait for the home page to load by checking for the presence of the primary column
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="primaryColumn"]')))
        print("Logged in successfully")

    except Exception as e:
        print(f"Error during login: {str(e)}")

def fetch_recent_tweets(driver, username):
    url = f"https://twitter.com/{username}"
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    try:
        print(f"Fetching tweets for {username}...")
        # Wait for tweets to load
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]')))

        # Get all tweet elements
        tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

        # Filter recent tweets within the last 15 minutes
        recent_tweets = []
        now = datetime.utcnow()  # Use UTC to match Twitter's timestamp format
        time_threshold = now - timedelta(minutes=15)

        for tweet in tweet_elements:
            timestamp = tweet.find_element(By.XPATH, './/time').get_attribute('datetime')
            tweet_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            if tweet_time > time_threshold:
                tweet_text = tweet.text
                recent_tweets.append(tweet_text)

        return recent_tweets

    except Exception as e:
        print(f"Error fetching recent tweets for {username}: {str(e)}")
        return []

def count_mentions(tweets, ticker):
    ticker_pattern = re.compile(r'\b[$#]?' + re.escape(ticker.strip('$#')) + r'\b', re.IGNORECASE)
    mentions = sum(1 for text in tweets if re.search(ticker_pattern, text))
    return mentions

def main(usernames, ticker, interval, twitter_username, twitter_password):
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        twitter_login(driver, twitter_username, twitter_password)

        while True:
            total_mentions = 0
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Scraping started at {current_time}...")

            for username in usernames:
                print(f"Fetching recent tweets for {username}...")
                recent_tweets = fetch_recent_tweets(driver, username)
                mentions = count_mentions(recent_tweets, ticker)
                total_mentions += mentions
                print(f"'{ticker}' was mentioned '{mentions}' times for {username}.")

                for tweet in recent_tweets:
                    if re.search(r'\b[$#]?' + re.escape(ticker.strip('$#')) + r'\b', tweet, re.IGNORECASE):
                        print(f"Recent tweet containing '{ticker}': {tweet}")

            print(f"Total '{ticker}' mentions across all accounts: {total_mentions}")
            print(f"Waiting for {interval} minutes before next scrape...\n")

            time.sleep(interval * 60)  # Convert minutes to seconds

    except Exception as e:
        print(f"Error in main loop: {str(e)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    # List of Twitter accounts to scrape
    usernames = [
        "omar209720","WestMontanaaa","Mr_Derivatives", "warrior_0719", "ChartingProdigy",
        "allstarcharts", "yuriymatso", "TriggerTrades",
        "AdamMancini4", "CordovaTrades", "Barchart", "RoyLMattox"
    ]

    ticker = "$AAPL"  # Replace with the desired ticker symbol
    interval = 15  # Interval in minutes

    # Twitter login credentials
    twitter_username = "omar209720"  # Replace with your Twitter username
    twitter_password = "ahmedhesham12"  # Replace with your Twitter password

    main(usernames, ticker, interval, twitter_username, twitter_password)
