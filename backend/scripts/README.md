# Rent-Search Scripts

This directory contains scripts for the Rent-Search project.

## Daily Property Scraping Script

The `scrape_daily.py` script is designed to be run as a daily cron job to scrape and save property data from the Rakumachi website.

### Features

- Scrapes property data from Rakumachi website
- Saves data to the configured database (SQLite or MySQL)
- Logs execution details to a daily log file
- Sends email notifications on errors
- Configurable retry count for scraping attempts

### Setup

1. Make the script executable:
   ```bash
   chmod +x scrape_daily.py
   ```

2. Configure email notifications:
   
   Set the following environment variables for email notifications:
   ```bash
   export EMAIL_SENDER="your-email@gmail.com"
   export EMAIL_PASSWORD="your-app-password"
   ```
   
   Note: For Gmail, you'll need to use an App Password rather than your regular password.
   
   Alternatively, edit the script to use your preferred email service.

3. Test the script manually:
   ```bash
   cd /path/to/rent-search/backend
   python scripts/scrape_daily.py
   ```

4. Set up the cron job to run daily:
   ```bash
   crontab -e
   ```
   
   Add the following line to run the script daily at 3:00 AM:
   ```
   0 3 * * * cd /path/to/rent-search/backend && /usr/bin/python scripts/scrape_daily.py
   ```
   
   Or with environment variables for email:
   ```
   0 3 * * * cd /path/to/rent-search/backend && EMAIL_SENDER="your-email@gmail.com" EMAIL_PASSWORD="your-app-password" /usr/bin/python scripts/scrape_daily.py
   ```

### Logs

Logs are stored in the `logs` directory with filenames in the format `scrape_daily_YYYYMMDD.log`.

### Troubleshooting

- If the script fails, check the log files in the `logs` directory.
- Ensure the database configuration in `app/config.py` is correct.
- Verify that the email configuration is correct if you're not receiving error notifications.
