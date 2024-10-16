import asyncio
import json
import logging
import os
from datetime import datetime  # Import the datetime module
from playwright.async_api import async_playwright

# Check if the files exist, if not, create them
if not os.path.exists('tokens_cache.json'):
    with open('tokens_cache.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('output.txt'):
    open('output.txt', 'w').close()

# Logging configuration to send everything to a text file and to the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('output.txt'),  # Save logs to file
        logging.StreamHandler()  # Show logs in the console
    ]
)

# Load credentials from the JSON file
def load_credentials():
    logging.info("Loading credentials from credentials.json...")
    with open('credentials.json', 'r') as file:
        return json.load(file)

# Save updated credentials back to the JSON file
def save_credentials(credentials):
    logging.info("Saving updated credentials to credentials.json...")
    with open('credentials.json', 'w') as file:
        json.dump(credentials, file, indent=4)

# Select the least used credential that was not used last
def select_least_used_credential(credentials):
    instagram_credentials = credentials['instagram_credentials']
    sorted_credentials = sorted(instagram_credentials, key=lambda x: (x['used_count'], x['last_used']))

    selected_credential = sorted_credentials[0]

    for credential in instagram_credentials:
        credential['last_used'] = False
    
    selected_credential['last_used'] = True
    selected_credential['used_count'] += 1

    logging.info(f"Selected credential: {selected_credential['username_session']}")
    save_credentials(credentials)
    return selected_credential['username_session'], selected_credential['password']

# Extract csrf_token, session_id, and ds_user_id from the cookies
async def extract_tokens_from_cookies(context):
    cookies = await context.cookies()
    csrf_token = None
    session_id = None
    ds_user_id = None

    for cookie in cookies:
        if cookie['name'] == 'csrftoken':
            csrf_token = cookie['value']
        elif cookie['name'] == 'sessionid':
            session_id = cookie['value']
        elif cookie['name'] == 'ds_user_id':
            ds_user_id = cookie['value']
    
    # Get the current timestamp in ISO 8601 format
    timestamp = datetime.now().isoformat()

    tokens = {
        'csrf_token': csrf_token,
        'session_id': session_id,
        'ds_user_id': ds_user_id,
        'timestamp': timestamp  # Store the timestamp in ISO 8601 format
    }

    logging.info(f"Extracted tokens: {json.dumps(tokens, indent=4)}")

    # Save tokens to a JSON file
    with open('tokens_cache.json', 'w') as f:
        json.dump(tokens, f, indent=4)

    return tokens  # Return the tokens to Celery for storage

# Main function to capture Instagram queries
async def capture_instagram_queries(username, password):
    
    async with async_playwright() as p:
        # Launch browser with mobile proxy and simulate Android
        
        # Configuración del proxy móvil de SmartProxy
        proxy = {
            "server": "http://gate.smartproxy.com:10001",
            "username": "user-spdauduoc2-asn-28403-os-android",
            "password": "0rPak+0Puoi5Qsfj6C"
        }
        
        logging.info("Launching browser with mobile proxy...")
        browser = await p.chromium.launch(headless=True)
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

        # 1. Navigate to the Instagram login page
        logging.info("Navigating to the login page...")
        await page.goto('https://www.instagram.com/')

        # Log in to Instagram
        logging.info(f"--- Logging in with user: {username} ---")
        await page.type('input[name="username"]', username, delay=100)
        await page.type('input[name="password"]', password, delay=100)
        await page.click('button[type="submit"]')

        # Wait for login to complete
        await page.wait_for_timeout(10000)

        # Extract tokens (csrf_token, session_id, ds_user_id)
        tokens = await extract_tokens_from_cookies(context)
        logging.info(f"Tokens extracted and saved to tokens_cache.json: {tokens}")

        # Close browser
        logging.info("Closing browser...")
        await context.close()

        return tokens  # Return the tokens to the Celery task



# import asyncio
# import json
# import logging
# import os
# from playwright.async_api import async_playwright

# # Check if the files exist, if not, create them
# if not os.path.exists('tokens_cache.json'):
#     with open('tokens_cache.json', 'w') as f:
#         json.dump({}, f)

# if not os.path.exists('output.txt'):
#     open('output.txt', 'w').close()

