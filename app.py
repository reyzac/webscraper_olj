from flask import Flask, request, jsonify, send_file
import os
from io import BytesIO
import pandas as pd

try:
    from scrape import run_scraper
except ImportError as e:
    print(f"Warning: Could not import scraper module: {e}")
    run_scraper = None

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }
                h1 {
                    color: #333;
                    margin-bottom: 30px;
                }
                label {
                    display: block;
                    margin-bottom: 15px;
                    color: #555;
                    font-size: 16px;
                }
                input {
                    padding: 10px;
                    width: 300px;
                    font-size: 16px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin-bottom: 15px;
                }
                button {
                    padding: 10px 30px;
                    font-size: 16px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .advanced-toggle {
                    background-color: #6c757d;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-bottom: 15px;
                }
                .advanced-toggle:hover {
                    background-color: #5a6268;
                }
                .advanced-options {
                    display: none;
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    border: 1px solid #dee2e6;
                    text-align: left;
                }
                .advanced-options.show {
                    display: block;
                }
                .advanced-options label {
                    margin-bottom: 10px;
                    font-weight: bold;
                }
                .advanced-options input[type="file"] {
                    width: 100%;
                    padding: 10px;
                    border: 1px dashed #ccc;
                    border-radius: 4px;
                    background-color: white;
                }
                .file-info {
                    font-size: 12px;
                    color: #666;
                    margin-top: 8px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Web Job Scraper</h1>
                <form method="POST" action="/scrape" enctype="multipart/form-data">
                    <label>Enter job keyword(s) to search:</label>
                    <input type="text" name="keyword" placeholder="e.g., python, accounting, data analyst" required>
                    <small style="display: block; color: #666; margin-top: 5px; margin-bottom: 15px;">
                        Tip: Enter multiple keywords separated by commas to search simultaneously
                    </small>

                    <button type="button" class="advanced-toggle" onclick="toggleAdvanced()">Advanced Options</button>

                    <div id="advancedOptions" class="advanced-options">
                        <label>Master CSV File (Optional):</label>
                        <input type="file" name="master_csv" accept=".csv">
                        <p class="file-info">
                            Upload an existing masterlist CSV to skip already scraped jobs.<br>
                            New jobs will be appended to this file after scraping.
                        </p>
                    </div>

                    <button type="submit">Start Scraping</button>
                </form>
            </div>

            <script>
                function toggleAdvanced() {
                    var options = document.getElementById('advancedOptions');
                    options.classList.toggle('show');
                }
            </script>
        </body>
    </html>
    '''

@app.route('/scrape', methods=['POST', 'GET'])
def scrape():
    if run_scraper is None:
        return '''
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2>Error</h2>
                <p>Scraper module failed to load. Check dependencies.</p>
                <br>
                <a href="/">Go Back</a>
            </body>
        </html>
        ''', 500

    keyword = request.form.get('keyword') or request.args.get('keyword', 'python')

    # Handle master CSV file upload
    master_df = None
    master_csv_file = request.files.get('master_csv')
    if master_csv_file and master_csv_file.filename:
        try:
            master_df = pd.read_csv(master_csv_file)
        except Exception as e:
            print(f"Error reading master CSV: {e}")
            master_df = None

    # Dictionary to track progress
    progress_data = {'jobs': [], 'total': 0, 'keywords': [], 'skipped': 0}

    def progress_callback(job_title, status, keyword=None):
        """Callback to track scraping progress"""
        if status == 'fetching':
            keyword_label = f" [{keyword}]" if keyword else ""
            progress_data['jobs'].append({
                'title': job_title,
                'status': f'Fetching full job details...{keyword_label}',
                'keyword': keyword or ''
            })
        elif status == 'complete':
            if progress_data['jobs']:
                keyword_label = f" [{keyword}]" if keyword else ""
                progress_data['jobs'][-1]['status'] = f'Complete{keyword_label}'
        elif status == 'skipped':
            keyword_label = f" [{keyword}]" if keyword else ""
            progress_data['jobs'].append({
                'title': job_title,
                'status': f'Skipped (exists in master){keyword_label}',
                'keyword': keyword or ''
            })
            progress_data['skipped'] += 1

    # Call the scraper with progress callback and master_df
    result = run_scraper(keyword, progress_callback, master_df)
    progress_data['total'] = len(progress_data['jobs'])
    progress_data['keywords'] = result.get('keywords', [])
    
    if result['success']:
        # Convert DataFrame to CSV in memory
        csv_buffer = BytesIO()
        result['df'].to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Generate HTML response with summary
        jobs_list_html = ''.join([
            f'<tr><td>{i+1}</td><td>{job["title"]}</td><td>{job.get("keyword", "")}</td><td style="color: green;">{job["status"]}</td></tr>'
            for i, job in enumerate(progress_data['jobs'])
        ])
        
        html_response = f'''
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        padding: 30px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                        max-width: 900px;
                        margin: 0 auto;
                    }}
                    h2 {{
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .summary {{
                        background-color: #e8f5e9;
                        padding: 15px;
                        border-radius: 4px;
                        margin-bottom: 20px;
                        border-left: 4px solid #4caf50;
                    }}
                    .summary-text {{
                        font-size: 16px;
                        color: #2e7d32;
                        margin: 5px 0;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                    }}
                    th {{
                        background-color: #007bff;
                        color: white;
                        padding: 12px;
                        text-align: left;
                        border-bottom: 2px solid #0056b3;
                    }}
                    td {{
                        padding: 10px;
                        border-bottom: 1px solid #ddd;
                    }}
                    tr:hover {{
                        background-color: #f9f9f9;
                    }}
                    .download-btn {{
                        background-color: #28a745;
                        color: white;
                        padding: 12px 30px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                        text-decoration: none;
                        display: inline-block;
                        margin-right: 10px;
                    }}
                    .download-btn:hover {{
                        background-color: #218838;
                    }}
                    .back-btn {{
                        background-color: #6c757d;
                        color: white;
                        padding: 12px 30px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                        text-decoration: none;
                        display: inline-block;
                    }}
                    .back-btn:hover {{
                        background-color: #5a6268;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>✓ Scraping Complete!</h2>
                    
                    <div class="summary">
                        <div class="summary-text"><strong>Keyword(s):</strong> {', '.join(progress_data['keywords']) if progress_data['keywords'] else keyword}</div>
                        <div class="summary-text"><strong>Total Jobs Found:</strong> {result['jobs_found']}</div>
                        <div class="summary-text"><strong>Jobs Processed:</strong> {progress_data['total']}</div>
                        <div class="summary-text"><strong>Jobs Skipped (from master):</strong> {progress_data['skipped']}</div>
                        <div class="summary-text"><strong>New Jobs Scraped:</strong> {progress_data['total'] - progress_data['skipped']}</div>
                        {f'<div class="summary-text"><strong>Scraping Mode:</strong> {"Parallel (Multiple Keywords)" if len(progress_data["keywords"]) > 1 else "Single Keyword"}</div>' if progress_data['keywords'] else ''}
                    </div>
                    
                    <h3>Job Titles & Status:</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Job Title</th>
                                <th>Keyword</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {jobs_list_html}
                        </tbody>
                    </table>
                    
                    <div>
                        <a href="/download" class="download-btn">Download New Jobs CSV</a>
                        <a href="/download_master" class="download-btn" style="background-color: #17a2b8;">Download Updated Master CSV</a>
                        <a href="/" class="back-btn">Back to Search</a>
                    </div>
                </div>
            </body>
        </html>
        '''
        
        # Store the dataframe in session or memory for download
        app.csv_data = csv_buffer
        # Create filename from keywords
        keywords_str = '_'.join([k.replace(' ', '_') for k in progress_data['keywords']]) if progress_data['keywords'] else keyword.replace(' ', '_')
        app.csv_filename = f'scraped_content_{keywords_str}.csv'

        # Store the updated master CSV (includes both old and new jobs)
        if 'master_df' in result and result['master_df'] is not None:
            master_buffer = BytesIO()
            result['master_df'].to_csv(master_buffer, index=False)
            master_buffer.seek(0)
            app.master_csv_data = master_buffer
            app.master_csv_filename = f'master_jobs_{keywords_str}.csv'
        else:
            # If no master was provided, use the new data as the master
            app.master_csv_data = BytesIO()
            result['df'].to_csv(app.master_csv_data, index=False)
            app.master_csv_data.seek(0)
            app.master_csv_filename = f'master_jobs_{keywords_str}.csv'

        return html_response
    else:
        return f'''
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2>Scraping Failed</h2>
                <p>No jobs found for "{keyword}"</p>
                <br>
                <a href="/">Try Again</a>
            </body>
        </html>
        '''

@app.route('/download')
def download():
    """Download the CSV file"""
    if hasattr(app, 'csv_data') and app.csv_data:
        app.csv_data.seek(0)
        return send_file(
            app.csv_data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=app.csv_filename
        )
    return "No data available", 404

@app.route('/download_master')
def download_master():
    """Download the updated master CSV file"""
    if hasattr(app, 'master_csv_data') and app.master_csv_data:
        app.master_csv_data.seek(0)
        return send_file(
            app.master_csv_data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=app.master_csv_filename
        )
    return "No master data available", 404

if __name__ == '__main__':
    port = os.environ.get('PORT', 8000)
    app.run(host='0.0.0.0', port=int(port), debug=False)
