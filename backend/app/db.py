"""
Database connection and ORM models for the application.
"""
import re
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, Float, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pymysql

from app.config import MYSQL_CONFIG, USE_SQLITE
from app.scraper import scrape_rakumachi

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if USE_SQLITE:
    os.makedirs(os.path.dirname(os.path.abspath(__file__)) + '/../data', exist_ok=True)
    db_path = os.path.dirname(os.path.abspath(__file__)) + '/../data/rent_search.db'
    CONNECTION_STRING = f"sqlite:///{db_path}"
    logger.info(f"Using SQLite database at {db_path}")
else:
    CONNECTION_STRING = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}?charset={MYSQL_CONFIG['charset']}"
    logger.info("Using MySQL database")

engine = create_engine(CONNECTION_STRING, echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Property(Base):
    """ORM model for properties table."""
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, unique=True, nullable=False)
    address = Column(String(255))
    pub_date = Column(Date)
    access = Column(String(255))
    structure = Column(String(100))
    land_area = Column(Integer)
    building_area = Column(Integer)
    build_at = Column(Date)
    floors = Column(Integer)
    detail_url = Column(Text)
    scraped_at = Column(Date, nullable=False, default=func.now())
    closed_at = Column(Date)
    
    price_histories = relationship("PriceHistory", back_populates="property", cascade="all, delete-orphan")

class PriceHistory(Base):
    """ORM model for price_history table."""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'))
    price = Column(Integer, nullable=False)
    gross = Column(Float(precision=3))
    scraped_at = Column(DateTime, nullable=False, default=func.now())
    
    property = relationship("Property", back_populates="price_histories")

def create_tables():
    """Create database tables if they don't exist."""
    Base.metadata.create_all(engine)
    logger.info("Database tables created or already exist.")

def extract_listing_id(detail_url: str) -> Optional[int]:
    """Extract listing ID from the detail URL."""
    try:
        match = re.search(r'id(\d+)', detail_url)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logger.error(f"Error extracting listing ID: {str(e)}")
        return None

def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object."""
    if not date_str:
        return None
    
    try:
        if re.match(r'\d{4}/\d{1,2}/\d{1,2}', date_str):
            return datetime.strptime(date_str, '%Y/%m/%d').date()
        
        match = re.match(r'(\d{4})年(\d{1,2})月', date_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            return date(year, month, 1)
        
        return None
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {str(e)}")
        return None

def extract_price(price_str: Optional[str]) -> Optional[int]:
    """Extract price in ten thousand yen from price string."""
    if not price_str:
        return None
    
    try:
        match = re.search(r'([0-9,]+)万円', price_str)
        if match:
            price_text = match.group(1).replace(',', '')
            return int(price_text)
        return None
    except Exception as e:
        logger.error(f"Error extracting price '{price_str}': {str(e)}")
        return None

def extract_gross(gross_str: Optional[str]) -> Optional[float]:
    """Extract gross yield percentage from gross string."""
    if not gross_str:
        return None
    
    try:
        match = re.search(r'([0-9.]+)%', gross_str)
        if match:
            return float(match.group(1))
        return None
    except Exception as e:
        logger.error(f"Error extracting gross yield '{gross_str}': {str(e)}")
        return None

def extract_floors(floors_str: Optional[str]) -> Optional[int]:
    """Extract number of floors from floors string."""
    if not floors_str:
        return None
    
    try:
        match = re.search(r'(\d+)階建', floors_str)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logger.error(f"Error extracting floors '{floors_str}': {str(e)}")
        return None

def extract_area(area_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract building and land area from area string.
    Returns a tuple of (building_area, land_area) in square meters.
    """
    if not area_str:
        return None, None
    
    try:
        building_area = None
        land_area = None
        
        building_match = re.search(r'建物([0-9.]+)㎡', area_str)
        if building_match:
            building_area = int(float(building_match.group(1)))
        
        land_match = re.search(r'土地\s*([0-9.]+)㎡', area_str)
        if land_match:
            land_area = int(float(land_match.group(1)))
        
        return building_area, land_area
    except Exception as e:
        logger.error(f"Error extracting area '{area_str}': {str(e)}")
        return None, None