# # Logging configuration to send everything to a text file and to the console
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(message)s',
#     handlers=[
#         logging.FileHandler('output.txt'),  # Save logs to file
#         logging.StreamHandler()  # Show logs in the console
#     ]
# )

# # Load credentials from the JSON file
# def load_credentials():
#     logging.info("Loading credentials from credentials.json...")
#     with open('credentials.json', 'r') as file:
#         return json.load(file)

# # Save updated credentials back to the JSON file
# def save_credentials(credentials):
#     logging.info("Saving updated credentials to credentials.json...")
#     with open('credentials.json', 'w') as file:
#         json.dump(credentials, file, indent=4)

# # Select the least used credential that was not used last
# def select_least_used_credential(credentials):
#     instagram_credentials = credentials['instagram_credentials']
#     sorted_credentials = sorted(instagram_credentials, key=lambda x: (x['used_count'], x['last_used']))

#     selected_credential = sorted_credentials[0]

#     for credential in instagram_credentials:
#         credential['last_used'] = False
    
#     selected_credential['last_used'] = True
#     selected_credential['used_count'] += 1

#     logging.info(f"Selected credential: {selected_credential['username_session']}")
#     save_credentials(credentials)
#     return selected_credential['username_session'], selected_credential['password']

# # Extract csrf_token, session_id, and ds_user_id from the cookies
# async def extract_tokens_from_cookies(context):
#     cookies = await context.cookies()
#     csrf_token = None
#     session_id = None
#     ds_user_id = None

#     for cookie in cookies:
#         if cookie['name'] == 'csrftoken':
#             csrf_token = cookie['value']
#         elif cookie['name'] == 'sessionid':
#             session_id = cookie['value']
#         elif cookie['name'] == 'ds_user_id':
#             ds_user_id = cookie['value']
    
#     tokens = {
#         'csrf_token': csrf_token,
#         'session_id': session_id,
#         'ds_user_id': ds_user_id,
#         'timestamp': str(asyncio.get_running_loop().time())  # Timestamp to verify extraction time
#     }

#     logging.info(f"Extracted tokens: {json.dumps(tokens, indent=4)}")

#     # Save tokens to a JSON file
#     with open('tokens_cache.json', 'w') as f:
#         json.dump(tokens, f, indent=4)

#     return tokens  # Return the tokens to Celery for storage

# # Main function to capture Instagram queries
# async def capture_instagram_queries(username, password):
    
#     async with async_playwright() as p:
#         # Launch browser with mobile proxy and simulate Android
        
#         # Configuración del proxy móvil de SmartProxy
#         proxy = {
#             "server": "http://gate.smartproxy.com:10001",
#             "username": "user-spdauduoc2-asn-28403-os-android",
#             "password": "0rPak+0Puoi5Qsfj6C"
#         }
        
#         logging.info("Launching browser with mobile proxy...")
#         browser = await p.chromium.launch(headless=True)
#         context = await browser.new_context(
#             viewport={"width": 800, "height": 1280},
#             user_agent="Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-T720 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36",
#             has_touch=True,
#             extra_http_headers={
#                 "sec-ch-ua": "\"Google Chrome\";v=\"91\", \" Not=A?Brand\";v=\"99\", \"Chromium\";v=\"91\"",
#                 "sec-ch-ua-mobile": "?1",
#                 "sec-ch-ua-platform": "\"Android\"",
#                 "Accept-Language": "en-US,en;q=0.9",
#                 "Accept-Encoding": "gzip, deflate, br",
#                 "Referer": "https://www.instagram.com/"
#             }
#         )

#         page = await context.new_page()

#         # 1. Navigate to the Instagram login page
#         logging.info("Navigating to the login page...")
#         await page.goto('https://www.instagram.com/')

#         # Log in to Instagram
#         logging.info(f"--- Logging in with user: {username} ---")
#         await page.type('input[name="username"]', username, delay=100)
#         await page.type('input[name="password"]', password, delay=100)
#         await page.click('button[type="submit"]')

#         # Wait for login to complete
#         await page.wait_for_timeout(7000)

#         # Extract tokens (csrf_token, session_id, ds_user_id)
#         tokens = await extract_tokens_from_cookies(context)
#         logging.info(f"Tokens extracted and saved to tokens_cache.json: {tokens}")

#         # Close browser
#         logging.info("Closing browser...")
#         await context.close()

#         return tokens  # Return the tokens to the Celery task
