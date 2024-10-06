# Google Reviews Scraper

A Python-based web scraper that automatically extracts Google Reviews within a specific date range (9 months to 1 year old),this can be changed according to user preference
. The script uses Selenium WebDriver to navigate through Google Maps reviews, extract relevant information, and save it to a CSV file.

## Features

- 🕒 Date range filtering (customizable, default 9-12 months)
- 📊 Exports data to CSV format
- 🔄 Automatic review expansion for full content
- 🚦 Built-in rate limiting and scroll management
- 📝 Comprehensive logging system
- ⚠️ Error handling and recovery mechanisms

## Prerequisites

- Python 3.6+
- Google Chrome Browser
- ChromeDriver (compatible with your Chrome version)

### Required Python Packages
```
selenium
pandas
beautifulsoup4
```

Install the required packages using:
```bash
pip install -r requirements.txt
```

## Setup

1. **ChromeDriver Installation**:
   - Download ChromeDriver from [official website](https://sites.google.com/chromium.org/driver/)
   - Ensure the version matches your Chrome browser
   - Place the executable in the specified path or update the path in the script

2. **Configuration**:
   Update the following paths in the script according to your system:
   ```python
   chrome_binary_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   chromedriver_path = "/usr/local/bin/chromedriver"
   ```

   For Windows users, typical paths might look like:
   ```python
   chrome_binary_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
   chromedriver_path = "C:\\path\\to\\chromedriver.exe"
   ```

## Usage

### Basic Usage

```python
from review_scraper import ReviewScraper

scraper = ReviewScraper(chrome_binary_path, chromedriver_path)
scraper.run(url="YOUR_GOOGLE_MAPS_URL", output_file="reviews.csv")
```

### Customizing Date Range

You can modify the date range by adjusting the `min_months` and `max_months` parameters in the `is_date_in_range` method:

```python
def is_date_in_range(self, review_date, min_months=9, max_months=12):
    """Check if the review date is within the specified range"""
    if not review_date:
        return False
        
    now = datetime.now()
    oldest_date = now - timedelta(days=max_months*30)
    newest_date = now - timedelta(days=min_months*30)
    
    return oldest_date <= review_date <= newest_date
```

## Output Format

The scraper generates a CSV file with the following columns:
- Author: Name of the reviewer
- Rating: Numerical rating (1-5)
- Date: Date of the review
- Content: Full review text

Example output:
```csv
Author,Rating,Date,Content
John Doe,4.5,3 months ago,Great experience with the service...
Jane Smith,5,10 months ago,Excellent customer support...
```

## Logging

The script includes comprehensive logging that captures:
- Information about the scraping progress
- Warnings about potential issues
- Error messages for debugging

Logs are printed to the console with timestamps:
```
2024-01-01 12:00:00 - INFO - Successfully extracted review by John Doe from 3 months ago
2024-01-01 12:00:01 - WARNING - Timeout waiting for element: button.w8nwRe.kyuRq
```

## Error Handling

The scraper includes robust error handling for common issues:
- Network timeouts
- Missing elements
- Invalid dates
- Scroll failures
- File saving errors

## Customization

### Modifying Scroll Behavior

Adjust the scroll behavior by modifying the `scroll_times` parameter:
```python
scraper.scroll_reviews(scroll_times=30)  # Increase for more reviews
```

### Changing Wait Times

Modify the wait times in `wait_for_element` method:
```python
def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=15):  # Increased timeout
```

## Limitations

- Requires stable internet connection
- Dependent on Google Maps HTML structure (may need updates if Google changes their layout)
- Rate limited by scroll timing to avoid detection
- May not capture all reviews if the business has a very large number of reviews

## Legal Considerations

- Ensure compliance with Google's Terms of Service
- Implement appropriate delays between requests
- Use for personal/educational purposes only
- Respect robots.txt and website policies

## Troubleshooting

Common issues and solutions:

1. **ChromeDriver Version Mismatch**:
   ```
   Solution: Download ChromeDriver version matching your Chrome browser
   ```

2. **Element Not Found Errors**:
   ```
   Solution: Increase timeout values or update element selectors
   ```

3. **Scroll Not Working**:
   ```
   Solution: Adjust scroll_times or add additional wait time between scrolls
   ```

## Contributing

Feel free to fork this repository and submit pull requests. Please ensure:
- Code follows the existing style
- New features include appropriate tests
- Documentation is updated accordingly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring their usage complies with Google's terms of service and applicable laws.
