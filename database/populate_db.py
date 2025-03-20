#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector
from database.processor import DataProcessor
from scrapers.daimler_scraper import DaimlerScraper
from scrapers.micro_bird_scraper import MicroBirdScraper
from scrapers.ross_scraper import RossScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_population.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def populate_database():
    try:
        db = DatabaseConnector()
        processor = DataProcessor()
        
        scrapers = [
            DaimlerScraper(),
            MicroBirdScraper(),
            RossScraper()
        ]
        
        total_buses = 0
        successful_buses = 0
        
        for scraper in scrapers:
            logger.info(f"Starting scraping process for {scraper.__class__.__name__}")
            
            try:
                buses_data = scraper.scrape()
                total_buses += len(buses_data)
                
                for bus_data in buses_data:
                    try:
                        bus_data['source'] = scraper.__class__.__name__.replace('Scraper', '')
                        bus_data['scraped'] = True
                        
                        bus = processor.save_bus_data(bus_data)
                        if bus:
                            successful_buses += 1
                            logger.info(f"Successfully saved bus with ID: {bus.id}")
                        else:
                            logger.error(f"Failed to save bus data: {bus_data.get('title', 'Unknown')}")
                    except Exception as e:
                        logger.error(f"Error processing bus data: {str(e)}")
                        continue
                
                logger.info(f"Completed processing for {scraper.__class__.__name__}")
                
            except Exception as e:
                logger.error(f"Error in scraper {scraper.__class__.__name__}: {str(e)}")
                continue
        
        logger.info(f"Database population completed:")
        logger.info(f"Total buses processed: {total_buses}")
        logger.info(f"Successfully saved: {successful_buses}")
        logger.info(f"Failed: {total_buses - successful_buses}")
        
        return successful_buses
        
    except Exception as e:
        logger.error(f"Error in populate_database: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    try:
        successful_buses = populate_database()
        sys.exit(0 if successful_buses > 0 else 1)
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1) 