def save_property_data(property_data: Dict[str, Any]) -> None:
    """Process and save property data to database."""
    session = Session()
    
    try:
        listing_id = extract_listing_id(property_data.get('detail_url'))
        if not listing_id:
            logger.warning(f"Could not extract listing ID from URL: {property_data.get('detail_url')}")
            return
        
        pub_date = parse_date(property_data.get('pub_date'))
        build_at = parse_date(property_data.get('build_at'))
        price = extract_price(property_data.get('price'))
        gross = extract_gross(property_data.get('gross'))
        floors = extract_floors(property_data.get('stories'))
        building_area, land_area = extract_area(property_data.get('square'))
        
        existing_property = session.query(Property).filter_by(listing_id=listing_id).first()
        
        if existing_property:
            existing_property.address = property_data.get('place')
            existing_property.access = property_data.get('access')
            existing_property.structure = property_data.get('structure')
            if pub_date:
                existing_property.pub_date = pub_date
            if build_at:
                existing_property.build_at = build_at
            if floors:
                existing_property.floors = floors
            if building_area:
                existing_property.building_area = building_area
            if land_area:
                existing_property.land_area = land_area
            
            latest_price = session.query(PriceHistory).filter_by(
                property_id=existing_property.id
            ).order_by(PriceHistory.scraped_at.desc()).first()
            
            price_changed = latest_price and (
                (price and price != latest_price.price) or 
                (gross and gross != latest_price.gross)
            )
            
            if price_changed or not latest_price:
                new_price_history = PriceHistory(
                    property_id=existing_property.id,
                    price=price if price is not None else 0,
                    gross=gross,
                    scraped_at=datetime.now()
                )
                session.add(new_price_history)
                
            logger.info(f"Updated existing property with listing ID: {listing_id}")
        else:
            new_property = Property(
                listing_id=listing_id,
                address=property_data.get('place'),
                pub_date=pub_date,
                access=property_data.get('access'),
                structure=property_data.get('structure'),
                land_area=land_area,
                building_area=building_area,
                build_at=build_at,
                floors=floors,
                detail_url=property_data.get('detail_url'),
                scraped_at=datetime.now()
            )
            session.add(new_property)
            session.flush()  # Flush to get the ID
            
            if price is not None:
                new_price_history = PriceHistory(
                    property_id=new_property.id,
                    price=price,
                    gross=gross,
                    scraped_at=datetime.now()
                )
                session.add(new_price_history)
            
            logger.info(f"Created new property with listing ID: {listing_id}")
        
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving property data: {str(e)}")
    finally:
        session.close()

def save_properties_from_rakumachi(url: str, max_retries: int = 5) -> int:
    """
    Scrape properties from Rakumachi and save them to the database.
    Returns the number of properties processed.
    """
    try:
        properties = scrape_rakumachi(url, max_retries=max_retries)
        
        count = 0
        for prop in properties:
            save_property_data(prop)
            count += 1
        
        logger.info(f"Processed {count} properties from Rakumachi")
        return count
    except Exception as e:
        logger.error(f"Error processing properties from Rakumachi: {str(e)}")
        return 0

def test_database():
    """Test database connection and operations."""
    try:
        create_tables()
        
        url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area%5B%5D=27102&area%5B%5D=27103&area%5B%5D=27104&area%5B%5D=27106&area%5B%5D=27107&area%5B%5D=27108&area%5B%5D=27109&area%5B%5D=27111&area%5B%5D=27113&area%5B%5D=27114&area%5B%5D=27115&area%5B%5D=27116&area%5B%5D=27117&area%5B%5D=27118&area%5B%5D=27119&area%5B%5D=27120&area%5B%5D=27121&area%5B%5D=27122&area%5B%5D=27123&area%5B%5D=27124&area%5B%5D=27125&area%5B%5D=27126&area%5B%5D=27127&area%5B%5D=27128&newly=&price_from=&price_to=500&gross_from=&gross_to=&dim%5B%5D=1004&year_from=&year_to=&b_area_from=&b_area_to=&houses_ge=&houses_le=&layout%5B%5D=5&layout%5B%5D=6&layout%5B%5D=7&layout%5B%5D=8&layout%5B%5D=9&layout%5B%5D=10&layout%5B%5D=11&layout%5B%5D=12&layout%5B%5D=13&layout%5B%5D=14&min=10&l_area_from=&l_area_to=&own=1&keyword="
        
        count = save_properties_from_rakumachi(url, max_retries=1)
        
        session = Session()
        properties_count = session.query(Property).count()
        price_history_count = session.query(PriceHistory).count()
        session.close()
        
        logger.info(f"Test completed. Properties: {properties_count}, Price histories: {price_history_count}")
        return True
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_database()
