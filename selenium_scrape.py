from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_chr_content(url, delay=2):
    """
    Scrape content from a container with class="entry-content" using Selenium
    
    Args:
        url: The URL of the webpage to scrape
        delay: Delay in seconds after page load (default: 2)
    
    Returns:
        The text content from the entry-content container, or None if not found
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        # Initialize the Chrome driver with automatic driver management
        # This will download the correct version and ignore the one in PATH
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load and add delay
        time.sleep(delay)
        
        # Wait for the entry-content element to be present
        wait = WebDriverWait(driver, 10)
        entry_content = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "entry-content"))
        )
        
        # Get the text content
        content = entry_content.text
        
        if content:
            return content
        else:
            print("Entry-content found but no text extracted")
            return None
            
    except Exception as e:
        print(f"Error scraping the page: {e}")
        return None
        
    finally:
        # Always close the browser
        if driver:
            driver.quit()

# Example usage
if __name__ == "__main__":
    # Replace with your target URL
    url = "https://novelbin.com/b/jackal-among-snakes/chapter-67-order-of-the-rose"
    
    content = scrape_chr_content(url)
    
    if content:
        print("Scraped content:")
        print(content)
    else:
        print("Failed to scrape content")