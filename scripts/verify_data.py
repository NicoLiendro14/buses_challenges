import logging
from database import db, Bus, BusOverview, BusImage
from sqlalchemy import func

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_bus_details(bus):
    """Print detailed information about a bus."""
    logger.info("\n" + "="*50)
    logger.info(f"Bus ID: {bus.id}")
    logger.info(f"Title: {bus.title}")
    logger.info(f"VIN: {bus.vin}")
    logger.info(f"Year: {bus.year}")
    logger.info(f"Make: {bus.make}")
    logger.info(f"Model: {bus.model}")
    logger.info(f"Price: ${bus.price}")
    logger.info(f"Source: {bus.source}")
    logger.info(f"Created: {bus.created_at}")
    logger.info(f"Updated: {bus.updated_at}")
    
    if bus.overview:
        logger.info("\nOverview:")
        logger.info(f"Main Description: {bus.overview.mdesc[:100]}...")
        logger.info(f"Features: {bus.overview.features}")
        logger.info(f"Specs: {bus.overview.specs}")
    
    if bus.images:
        logger.info(f"\nImages ({len(bus.images)}):")
        for img in bus.images:
            logger.info(f"- {img.name}: {img.url}")
    
    logger.info("="*50)

def main():
    try:
        db.create_tables()
        
        total_buses = db.session.query(func.count(Bus.id)).scalar()
        logger.info(f"\nTotal buses in database: {total_buses}")
        
        source_counts = db.session.query(
            Bus.source, func.count(Bus.id)
        ).group_by(Bus.source).all()
        
        logger.info("\nBuses by source:")
        for source, count in source_counts:
            logger.info(f"{source}: {count}")
        
        make_counts = db.session.query(
            Bus.make, func.count(Bus.id)
        ).group_by(Bus.make).all()
        
        logger.info("\nBuses by make:")
        for make, count in make_counts:
            logger.info(f"{make}: {count}")
        
        year_counts = db.session.query(
            Bus.year, func.count(Bus.id)
        ).group_by(Bus.year).all()
        
        logger.info("\nBuses by year:")
        for year, count in year_counts:
            logger.info(f"{year}: {count}")
        
        logger.info("\nLatest 3 buses added:")
        latest_buses = db.session.query(Bus).order_by(Bus.created_at.desc()).limit(3).all()
        for bus in latest_buses:
            print_bus_details(bus)
        
        duplicate_vins = db.session.query(
            Bus.vin, func.count(Bus.vin)
        ).group_by(Bus.vin).having(func.count(Bus.vin) > 1).all()
        
        if duplicate_vins:
            logger.warning("\nPotential duplicate VINs found:")
            for vin, count in duplicate_vins:
                logger.warning(f"VIN {vin}: {count} occurrences")
        
        logger.info("\nData verification completed successfully")
        
    except Exception as e:
        logger.error(f"Error in verification process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 