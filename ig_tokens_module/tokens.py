import asyncio
import json
import logging
import os
from datetime import datetime
from playwright.async_api import async_playwright

class TokenManager:
    def __init__(self, credentials_file='credentials.json', token_cache_file='tokens_cache.json', log_file='output.txt'):
        # Configuración de archivos y logging
        self.credentials_file = credentials_file
        self.token_cache_file = token_cache_file
        self.log_file = log_file

        # Inicializar el archivo de tokens si no existe
        if not os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, 'w') as f:
                json.dump({}, f)

        # Configuración de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
    
    # Método para cargar credenciales
    def load_credentials(self):
        logging.info("Loading credentials from credentials.json...")
        with open(self.credentials_file, 'r') as file:
            return json.load(file)

    # Método para guardar credenciales actualizadas
    def save_credentials(self, credentials):
        logging.info("Saving updated credentials to credentials.json...")
        with open(self.credentials_file, 'w') as file:
            json.dump(credentials, file, indent=4)

    # Método para seleccionar la credencial menos usada
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

    # Método para extraer tokens desde cookies
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
        self.save_tokens(tokens)
        return tokens

    # Método para guardar tokens
    def save_tokens(self, tokens):
        with open(self.token_cache_file, 'w') as f:
            json.dump(tokens, f, indent=4)

    # Método principal para capturar tokens de Instagram
    async def capture_instagram_queries(self, username, password):
        async with async_playwright() as p:
            logging.info("Launching browser with mobile proxy...")
            browser = await p.chromium.launch(headless=True)

            # Configuración del navegador
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
            await page.goto('https://www.instagram.com/')

            # Inicio de sesión en Instagram
            logging.info(f"--- Logging in with user: {username} ---")
            await page.type('input[name="username"]', username, delay=100)
            await page.type('input[name="password"]', password, delay=100)
            await page.click('button[type="submit"]')

            await page.wait_for_timeout(7000)

            # Extraer tokens
            tokens = await self.extract_tokens_from_cookies(context)
            logging.info(f"Tokens extracted and saved to {self.token_cache_file}: {tokens}")

            await context.close()

            return tokens

# Ejemplo de uso
if __name__ == "__main__":
    token_manager = TokenManager()
    credentials = token_manager.load_credentials()
    username, password = token_manager.select_least_used_credential(credentials)

    # Ejecutar la captura de tokens
    asyncio.run(token_manager.capture_instagram_queries(username, password))
