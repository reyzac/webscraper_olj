from flask import Flask, request, jsonify, send_file
import os
from io import BytesIO

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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Web Job Scraper</h1>
                <form method="POST" action="/scrape">
                    <label>Enter job keyword to search:</label>
                    <input type="text" name="keyword" placeholder="e.g., python, accounting, data analyst" required>
                    <button type="submit">Start Scraping</button>
                </form>
            </div>
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
    
    # Dictionary to track progress
    progress_data = {'jobs': [], 'total': 0}
    
    def progress_callback(job_title, status):
        """Callback to track scraping progress"""
        if status == 'fetching':
            progress_data['jobs'].append({'title': job_title, 'status': 'Fetching full job details...'})
        elif status == 'complete':
            if progress_data['jobs']:
                progress_data['jobs'][-1]['status'] = 'Complete ✓'
    
    # Call the scraper with progress callback
    result = run_scraper(keyword, progress_callback)
    progress_data['total'] = len(progress_data['jobs'])
    
    if result['success']:
        # Convert DataFrame to CSV in memory
        csv_buffer = BytesIO()
        result['df'].to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Generate HTML response with summary
        jobs_list_html = ''.join([
            f'<tr><td>{i+1}</td><td>{job["title"]}</td><td style="color: green;">{job["status"]}</td></tr>'
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
                        <div class="summary-text"><strong>Keyword:</strong> {keyword}</div>
                        <div class="summary-text"><strong>Total Jobs Found:</strong> {result['jobs_found']}</div>
                        <div class="summary-text"><strong>Jobs Processed:</strong> {progress_data['total']}</div>
                    </div>
                    
                    <h3>Job Titles & Status:</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Job Title</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {jobs_list_html}
                        </tbody>
                    </table>
                    
                    <div>
                        <form method="POST" style="display: inline;">
                            <input type="hidden" name="keyword" value="{keyword}">
                        </form>
                        <a href="/download" class="download-btn">📥 Download CSV</a>
                        <a href="/" class="back-btn">← Back to Search</a>
                    </div>
                </div>
            </body>
        </html>
        '''
        
        # Store the dataframe in session or memory for download
        app.csv_data = csv_buffer
        app.csv_filename = f'scraped_content_{keyword}.csv'
        
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

if __name__ == '__main__':
    port = os.environ.get('PORT', 8000)
    app.run(host='0.0.0.0', port=int(port), debug=False)
