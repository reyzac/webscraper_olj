# Web Scraper for OnlineJobs.ph

A Python web scraping project that extracts job listings from OnlineJobs.ph and saves them to CSV format. The project includes multiple scraping approaches using `requests` and `BeautifulSoup`, as well as ~~Selenium for JavaScript-heavy pages~~.

## Features

- 🔍 **Job Listing Scraper**: Scrapes job postings from OnlineJobs.ph with customizable search keywords
- 📄 **Full Job Details**: Extracts job titles, descriptions, posting dates, and full job descriptions
- 📊 **CSV Export**: Automatically saves scraped data to CSV files for easy analysis
- 🔄 **Pagination Support**: Handles multiple pages of job listings automatically
- ⏱️ **Rate Limiting**: Includes delays between requests to be respectful to servers
- 🎯 **Multiple Scraping Methods**: ~~Includes both requests-based and Selenium-based scrapers~~ (N/A)

## Project Structure

```
webscraper_olj/
├── scrape.py              # Main job scraper for OnlineJobs.ph
├── claude_scrape.py        # Novel content scraper using requests
├── selenium_scrape.py      # Novel content scraper using Selenium
├── .gitignore             # Git ignore file (excludes CSV files)
└── README.md              # This file
```

## Requirements

- Python 3.7+
- See `requirements.txt` for package dependencies

## Installation

1. Clone this repository:
```bash
git clone https://github.com/reyzac/webscraper_olj.git
cd webscraper_olj
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. (Optional) For Selenium scraper, ensure you have Chrome browser installed. The `webdriver_manager` package will automatically download the appropriate ChromeDriver.

## Usage

### Main Job Scraper (`scrape.py`)

Scrapes job listings from OnlineJobs.ph based on search keywords.

```bash
python scrape.py
```

**Configuration:**
- Modify the `base_params` dictionary in `scrape.py` to change search criteria:
  - `jobkeyword`: Search keyword (default: 'finance')
  - `partTime`, `gig`, `fullTime`: Job type filters
- Adjust the `while page <= 2:` condition to scrape more or fewer pages

**Output:**
- Creates a CSV file named `scraped_content_{keyword}.csv`
- Contains columns: `html_content`, `job_title`, `job_type`, `job_posted_by`, `job_posted_on`, `job_desc`, `job_link`, `job_desc_full`

### Novel Content Scraper (`claude_scrape.py`)

Scrapes content from novel websites using requests library.

```bash
python claude_scrape.py
```

**Configuration:**
- Modify the `url` variable in the `if __name__ == "__main__"` block
- Adjust the `delay` parameter to change wait time between requests

### Selenium Scraper (`selenium_scrape.py`)

Scrapes JavaScript-rendered content using Selenium WebDriver.

```bash
python selenium_scrape.py
```

**Configuration:**
- Modify the `url` variable in the `if __name__ == "__main__"` block
- Runs in headless mode by default (no browser window)
- Automatically manages ChromeDriver installation

## Data Output

The main scraper (`scrape.py`) generates CSV files with the following columns:

- **html_content**: Raw HTML of the job posting
- **job_title**: Title of the job position
- **job_type**: Type of employment (Full-time, Part-time, Gig)
- **job_posted_by**: Name of the employer/poster
- **job_posted_on**: Date when the job was posted
- **job_desc**: Short description from the listing page
- **job_link**: URL to the full job posting
- **job_desc_full**: Complete job description from the detail page

## Important Notes

⚠️ **Web Scraping Ethics:**
- This scraper includes rate limiting (1-second delay between pages) to be respectful to the server
- Always check a website's `robots.txt` and Terms of Service before scraping
- Use scraped data responsibly and in accordance with the website's policies
- Consider reaching out to website owners for official APIs if available

⚠️ **Legal Considerations:**
- Web scraping may be subject to legal restrictions depending on your jurisdiction
- Ensure compliance with applicable laws and website terms of service
- This project is for educational purposes

## Dependencies

- `requests`: HTTP library for making web requests
- `beautifulsoup4`: HTML parsing library
- `pandas`: Data manipulation and CSV export
- `selenium`: Browser automation (for `selenium_scrape.py`)
- `webdriver-manager`: Automatic ChromeDriver management (for `selenium_scrape.py`)

## Troubleshooting

**Issue: "No module named 'X'"**
- Solution: Install missing packages with `pip install -r requirements.txt`

**Issue: Selenium scraper fails**
- Solution: Ensure Chrome browser is installed. The webdriver_manager will handle ChromeDriver automatically.

**Issue: Getting blocked or rate-limited**
- Solution: Increase the delay between requests in the code (modify `time.sleep()` values)

**Issue: No jobs found**
- Solution: Check your internet connection and verify the website structure hasn't changed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See the [LICENSE](LICENSE) file for details.

## Author

Created for educational and personal use.

---

**Disclaimer**: This tool is for educational purposes only. Always respect website terms of service and use responsibly.
