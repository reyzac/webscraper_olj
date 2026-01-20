import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def scrape_job_link(job_link):
    """
    Scrape job description from the given job link
    """
    response_joblink = requests.get(job_link, headers=headers)
    if response_joblink.status_code == 200:
        soup2 = BeautifulSoup(response_joblink.content, 'html.parser')
        job_desc_element = soup2.find('p', id='job-description')
        if job_desc_element:
            job_desc = job_desc_element.get_text()
            job_desc = job_desc.strip() if job_desc else 'N/A'

        salary_element = soup2.find('h3', string='WAGE / SALARY')
        if salary_element:
            salary = salary_element.find_next('p').get_text()
            salary = salary.strip() if salary else 'N/A'

        hours_perweek_element = soup2.find('h3', string='HOURS PER WEEK')
        if hours_perweek_element:
            hours_perweek = hours_perweek_element.find_next('p').get_text()
            hours_perweek = hours_perweek.strip() if hours_perweek else 'N/A'

    return {
        'job_desc': job_desc,
        'salary': salary,
        'hours_perweek': hours_perweek
    }


keyword = input("Enter the keyword to search for: ")
# Base URL parameters
base_params = {
    'jobkeyword': keyword,
    'skill_tags': '',
    'partTime': 'on',
    'gig': 'on',
    'fullTime': 'on'
}

# Headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Create a list to store data from all pages
all_data = []

# Pagination: Start from page 1 (offset 0), then 30, 60, 90...
page = 1
offset = 0

while page <= 2:
    # Construct URL based on page number
    if page == 1:
        # First page has no offset in URL
        url = f"https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword={base_params['jobkeyword']}&skill_tags={base_params['skill_tags']}&gig={base_params['gig']}&partTime={base_params['partTime']}&fullTime={base_params['fullTime']}&isFromJobsearchForm=1"
    else:
        # Subsequent pages have offset and isFromJobsearchForm parameter
        url = f"https://www.onlinejobs.ph/jobseekers/jobsearch/{offset}?jobkeyword={base_params['jobkeyword']}&skill_tags={base_params['skill_tags']}&gig={base_params['gig']}&partTime={base_params['partTime']}&fullTime={base_params['fullTime']}&isFromJobsearchForm=1"
    
    print(f"Scraping page {page} (offset: {offset})...")
    
    # Make a GET request to the URL with headers
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all <div> elements with class "jobpost-cat-box"
        entry_content = soup.find_all('div', class_='jobpost-cat-box')
        
        # If no jobs found on this page, stop pagination
        if not entry_content:
            print(f"No more jobs found. Stopping at page {page}.")
            break
        
        print(f"Found {len(entry_content)} jobs on page {page}")
        
        # Extract data from each <div> element and save to list
        for div in entry_content:
            
            job_title_element = div.find('h4', class_='fs-16')
            job_posted_element = div.find('p', class_='fs-13')
            job_desc_element = div.find('div', class_='desc')
            
            # Get the full text which contains job title and job type separated by tab/whitespace
            job_title_full = job_title_element.get_text() if job_title_element else 'N/A'
            
            # Split on tab or multiple whitespaces to separate job title and job type
            job_parts = re.split(r'\s{2,}|\t', job_title_full.strip())
            
            # First part is job title, last part is job type
            job_title = job_parts[0] if job_parts else 'N/A'
            job_type = job_parts[-1] if len(job_parts) > 1 else 'N/A'
            
            # If job_type is same as job_title (only one part), set job_type to empty
            if job_type == job_title:
                job_type = 'N/A'
            
            job_posted_parts = re.split('Posted on', job_posted_element.get_text()) if job_posted_element else []
            job_posted_by = job_posted_parts[0] if job_posted_parts else 'N/A'
            job_posted_by = job_posted_by.strip() if job_posted_by else 'N/A'
            job_posted_on = job_posted_parts[1] if len(job_posted_parts) > 1 else 'N/A'
            job_posted_on = job_posted_on.strip() if job_posted_on else 'N/A'

            job_desc = job_desc_element.get_text() if job_desc_element else 'N/A'
            job_desc = job_desc.strip() if job_desc else 'N/A'

            # Extract job link safely
            job_link = 'N/A'
            if job_desc_element:
                link_tag = job_desc_element.find('a')
                if link_tag and link_tag.get('href'):
                    job_link = link_tag['href'].strip()
                    if job_link and not job_link.startswith('http'):
                        job_link = 'https://www.onlinejobs.ph' + job_link
            
            # Get job description from the link
            job_details = scrape_job_link(job_link)
            

            all_data.append({
                #'html_content': str(div),
                'job_title': job_title,
                'job_type': job_type,
                'job_posted_by': job_posted_by,
                'job_posted_on': job_posted_on,
                'job_desc': job_desc,
                'job_link': job_link,
                'salary': job_details['salary'],
                'hours_perweek': job_details['hours_perweek'],
                'job_desc_full': job_details['job_desc'],
            })
        
        # Move to next page
        page += 1
        offset += 30  # Each page shows 30 jobs
        
        # Small delay to be respectful to the server
        time.sleep(1)
        
    else:
        print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
        break

# Create a DataFrame from all collected data
if all_data:
    df = pd.DataFrame(all_data)
    
    # Display the dataframe summary
    print(f"\nTotal jobs scraped: {len(df)} from {page - 1} page(s)")
    print(df.head())
    
    # Save to CSV
    filename = f'scraped_content_{base_params["jobkeyword"]}.csv'
    df.to_csv(filename, index=False)
    print(f"\nData saved to scraped_content_{base_params["jobkeyword"]}.csv")
else:
    print("No data was collected.")