from typing import List, Dict, Any, Optional
from datetime import datetime, UTC, timedelta
import logging
from . import db, Bus, BusOverview, BusImage

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_bus_data(self, data: Dict[str, Any]) -> Optional[Bus]:
        """Process raw bus data and create a Bus object."""
        try:
            print(f"\nProcessing bus data with VIN: {data.get('vin')}")
            
            bus_data = {
                'title': str(data.get('title', '')),
                'year': str(data.get('year', '')),
                'make': str(data.get('make', '')),
                'model': str(data.get('model', '')),
                'body': str(data.get('body', '')),
                'chassis': str(data.get('chassis', '')),
                'engine': str(data.get('engine', '')),
                'transmission': str(data.get('transmission', '')),
                'mileage': str(data.get('mileage', '')),
                'passengers': str(data.get('passengers', '')),
                'wheelchair': str(data.get('wheelchair', '')),
                'color': str(data.get('color', '')),
                'interior_color': str(data.get('interior_color', '')),
                'exterior_color': str(data.get('exterior_color', '')),
                'source': str(data.get('source', '')),
                'source_url': str(data.get('source_url', '')),
                'price': str(data.get('price', '')),
                'cprice': str(data.get('cprice', '')),
                'vin': str(data.get('vin', '')),
                'gvwr': str(data.get('gvwr', '')),
                'dimensions': str(data.get('dimensions', '')),
                'luggage': bool(data.get('luggage', False)),
                'state_bus_standard': str(data.get('state_bus_standard', '')),
                'airconditioning': data.get('airconditioning'),
                'location': str(data.get('location', '')),
                'brake': str(data.get('brake', '')),
                'contact_email': str(data.get('contact_email', '')),
                'contact_phone': str(data.get('contact_phone', '')),
                'us_region': data.get('us_region'),
                'description': str(data.get('description', '')),
                'scraped': True
            }
            
            bus = Bus(**bus_data)
            print(f"Created bus object with ID: {getattr(bus, 'id', None)}")
            return bus
        except Exception as e:
            self.logger.error(f"Error processing bus data: {str(e)}")
            print(f"Error in process_bus_data: {str(e)}")
            return None

    def process_overview_data(self, bus_id: int, data: Dict[str, Any]) -> Optional[BusOverview]:
        """Process overview data and create a BusOverview object."""
        try:
            print(f"\nProcessing overview data for bus_id: {bus_id}")
            
            overview_data = {
                'bus_id': bus_id,
                'mdesc': str(data.get('mdesc', '')),
                'intdesc': str(data.get('intdesc', '')),
                'extdesc': str(data.get('extdesc', '')),
                'features': str(data.get('features', '')),
                'specs': str(data.get('specs', ''))
            }
            
            overview = BusOverview(**overview_data)
            print(f"Created overview object with ID: {getattr(overview, 'id', None)}")
            return overview
        except Exception as e:
            self.logger.error(f"Error processing overview data: {str(e)}")
            print(f"Error in process_overview_data: {str(e)}")
            return None

    def process_image_data(self, bus_id: int, images: List[Dict[str, Any]]) -> List[BusImage]:
        """Process image data and create BusImage objects."""
        try:
            print(f"\nProcessing image data for bus_id: {bus_id}")
            image_objects = [
                BusImage(
                    bus_id=bus_id,
                    name=img.get('name', f'image_{i}'),
                    url=img.get('url'),
                    description=img.get('description'),
                    image_index=i
                )
                for i, img in enumerate(images)
            ]
            print(f"Created {len(image_objects)} image objects")
            return image_objects
        except Exception as e:
            self.logger.error(f"Error processing image data: {str(e)}")
            print(f"Error in process_image_data: {str(e)}")
            return []

    def save_bus_data(self, data: Dict[str, Any]) -> Optional[Bus]:
        """Save processed bus data to database."""
        print(f"\nStarting save_bus_data with VIN: {data.get('vin')}")
        session = db.session
        try:
            if data.get('vin'):
                print(f"Checking for existing bus with VIN: {data['vin']}")
                existing_bus = session.query(Bus).filter_by(vin=data['vin']).first()
                if existing_bus:
                    print(f"Found existing bus with ID: {existing_bus.id}")
                    print(f"Current updated_at: {existing_bus.updated_at}")
                    self.logger.info(f"Bus with VIN {data['vin']} already exists. Updating...")
                    for key, value in data.items():
                        if hasattr(existing_bus, key) and key not in ['id', 'created_at', 'updated_at', 'images', 'overview']:
                            print(f"Updating {key} from {getattr(existing_bus, key)} to {value}")
                            setattr(existing_bus, key, value)
                    
                    # Update timestamp with timezone-aware datetime
                    # Add 1 second to ensure the timestamp is different
                    new_timestamp = datetime.now(UTC) + timedelta(seconds=1)
                    print(f"Setting new updated_at to: {new_timestamp}")
                    existing_bus.updated_at = new_timestamp
                    bus = existing_bus
                else:
                    print("No existing bus found, creating new one")
                    bus = self.process_bus_data(data)
                    if bus:
                        print(f"Adding new bus to session with ID: {getattr(bus, 'id', None)}")
                        session.add(bus)
                        session.flush()
            else:
                print("No VIN provided, creating new bus")
                bus = self.process_bus_data(data)
                if bus:
                    print(f"Adding new bus to session with ID: {getattr(bus, 'id', None)}")
                    session.add(bus)
                    session.flush()

            if bus:
                print(f"Bus object created/updated with ID: {getattr(bus, 'id', None)}")
                print(f"Final updated_at value: {getattr(bus, 'updated_at', None)}")
                if any(key in data for key in ['mdesc', 'intdesc', 'extdesc', 'features', 'specs']):
                    print("Processing overview data")
                    existing_overview = session.query(BusOverview).filter_by(bus_id=bus.id).first()
                    if existing_overview:
                        print(f"Deleting existing overview with ID: {existing_overview.id}")
                        session.delete(existing_overview)
                    
                    overview = self.process_overview_data(bus.id, data)
                    if overview:
                        print(f"Adding new overview to session with ID: {getattr(overview, 'id', None)}")
                        session.add(overview)

                if data.get('images'):
                    print("Processing image data")
                    existing_images = session.query(BusImage).filter_by(bus_id=bus.id).all()
                    if existing_images:
                        print(f"Deleting {len(existing_images)} existing images")
                        for img in existing_images:
                            session.delete(img)
                    
                    images = self.process_image_data(bus.id, data['images'])
                    for image in images:
                        print(f"Adding image to session with ID: {getattr(image, 'id', None)}")
                        session.add(image)

                print("Committing session")
                session.commit()
                self.logger.info(f"Successfully saved bus data with ID: {bus.id}")
                print(f"Successfully saved bus with ID: {bus.id}")
                return bus

            print("No bus object created/updated")
            return None

        except Exception as e:
            self.logger.error(f"Error saving bus data: {str(e)}")
            print(f"Error in save_bus_data: {str(e)}")
            session.rollback()
            return None
        finally:
            print("Closing session")
            session.close()

    def save_multiple_buses(self, data_list: List[Dict[str, Any]]) -> List[Bus]:
        """Save multiple bus records to database."""
        print(f"\nStarting save_multiple_buses with {len(data_list)} buses")
        saved_buses = []
        for i, data in enumerate(data_list):
            print(f"\nProcessing bus {i+1}/{len(data_list)}")
            bus = self.save_bus_data(data)
            if bus:
                saved_buses.append(bus)
                print(f"Successfully saved bus {i+1} with ID: {bus.id}")
            else:
                print(f"Failed to save bus {i+1}")
        print(f"Completed save_multiple_buses. Successfully saved {len(saved_buses)} buses")
        return saved_buses 