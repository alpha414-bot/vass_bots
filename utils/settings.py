from dotenv import load_dotenv
import os
import json

# Load the .env file
load_dotenv()


class AppSettings:
    USE_PROXY: bool = os.getenv("USE_PROXY", "False").lower() in ("true", "1", "yes")
    PROXY_TYPE: str = str(os.getenv("PROXY_TYPE", "socks4"))

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str | int = os.getenv("DB_PORT", 3306)
    DB_DATABASE: str = os.getenv("DB_DATABASE", "database_name")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Allowed Hosts
    # ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", ["localhost", "*"])
    # Allowed Hosts
    try:
        # Attempt to load ALLOWED_HOSTS as a JSON array if set
        ALLOWED_HOSTS: list = json.loads(
            os.getenv("ALLOWED_HOSTS", '["localhost", "*"]')
        )
        if not isinstance(ALLOWED_HOSTS, list):
            raise ValueError("ALLOWED_HOSTS must be a list")
    except (json.JSONDecodeError, ValueError):
        # Fallback if not a valid JSON list, treating as a comma-separated string
        ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,*").split(",")
        # Strip whitespace from each item
        ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

    # Telegram Bot Setup
    CHAT_ID: str = os.getenv("CHAT_ID", "1715608783")
    USE_TG_BOT: bool = os.getenv("USE_TG_BOT", "True").lower() in ("true", "1", "yes")
    MAX_TELEGRAM_MESSAGE_LENGTH: int = int(
        os.getenv("MAX_TELEGRAM_MESSAGE_LENGTH", 1200)
    )

    # Captcha
    APIKEY_2CAPTCHA = os.getenv("APIKEY_2CAPTCHA", "1f900baf6f486e66db38ba2a8efe5f0d")
    # APIKEY_2CAPTCHA = os.getenv("APIKEY_2CAPTCHA", "d8521da8e2461799140efb0f94013233")
    FIND_RECAPTCHA_SCRIPT = """
        function findRecaptchaClients() {
            // Check if reCAPTCHA config is available
            console.log("called upon")
            if (typeof ___grecaptcha_cfg === 'undefined') return [];
            
            return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
                const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
                const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

                objects.forEach(([toplevelKey, toplevel]) => {
                    const found = Object.entries(toplevel).find(([_, value]) => (
                        value && typeof value === 'object' && 'sitekey' in value && 'size' in value
                    ));

                    // Base URI if we find a top-level element
                    if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel.tagName === 'DIV') {
                        data.pageurl = toplevel.baseURI;
                    }

                    if (found) {
                        const [sublevelKey, sublevel] = found;

                        data.sitekey = sublevel.sitekey;
                        const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
                        const callback = sublevel[callbackKey];

                        // Handle callback extraction
                        if (!callback) {
                            data.callback = null;
                            data.function = null;
                        } else {
                            data.function = callback;
                            const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
                            data.callback = `___grecaptcha_cfg.clients${keys}`;
                        }
                    }
                });
                console.log("Sending data", data)
                return data;
            });
        }
        // Expose function globally
        window.findRecaptchaClients = findRecaptchaClients;
        findRecaptchaClients();
    """

    class Config:
        env_file = ".env"


settings = AppSettings()

emblem = """
        ____      __       ________  __       __      ____
       /    \    |  |     |   ___   |  |     |  |    /    \ 
      /  /\  \   |  |     | ( ___ ) |  |_____|  |   /  /\  \ 
     /  /__\  \  |  |     |   _____ /   _____   |  /  /__\  \ 
    /  ______  \ |  |     |  |      |  |     |  | /  ______  \ 
   /  /      \  \|  |_____|  |      |  |     |  |/  /      \  \ 
  /__/        \__\________|__|      |__|     |__|__/        \__\ 

  EMAIL   ADDRESS:        [alphasoft2021@gmail.com]
  GITHUB  REPO:           [https://github.com/alpha414-bot]
"""
