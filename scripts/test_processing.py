import logging
from database.processor import DataProcessor
from scrapers.daimler_scraper import DaimlerScraper
from database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        processor = DataProcessor()
        scraper = DaimlerScraper()
        
        listings = scraper.get_listings()
        logger.info("Fetching listings from Daimler...")
        listings = scraper.get_listings()
        logger.info(f"Found {len(listings)} listings")

        for listing in listings:
            try:
                logger.info(f"Processing listing: {listing.get('title', 'Unknown')}")
                
                bus = processor.save_bus_data(listing)
                if bus:
                    logger.info(f"Successfully saved bus with VIN: {bus.vin}")
                else:
                    logger.warning("Failed to save bus data")
                    
            except Exception as e:
                logger.error(f"Error processing listing: {str(e)}")
                continue
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 