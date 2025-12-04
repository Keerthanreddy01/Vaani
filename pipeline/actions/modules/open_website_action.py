import webbrowser
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

WEBSITE_SHORTCUTS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "reddit": "https://www.reddit.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
}

def open_website(entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    url = entities.get('url', '')
    website = entities.get('website', '').lower()
    
    if not url and not website:
        url = entities.get('LOCATION', '')
    
    if website and not url:
        url = WEBSITE_SHORTCUTS.get(website)
    
    if not url:
        return {
            "status": "error",
            "message": "No URL or website specified",
            "data": {"available_shortcuts": list(WEBSITE_SHORTCUTS.keys())}
        }
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        webbrowser.open(url)
        logger.info(f"Opened website: {url}")
        
        return {
            "status": "success",
            "message": f"Opening {website or url}",
            "data": {"url": url}
        }
    
    except Exception as e:
        logger.error(f"Failed to open website {url}: {e}")
        return {
            "status": "error",
            "message": f"Failed to open website: {str(e)}",
            "data": {"url": url, "error": str(e)}
        }

def list_websites() -> list:
    return list(WEBSITE_SHORTCUTS.keys())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Available website shortcuts:", list_websites())
    
    result = open_website({"website": "google"}, {})
    print(f"Result: {result}")

