import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.scraper import scrape_rakumachi

def main():
    """Test the scraper and print the results."""
    url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area%5B%5D=27102&area%5B%5D=27103&area%5B%5D=27104&area%5B%5D=27106&area%5B%5D=27107&area%5B%5D=27108&area%5B%5D=27109&area%5B%5D=27111&area%5B%5D=27113&area%5B%5D=27114&area%5B%5D=27115&area%5B%5D=27116&area%5B%5D=27117&area%5B%5D=27118&area%5B%5D=27119&area%5B%5D=27120&area%5B%5D=27121&area%5B%5D=27122&area%5B%5D=27123&area%5B%5D=27124&area%5B%5D=27125&area%5B%5D=27126&area%5B%5D=27127&area%5B%5D=27128&newly=&price_from=&price_to=500&gross_from=&gross_to=&dim%5B%5D=1004&year_from=&year_to=&b_area_from=&b_area_to=&houses_ge=&houses_le=&layout%5B%5D=5&layout%5B%5D=6&layout%5B%5D=7&layout%5B%5D=8&layout%5B%5D=9&layout%5B%5D=10&layout%5B%5D=11&layout%5B%5D=12&layout%5B%5D=13&layout%5B%5D=14&min=10&l_area_from=&l_area_to=&own=1&keyword="
    
    print(f"Scraping URL: {url}")
    properties = scrape_rakumachi(url)
    
    print(f"\nFound {len(properties)} properties")
    
    if properties:
        print("\nSample property:")
        print(json.dumps(properties[0], ensure_ascii=False, indent=2))
    
    output_file = "scraped_properties.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)
    
    print(f"\nAll properties saved to {output_file}")

if __name__ == "__main__":
    main()
