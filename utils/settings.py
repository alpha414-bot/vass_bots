from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()


class AppSettings:
    USE_PROXY: bool = bool(os.getenv("USE_PROXY", True))
    PROXY_TYPE: str = str(os.getenv("PROXY_TYPE", "socks4"))

    WORKDIR = os.getenv("WORKDIR", "sessions/")

    # Email Configuration
    MAIL_HOST: str = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 465))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "gmail@gmail.com")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "password")
    MAIL_FROM_ADDRESS: str = os.getenv("MAIL_FROM_ADDRESS", "gmail@gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "APP_NAME")

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str | int = os.getenv("DB_PORT", 3306)
    DB_DATABASE: str = os.getenv("DB_DATABASE", "database_name")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Allowed Hosts
    ALLOWED_HOSTS: dict = os.getenv("ALLOWED_HOSTS", ["localhost", "*"])

    # Telegram Bot Setup
    CHAT_ID: str = os.getenv("CHAT_ID", "1715608783")
    USE_TG_BOT: bool = bool(os.getenv("USE_TG_BOT", False))
    BOT_TOKEN: str = os.getenv(
        "BOT_TOKEN", "7559961212:AAG2hRrH0BSAkGgdTYRpMm1Br2wNlYouNWY"
    )
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
