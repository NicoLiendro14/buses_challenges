import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
import json

sys.path.append(str(Path(__file__).parent.parent))

from scrapers.ross_scraper import RossScraper
from database.processor import DataProcessor
from database import db, create_tables
from database.models import Base

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ross_bus_scraping.log')
    ]
)
logger = logging.getLogger(__name__)

def print_listing_details(listing, index, total):
    """Imprime detalles formateados de un listado."""
    print(f"\n{'='*50}")
    print(f"PROCESANDO LISTADO {index}/{total}")
    print(f"{'='*50}")
    print(f"📝 Título: {listing.get('title', 'Sin título')}")
    print(f"🔑 VIN: {listing.get('vin', 'No disponible')}")
    print(f"🌐 URL: {listing.get('source_url', 'No disponible')}")
    print(f"🏭 Fabricante: {listing.get('make', 'No disponible')}")
    print(f"📅 Año: {listing.get('year', 'No disponible')}")
    print(f"💰 Precio: {listing.get('price', 'No disponible')}")
    print(f"{'='*50}")

def print_error_details(error, listing_index=None, listing_data=None):
    """Imprime detalles formateados de un error."""
    print(f"\n{'!'*50}")
    print("ERROR DETECTADO")
    print(f"{'!'*50}")
    print(f"📌 Tipo de error: {type(error).__name__}")
    print(f"📌 Mensaje de error: {str(error)}")
    if listing_index is not None:
        print(f"📌 Listado afectado: {listing_index}")
    if listing_data:
        print("\n📋 Datos del listado:")
        print(json.dumps(listing_data, indent=2, ensure_ascii=False))
    print(f"{'!'*50}")

def process_ross_bus_data():
    """Procesa y guarda los datos de buses de Ross Bus."""
    try:
        print("\n🚀 INICIANDO PROCESO DE SCRAPING")
        print("1️⃣ Inicializando base de datos...")
        logger.info("Inicializando base de datos...")
        
        print("2️⃣ Eliminando tablas existentes...")
        logger.info("Eliminando tablas existentes...")
        Base.metadata.drop_all(db.engine)
        
        print("3️⃣ Creando tablas con nuevos tamaños...")
        logger.info("Creando tablas con nuevos tamaños...")
        create_tables()
        
        print("4️⃣ Inicializando scraper y procesador...")
        logger.info("Inicializando scraper y procesador...")
        scraper = RossScraper()
        processor = DataProcessor()
        
        print("5️⃣ Obteniendo listados de buses...")
        logger.info("Obteniendo listados de buses...")
        listings = scraper.scrape()
        
        if not listings:
            print_error_details(Exception("No se encontraron listados de buses"))
            logger.error("No se encontraron listados de buses")
            sys.exit(1)
        
        print(f"6️⃣ Se encontraron {len(listings)} listados de buses")
        logger.info(f"Se encontraron {len(listings)} listados de buses")
        
        for i, listing in enumerate(listings, 1):
            try:
                print_listing_details(listing, i, len(listings))
                
                listing['scraped_at'] = datetime.now(timezone.utc)
                
                print("\n💾 Intentando guardar en la base de datos...")
                bus = processor.save_bus_data(listing)
                
                if bus:
                    print(f"✅ Bús guardado exitosamente:")
                    print(f"   - Título: {bus.title}")
                    print(f"   - VIN: {bus.vin}")
                    print(f"   - ID: {bus.id}")
                    logger.info(f"Bús guardado exitosamente: {bus.title} (VIN: {bus.vin})")
                else:
                    print(f"❌ No se pudo guardar el bús: {listing.get('title', 'Sin título')}")
                    logger.warning(f"No se pudo guardar el bús: {listing.get('title', 'Sin título')}")
                
            except Exception as e:
                print_error_details(e, i, listing)
                logger.error(f"Error procesando listado {i}: {str(e)}")
                sys.exit(1)
        
        print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("Proceso completado exitosamente")
        
    except Exception as e:
        print_error_details(e)
        logger.error(f"Error en el proceso principal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        process_ross_bus_data()
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
        logger.info("Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error_details(e)
        logger.error(f"Error fatal: {str(e)}")
        sys.exit(1) 