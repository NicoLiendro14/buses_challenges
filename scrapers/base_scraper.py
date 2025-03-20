from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
from random import uniform
from urllib.parse import urljoin

from database import Bus, BusOverview, BusImage, AirConditioningType, USRegion

class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)

    @abstractmethod
    def get_listing_urls(self) -> List[str]:
        """Get all listing URLs from the main page."""
        pass

    @abstractmethod
    def parse_listing(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single listing page and return structured data."""
        pass

    def get_page(self, url: str, retries: int = 3, delay: float = 1.0) -> Optional[BeautifulSoup]:
        """Get a page with retry logic and random delays."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(uniform(delay, delay * 2))
                return BeautifulSoup(response.text, 'html.parser')
            except requests.RequestException as e:
                self.logger.error(f"Attempt {attempt + 1}/{retries} failed for {url}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(uniform(delay * 2, delay * 4))
                continue
        return None

    def extract_text(self, element: Any, selector: str) -> Optional[str]:
        """Safely extract text from an element using a selector."""
        if element is None:
            return None
        found = element.select_one(selector)
        return found.text.strip() if found else None

    def extract_attribute(self, element: Any, selector: str, attribute: str) -> Optional[str]:
        """Safely extract an attribute from an element using a selector."""
        if element is None:
            return None
        found = element.select_one(selector)
        return found.get(attribute) if found else None

    def extract_list(self, element: Any, selector: str) -> List[str]:
        """Extract a list of text from elements matching a selector."""
        if element is None:
            return []
        elements = element.select(selector)
        return [el.text.strip() for el in elements if el.text.strip()]

    def normalize_price(self, price_str: str) -> Optional[str]:
        """Normalize price string to a standard format."""
        if not price_str:
            return None
        try:
            # Remove currency symbols, commas, and whitespace
            price = ''.join(c for c in price_str if c.isdigit() or c == '.')
            return f"${float(price):,.2f}"
        except (ValueError, TypeError):
            return None

    def normalize_mileage(self, mileage_str: str) -> Optional[str]:
        """Normalize mileage string to a standard format."""
        if not mileage_str:
            return None
        try:
            # Extract only numbers
            mileage = ''.join(c for c in mileage_str if c.isdigit())
            return f"{int(mileage):,}"
        except (ValueError, TypeError):
            return None

    def create_bus_object(self, data: Dict[str, Any]) -> Bus:
        """Create a Bus object from scraped data."""
        return Bus(
            title=data.get('title'),
            year=data.get('year'),
            make=data.get('make'),
            model=data.get('model'),
            body=data.get('body'),
            chassis=data.get('chassis'),
            engine=data.get('engine'),
            transmission=data.get('transmission'),
            mileage=self.normalize_mileage(data.get('mileage')),
            passengers=data.get('passengers'),
            wheelchair=data.get('wheelchair'),
            color=data.get('color'),
            interior_color=data.get('interior_color'),
            exterior_color=data.get('exterior_color'),
            source=data.get('source'),
            source_url=data.get('source_url'),
            price=self.normalize_price(data.get('price')),
            cprice=self.normalize_price(data.get('cprice')),
            vin=data.get('vin'),
            gvwr=data.get('gvwr'),
            dimensions=data.get('dimensions'),
            luggage=data.get('luggage', False),
            state_bus_standard=data.get('state_bus_standard'),
            airconditioning=data.get('airconditioning', AirConditioningType.OTHER),
            location=data.get('location'),
            brake=data.get('brake'),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone'),
            us_region=data.get('us_region', USRegion.OTHER),
            description=data.get('description'),
            scraped=True
        )

    def create_overview_object(self, bus_id: int, data: Dict[str, Any]) -> BusOverview:
        """Create a BusOverview object from scraped data."""
        return BusOverview(
            bus_id=bus_id,
            mdesc=data.get('mdesc'),
            intdesc=data.get('intdesc'),
            extdesc=data.get('extdesc'),
            features=data.get('features'),
            specs=data.get('specs')
        )

    def create_image_objects(self, bus_id: int, images: List[Dict[str, Any]]) -> List[BusImage]:
        """Create BusImage objects from scraped data."""
        return [
            BusImage(
                bus_id=bus_id,
                name=img.get('name', f'image_{i}'),
                url=img.get('url'),
                description=img.get('description'),
                image_index=i
            )
            for i, img in enumerate(images)
        ]

    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method that orchestrates the scraping process."""
        self.logger.info(f"Starting scraping process for {self.__class__.__name__}")
        results = []
        
        try:
            listing_urls = self.get_listing_urls()
            self.logger.info(f"Found {len(listing_urls)} listings to scrape")
            
            for url in listing_urls:
                try:
                    data = self.parse_listing(url)
                    if data:
                        results.append(data)
                        self.logger.info(f"Successfully scraped listing: {url}")
                    else:
                        self.logger.warning(f"Failed to parse listing: {url}")
                except Exception as e:
                    self.logger.error(f"Error scraping listing {url}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in scraping process: {str(e)}")
            
        self.logger.info(f"Completed scraping process. Total results: {len(results)}")
        return results
