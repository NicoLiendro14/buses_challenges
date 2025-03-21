import sys
import logging
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from scrapers.micro_bird_scraper import MicroBirdScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    scraper = MicroBirdScraper()
    
    logger.info("Getting all bus categories...")
    categories = scraper.get_listings()
    logger.info(f"Found {len(categories)} categories:")
    for cat in categories:
        logger.info(f"- {cat['title']}: {cat['url']}")
    
    for category in categories:
        logger.info(f"\nProcessing category: {category['title']}")
        models = scraper.get_category_listings(category['url'])
        logger.info(f"Found {len(models)} models in this category")
        
        for model in models:
            logger.info(f"\nModel: {model['title']}")
            logger.info(f"URL: {model['url']}")
            logger.info(f"Capacity: {model['capacity']}")
            logger.info(f"Image URL: {model['image_url']}")
            
            details = scraper.parse_listing(model['url'])
            if details:
                logger.info("\nSpecifications:")
                for key, value in details['specifications'].items():
                    logger.info(f"- {key}: {value}")
            else:
                logger.warning("Could not parse model details")

if __name__ == "__main__":
    main() 