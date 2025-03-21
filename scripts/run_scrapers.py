#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.daimler_scraper import DaimlerScraper
from scrapers.micro_bird_scraper import MicroBirdScraper
from scrapers.ross_scraper import RossScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrapers_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_scrapers(output_dir='scraped_data'):
    """
    Run all scrapers and save their results as JSON files.
    
    Args:
        output_dir: Directory to save JSON output files
    
    Returns:
        dict: Statistics about the scraped data
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    scrapers = [
        DaimlerScraper(),
        MicroBirdScraper(),
        RossScraper()
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats = {
        "timestamp": timestamp,
        "scrapers": {}
    }
    
    for scraper in scrapers:
        scraper_name = scraper.__class__.__name__
        logger.info(f"Starting {scraper_name}")
        
        try:
            buses_data = scraper.scrape()
            
            for bus in buses_data:
                bus['source'] = scraper_name.replace('Scraper', '')
            
            output_file = f"{output_dir}/{scraper_name.lower()}_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(buses_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ {scraper_name} completed: {len(buses_data)} buses saved to {output_file}")
            
            stats["scrapers"][scraper_name] = {
                "count": len(buses_data),
                "output_file": output_file,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"✗ Error in {scraper_name}: {str(e)}")
            stats["scrapers"][scraper_name] = {
                "count": 0,
                "status": "error",
                "error": str(e)
            }
    
    stats_file = f"{output_dir}/scraping_stats_{timestamp}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    logger.info("\n--- Scraping Summary ---")
    for scraper_name, scraper_stats in stats["scrapers"].items():
        status = "✓" if scraper_stats["status"] == "success" else "✗"
        logger.info(f"{status} {scraper_name}: {scraper_stats['count']} buses")
    
    return stats

if __name__ == "__main__":
    run_scrapers()
    logger.info("To populate the database with this data, run: python database/populate_db.py") 