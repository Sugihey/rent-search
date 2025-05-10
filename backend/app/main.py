from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from typing import List, Dict, Any, Optional
from app.scraper import scrape_rakumachi
from app.db import save_properties_from_rakumachi, Property, PriceHistory, Session, create_tables
from sqlalchemy import desc, func, cast, Date
from datetime import datetime, timedelta

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_tables()
    add_sample_data()

def add_sample_data():
    """Add sample data for testing if the database is empty."""
    session = Session()
    try:
        if session.query(Property).count() > 0:
            return
        
        # Create sample properties
        properties = []
        for i in range(1, 6):
            prop = Property(
                listing_id=1000 + i,
                address=f"Sample Address {i}",
                pub_date=datetime.now().date(),
                access=f"Sample Access {i}",
                structure="マンション",
                land_area=25,
                building_area=35,
                build_at=datetime(2010, 1, 1).date(),
                floors=5,
                detail_url=f"https://example.com/property/{1000 + i}",
                scraped_at=datetime.now().date()
            )
            session.add(prop)
            properties.append(prop)
        
        session.flush()
        
        dates = []
        current_date = datetime.now()
        for days_ago in range(365, 0, -7):  # Weekly data points for the last year
            dates.append(current_date - timedelta(days=days_ago))
        
        for prop in properties:
            base_price = 2000 + (prop.id * 100)  # Different base price for each property
            for i, date in enumerate(dates):
                price_variation = int((i % 5) * 50)
                price = base_price + price_variation
                
                gross = 5.0 + (i % 10) / 10
                
                price_history = PriceHistory(
                    property_id=prop.id,
                    price=price,
                    gross=gross,
                    scraped_at=date
                )
                session.add(price_history)
        
        session.commit()
        print(f"Added sample data: {len(properties)} properties with price history")
    except Exception as e:
        session.rollback()
        print(f"Error adding sample data: {str(e)}")
    finally:
        session.close()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/properties", response_model=List[Dict[str, Any]])
async def get_properties(max_retries: int = 1):
    """
    Scrape and return property information from Rakumachi website.
    
    The website may block scraping attempts with 403 Forbidden errors.
    In that case, mock data will be returned for testing purposes.
    
    Args:
        max_retries: Maximum number of retry attempts for scraping (default: 1)
                     Set to 0 to skip scraping and use mock data directly
    
    Returns:
        List of dictionaries containing property information
    """
    url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area%5B%5D=27102&area%5B%5D=27103&area%5B%5D=27104&area%5B%5D=27106&area%5B%5D=27107&area%5B%5D=27108&area%5B%5D=27109&area%5B%5D=27111&area%5B%5D=27113&area%5B%5D=27114&area%5B%5D=27115&area%5B%5D=27116&area%5B%5D=27117&area%5B%5D=27118&area%5B%5D=27119&area%5B%5D=27120&area%5B%5D=27121&area%5B%5D=27122&area%5B%5D=27123&area%5B%5D=27124&area%5B%5D=27125&area%5B%5D=27126&area%5B%5D=27127&area%5B%5D=27128&newly=&price_from=&price_to=500&gross_from=&gross_to=&dim%5B%5D=1004&year_from=&year_to=&b_area_from=&b_area_to=&houses_ge=&houses_le=&layout%5B%5D=5&layout%5B%5D=6&layout%5B%5D=7&layout%5B%5D=8&layout%5B%5D=9&layout%5B%5D=10&layout%5B%5D=11&layout%5B%5D=12&layout%5B%5D=13&layout%5B%5D=14&min=10&l_area_from=&l_area_to=&own=1&keyword="
    
    try:
        properties = scrape_rakumachi(url, max_retries=max_retries, retry_delay=3)
        return properties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape properties: {str(e)}")

