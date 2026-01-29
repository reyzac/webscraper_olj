# Web Job Scraper - OnlineJobs.ph

A Flask web application that scrapes job listings from OnlineJobs.ph and allows users to download results as CSV files. Built with Python and deployed on Google Cloud Run.

## Features

- 🌐 **Web Interface**: User-friendly Flask web app for searching jobs
- 🔍 **Job Listing Scraper**: Scrapes job postings from OnlineJobs.ph with customizable search keywords
- 📄 **Full Job Details**: Extracts job titles, descriptions, posting dates, and full job descriptions
- 📊 **CSV Export**: Download scraped data directly as CSV files
- 🔄 **Pagination Support**: Automatically handles multiple pages of job listings
- ⏱️ **Rate Limiting**: Includes delays between requests to be respectful to servers
- ☁️ **Cloud Deployed**: Runs on Google Cloud Run

## Project Structure

```
webscraper_olj/
├── app.py                 # Flask web application
├── scrape.py              # Job scraper logic for OnlineJobs.ph
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition for Cloud Run
├── DOCKER_GUIDE.md        # Beginner's guide to Docker and the Dockerfile
├── .dockerignore          # Files to exclude from Docker build
├── .gcloudignore          # Files to exclude from gcloud deployments
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Requirements

- Python 3.13+
- See `requirements.txt` for package dependencies
- Google Cloud Platform account (for cloud deployment)
- Docker (for local container testing)

## Installation & Setup

### Local Development

1. Clone this repository:
```bash
git clone https://github.com/reyzac/webscraper_olj.git
cd webscraper_olj
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask app locally:
```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Google Cloud Run Deployment

This app is configured for Google Cloud Run deployment using Docker containers.

> **New to Docker?** See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for a beginner-friendly explanation of how Docker and the Dockerfile work.

1. **Prerequisites**:
   - Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Authenticate: `gcloud auth login`
   - Set your project: `gcloud config set project YOUR_PROJECT_ID`

2. **Enable required APIs**:
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

3. **Build and deploy**:
```bash
# Build and push container using Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/webscraper-olj

# Deploy to Cloud Run
gcloud run deploy webscraper-olj \
  --image gcr.io/YOUR_PROJECT_ID/webscraper-olj \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 300s
```

4. **Local Docker testing** (optional):
```bash
docker build -t webscraper-olj .
docker run -p 8080:8080 webscraper-olj
# Visit http://localhost:8080
```

## Usage

### Web Interface

1. Navigate to the app URL (locally or on Cloud Run)
2. Enter a job keyword (e.g., "python", "data analyst", "finance")
3. Click "Start Scraping"
4. Download the CSV file with results

The app will scrape the first 2 pages of job listings (60 jobs) and provide additional details like salary and hours per week.

## Data Output

The scraper generates CSV files with the following columns:

- **job_title**: Title of the job position
- **job_type**: Type of employment (Full-time, Part-time, Gig)
- **job_posted_by**: Name of the employer/poster
- **job_posted_on**: Date when the job was posted
- **job_desc**: Short description from the listing page
- **job_link**: URL to the full job posting
- **salary**: Salary/wage information (if available)
- **hours_perweek**: Expected hours per week (if available)
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

- `flask`: Web framework
- `requests`: HTTP library for making web requests
- `beautifulsoup4`: HTML parsing library
- `pandas`: Data manipulation and CSV export
- `lxml`: XML/HTML parsing library
- `gunicorn`: Production WSGI server

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
