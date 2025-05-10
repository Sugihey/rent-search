from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from typing import List, Dict, Any, Optional
from app.scraper import scrape_rakumachi
from app.db import save_properties_from_rakumachi, Property, PriceHistory, Session, create_tables
from sqlalchemy import desc, func, cast, Date
from datetime import datetime, timedelta

app = FastAPI()

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
        
        query_result = session.query(
            cast(PriceHistory.scraped_at, Date).label('date'),
            func.avg(PriceHistory.price).label('avg_price'),
            func.min(PriceHistory.price).label('min_price'),
            func.max(PriceHistory.price).label('max_price'),
            func.count(PriceHistory.id).label('count')
        ).filter(
            PriceHistory.scraped_at >= start_date
        ).group_by(
            cast(PriceHistory.scraped_at, Date)
        ).order_by(
            cast(PriceHistory.scraped_at, Date)
        ).all()
        
        result = []
        for row in query_result:
            result.append({
                "date": row.date.isoformat(),
                "avg_price": float(row.avg_price) if row.avg_price else 0,
                "min_price": row.min_price if row.min_price else 0,
                "max_price": row.max_price if row.max_price else 0,
                "count": row.count
            })
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve price trends: {str(e)}")
    finally:
        session.close()