@app.post("/api/scrape-and-save")
async def scrape_and_save_properties(max_retries: int = 1):
    """
    Scrape properties from Rakumachi and save them to the database.
    
    Args:
        max_retries: Maximum number of retry attempts for scraping (default: 1)
    
    Returns:
        Dictionary with count of processed properties
    """
    url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area%5B%5D=27102&area%5B%5D=27103&area%5B%5D=27104&area%5B%5D=27106&area%5B%5D=27107&area%5B%5D=27108&area%5B%5D=27109&area%5B%5D=27111&area%5B%5D=27113&area%5B%5D=27114&area%5B%5D=27115&area%5B%5D=27116&area%5B%5D=27117&area%5B%5D=27118&area%5B%5D=27119&area%5B%5D=27120&area%5B%5D=27121&area%5B%5D=27122&area%5B%5D=27123&area%5B%5D=27124&area%5B%5D=27125&area%5B%5D=27126&area%5B%5D=27127&area%5B%5D=27128&newly=&price_from=&price_to=500&gross_from=&gross_to=&dim%5B%5D=1004&year_from=&year_to=&b_area_from=&b_area_to=&houses_ge=&houses_le=&layout%5B%5D=5&layout%5B%5D=6&layout%5B%5D=7&layout%5B%5D=8&layout%5B%5D=9&layout%5B%5D=10&layout%5B%5D=11&layout%5B%5D=12&layout%5B%5D=13&layout%5B%5D=14&min=10&l_area_from=&l_area_to=&own=1&keyword="
    
    try:
        create_tables()
        
        count = save_properties_from_rakumachi(url, max_retries=max_retries)
        return {"success": True, "properties_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save properties: {str(e)}")

@app.get("/api/db-properties")
async def get_db_properties():
    """
    Get properties from the database.
    
    Returns:
        List of properties with their latest price history
    """
    session = Session()
    try:
        properties = session.query(Property).all()
        result = []
        
        for prop in properties:
            latest_price = session.query(PriceHistory).filter_by(
                property_id=prop.id
            ).order_by(desc(PriceHistory.scraped_at)).first()
            
            property_data = {
                "id": prop.id,
                "listing_id": prop.listing_id,
                "address": prop.address,
                "pub_date": prop.pub_date.isoformat() if prop.pub_date else None,
                "access": prop.access,
                "structure": prop.structure,
                "land_area": prop.land_area,
                "building_area": prop.building_area,
                "build_at": prop.build_at.isoformat() if prop.build_at else None,
                "floors": prop.floors,
                "detail_url": prop.detail_url,
                "scraped_at": prop.scraped_at.isoformat() if prop.scraped_at else None,
                "closed_at": prop.closed_at.isoformat() if prop.closed_at else None
            }
            
            if latest_price:
                property_data["price"] = latest_price.price
                property_data["gross"] = latest_price.gross
                property_data["price_updated_at"] = latest_price.scraped_at.isoformat()
            
            result.append(property_data)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve properties: {str(e)}")
    finally:
        session.close()

@app.get("/api/price-trends")
async def get_price_trends(days: Optional[int] = Query(30, description="Number of days to look back (7, 30, 180, 365)")):
    """
    Get price trends from the database.
    
    Aggregates price data from price_history table by date, calculating average, min, max prices and count.
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        List of dictionaries containing date and aggregated price data
    """
    session = Session()
    try:
        valid_days = [7, 30, 180, 365]
        if days not in valid_days:
            days = 30  # Default to 30 days if invalid
        
        start_date = datetime.now() - timedelta(days=days)
        
        price_history_data = session.query(
            PriceHistory
        ).filter(
            PriceHistory.scraped_at >= start_date
        ).all()
        
        date_groups = {}
        for item in price_history_data:
            date_key = item.scraped_at.date().isoformat()
            
            if date_key not in date_groups:
                date_groups[date_key] = {
                    'prices': [],
                    'date': date_key
                }
            
            date_groups[date_key]['prices'].append(item.price)
        
        result = []
        for date_key in sorted(date_groups.keys()):
            group = date_groups[date_key]
            prices = group['prices']
            
            result.append({
                'date': group['date'],
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
                'count': len(prices)
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve price trends: {str(e)}")
    finally:
        session.close()
