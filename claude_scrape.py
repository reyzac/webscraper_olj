import requests
from bs4 import BeautifulSoup
import time

# Create a session to maintain cookies
session = requests.Session()

def scrape_chr_content(url, delay=2):
    """
    Scrape content from a container with class="entry-content"
    
    Args:
        url: The URL of the webpage to scrape
        delay: Delay in seconds before making the request (default: 2)
    
    Returns:
        The text content from the entry-content container, or None if not found
    """
    try:
        # Add delay to avoid being blocked
        time.sleep(delay)
        
        # Send GET request with more realistic headers using session
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://novelbin.com/'
        }
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find container with class='entry-content'
        entry_content = soup.find(class_='entry-content')
        
        if entry_content:
            # Return the text content
            return entry_content.get_text(strip=True, separator='\n')
        else:
            print("No container with class='entry-content' found")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your target URL
    url = "https://novelbin.com/b/jackal-among-snakes/chapter-67-order-of-the-rose"
    
    content = scrape_chr_content(url)
    
    if content:
        print("Scraped content:")
        print(content)