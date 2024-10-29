import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

class TokenManager:
    def __init__(self, credentials_file='credentials.json', token_cache_file='tokens_cache.json', log_file='output.txt'):
        # File configuration and logging setup
        self.credentials_file = credentials_file
        self.token_cache_file = token_cache_file
        self.log_file = log_file

        # Initialize tokens file if it doesn't exist
        if not os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, 'w') as f:
                json.dump({}, f)

        # Logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
    
    # Method to load credentials from credentials.json
    def load_credentials(self):
        logging.info("Loading credentials from credentials.json...")
        with open(self.credentials_file, 'r') as file:
            return json.load(file)

    # Method to save updated credentials
    def save_credentials(self, credentials):
        logging.info("Saving updated credentials to credentials.json...")
        with open(self.credentials_file, 'w') as file:
            json.dump(credentials, file, indent=4)

    # Method to select the least used credential
    def select_least_used_credential(self, credentials):
        instagram_credentials = credentials['instagram_credentials']
        sorted_credentials = sorted(instagram_credentials, key=lambda x: (x['used_count'], x['last_used']))

        selected_credential = sorted_credentials[0]
        for credential in instagram_credentials:
            credential['last_used'] = False
        selected_credential['last_used'] = True
        selected_credential['used_count'] += 1

        logging.info(f"Selected credential: {selected_credential['username_session']}")
        self.save_credentials(credentials)
        return selected_credential['username_session'], selected_credential['password']

    # Method to check for valid tokens in the tokens_cache.json file
    def get_valid_tokens_from_file(self):
        """
        Checks if the tokens in tokens_cache.json are still valid (i.e., less than 36 hours old).
        If valid, returns the tokens, otherwise returns None.
        """
        if not os.path.exists(self.token_cache_file):
            logging.info("No token cache file found.")
            return None
        
        with open(self.token_cache_file, 'r') as f:
            tokens = json.load(f)
        
        if not tokens:
            logging.info("Token cache file is empty.")
            return None

        # Check the timestamp for validity
        token_timestamp = datetime.fromisoformat(tokens.get('timestamp', ''))
        current_time = datetime.now()
        if (current_time - token_timestamp) < timedelta(hours=36):
            logging.info(100*"#")
            logging.info("Valid tokens found in tokens_cache.json.")
            logging.info(100*"#")
            return tokens
        else:
            logging.info("Tokens in tokens_cache.json are expired.")
            return None

    # Method to extract tokens from cookies
    async def extract_tokens_from_cookies(self, context):
        cookies = await context.cookies()
        csrf_token, session_id, ds_user_id = None, None, None

        for cookie in cookies:
            if cookie['name'] == 'csrftoken':
                csrf_token = cookie['value']
            elif cookie['name'] == 'sessionid':
                session_id = cookie['value']
            elif cookie['name'] == 'ds_user_id':
                ds_user_id = cookie['value']

        timestamp = datetime.now().isoformat()
        tokens = {
            'csrf_token': csrf_token,
            'session_id': session_id,
            'ds_user_id': ds_user_id,
            'timestamp': timestamp
        }

        logging.info(f"Extracted tokens: {json.dumps(tokens, indent=4)}")
        return tokens  # We won't save the tokens until the ig-x-www-claim is obtained

    # Method to update tokens with ig-x-www-claim
    def update_tokens_with_claim(self, tokens, claim):
        """
        Updates the tokens_cache.json file with the ig-x-www-claim.
        """
        try:
            # Add ig-x-www-claim
            tokens['x_ig_www_claim'] = claim
            tokens['timestamp'] = datetime.now().isoformat()

            # Save updated tokens to file
            with open(self.token_cache_file, 'w') as f:
                json.dump(tokens, f, indent=4)

            logging.info(f"Updated tokens with x_ig_www_claim: {claim}")
        except Exception as e:
            logging.error(f"Error updating tokens with claim: {e}")

    # Method to extract the ig-x-www-claim from the HTML response
    async def extract_ig_www_claim(self, page):
        """
        Extract the ig-x-www-claim from the HTML and return it.
        """
        html_content = await page.content()
        logging.info("Extracting ig-x-www-claim from the page...")

        # Search for the claim in the HTML
        start_index = html_content.find('"claim":')
        if start_index != -1:
            start_index += len('"claim":"')
            end_index = html_content.find('"', start_index)
            claim = html_content[start_index:end_index]
            logging.info(f"ig-x-www-claim found: {claim}")
            return claim
        else:
            logging.error("ig-x-www-claim not found in the HTML.")
            return None

    # Main method to capture Instagram tokens and extract ig-x-www-claim
    async def capture_instagram_queries(self, username, password):
        # Check for valid tokens in tokens_cache.json first
        tokens = self.get_valid_tokens_from_file()
        if tokens:
            return tokens  # Return valid tokens if found

        async with async_playwright() as p:
            
            # Proxy configuration (commented out)
            # proxy = {
            #     "server": "http://gate.smartproxy.com:10001",
            #     "username": "user-spdauduoc2-asn-28403-os-android",
            #     "password": "0rPak+0Puoi5Qsfj6C"
            # }
            
            # logging.info("Launching browser with mobile proxy...")
            # browser = await p.chromium.launch(headless=True, proxy=proxy)
            
            logging.info("Launching browser without mobile proxy...")
            browser = await p.chromium.launch(headless=True)

            # Browser configuration
            context = await browser.new_context(
                viewport={"width": 800, "height": 1280},
                user_agent="Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-T720 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36",
                has_touch=True,
                extra_http_headers={
                    "sec-ch-ua": "\"Google Chrome\";v=\"91\", \" Not=A?Brand\";v=\"99\", \"Chromium\";v=\"91\"",
                    "sec-ch-ua-mobile": "?1",
                    "sec-ch-ua-platform": "\"Android\"",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.instagram.com/"
                }
            )

            page = await context.new_page()
            logging.info("Navigating to the login page...")
            await page.goto('https://www.instagram.com/', timeout=5000)

            # Login to Instagram
            logging.info(f"--- Logging in with user: {username} ---")
            await page.type('input[name="username"]', username, delay=100)
            await page.type('input[name="password"]', password, delay=100)
            await page.click('button[type="submit"]')

            await page.wait_for_timeout(7000)  # Wait for login to complete

            # Extract tokens without saving them yet
            tokens = await self.extract_tokens_from_cookies(context)

            # Navigate to the Instagram profile page
            logging.info("Navigating to Instagram profile page...")
            await page.goto('https://www.instagram.com/chincha_rabina/', timeout=5000)

            await page.wait_for_timeout(4000)  # Wait 4 seconds for content to load

            # Extract ig-x-www-claim
            claim = await self.extract_ig_www_claim(page)
            if claim:
                self.update_tokens_with_claim(tokens, claim)  # Save tokens only when we have the claim

            await context.close()

            return tokens

# Usage example
if __name__ == "__main__":
    token_manager = TokenManager()
    credentials = token_manager.load_credentials()
    username, password = token_manager.select_least_used_credential(credentials)

    # Execute token capture and ig-x-www-claim extraction
    asyncio.run(token_manager.capture_instagram_queries(username, password))
