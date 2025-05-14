"""
Script to scrape and save properties from Rakumachi website.
Designed to be run as a daily cron job.
"""
import sys
import os
import logging
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import save_properties_from_rakumachi, create_tables
import app.config
app.config.USE_SQLITE = True

log_dir = Path(__file__).resolve().parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'scrape_daily_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

EMAIL_RECIPIENT = "sugihey@gmail.com"
EMAIL_SENDER = "your-email@gmail.com"  # Replace with actual sender email
EMAIL_PASSWORD = ""  # Set this via environment variable in production

def send_error_email(error_message):
    """
    Send an error notification email.
    
    Args:
        error_message: The error message to include in the email
    """
    try:
        sender = os.environ.get("EMAIL_SENDER", EMAIL_SENDER)
        password = os.environ.get("EMAIL_PASSWORD", EMAIL_PASSWORD)
        
        if not password:
            logger.error("Email password not configured. Set EMAIL_PASSWORD environment variable.")
            return
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = f"Error in Rent-Search Daily Scraping - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
        An error occurred during the daily property scraping:
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Error details:
        {error_message}
        
        Please check the logs at {log_file} for more information.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, EMAIL_RECIPIENT, text)
        server.quit()
        
        logger.info(f"Error notification email sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        logger.error(f"Failed to send error email: {str(e)}")

def main():
    """
    Main function to scrape and save properties.
    """
    start_time = datetime.now()
    logger.info(f"Starting daily property scraping at {start_time}")
    
    url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area%5B%5D=27102&area%5B%5D=27103&area%5B%5D=27104&area%5B%5D=27106&area%5B%5D=27107&area%5B%5D=27108&area%5B%5D=27109&area%5B%5D=27111&area%5B%5D=27113&area%5B%5D=27114&area%5B%5D=27115&area%5B%5D=27116&area%5B%5D=27117&area%5B%5D=27118&area%5B%5D=27119&area%5B%5D=27120&area%5B%5D=27121&area%5B%5D=27122&area%5B%5D=27123&area%5B%5D=27124&area%5B%5D=27125&area%5B%5D=27126&area%5B%5D=27127&area%5B%5D=27128&newly=&price_from=&price_to=500&gross_from=&gross_to=&dim%5B%5D=1004&year_from=&year_to=&b_area_from=&b_area_to=&houses_ge=&houses_le=&layout%5B%5D=5&layout%5B%5D=6&layout%5B%5D=7&layout%5B%5D=8&layout%5B%5D=9&layout%5B%5D=10&layout%5B%5D=11&layout%5B%5D=12&layout%5B%5D=13&layout%5B%5D=14&min=10&l_area_from=&l_area_to=&own=1&keyword="
    
    try:
        db_type = "SQLite" if app.config.USE_SQLITE else "MySQL"
        logger.info(f"Using {db_type} database")
        
        create_tables()
        logger.info("Database tables verified")
        
        count = save_properties_from_rakumachi(url, max_retries=5)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Completed daily property scraping at {end_time}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Properties processed: {count}")
        
        return 0  # Success
    except Exception as e:
        error_message = f"Error during property scraping: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        
        send_error_email(error_message)
        
        return 1  # Error

if __name__ == "__main__":
    sys.exit(main())
