from typing import List, Dict, Optional, Any
import json
import re
from urllib.parse import urljoin
import pdb
import sys
import os
import logging

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.base_scraper import BaseScraper
from database import AirConditioningType, USRegion

class DaimlerScraper(BaseScraper):
    BASE_URL = "https://www.daimlercoachesnorthamerica.com"
    LISTINGS_URL = f"{BASE_URL}/pre-owned-motor-coaches/"
    AJAX_URL = f"{BASE_URL}/wp-admin/admin-ajax.php"
    
    def __init__(self):
        super().__init__()
        self._main_page_soup = None
        
    def get_main_page(self):
        """Get the main page once and cache it."""
        if not self._main_page_soup:
            self._main_page_soup = self.get_page(self.LISTINGS_URL)
        return self._main_page_soup

    def get_listing_urls(self) -> List[str]:
        """Get all listing URLs from the main page."""
        soup = self.get_main_page()
        if not soup:
            return []

        listings = []
        for listing in soup.select('.coaches-models-box'):
            img_link = listing.select_one('.coaches-models-image a')
            if img_link and 'data-model-id' in img_link.attrs:
                listings.append(img_link.attrs['data-model-id'])

        return listings

    def extract_detail_text(self, element, label):
        """Extract text that appears after a strong tag with the given label."""
        if not element:
            return None
        
        for strong in element.find_all('strong'):
            if label in strong.text:
                next_content = strong.next_sibling
                if next_content and isinstance(next_content, str):
                    return next_content.strip()
        return None

    def get_images(self, model_id: str) -> List[str]:
        """Get all images for a specific model using AJAX request."""
        data = {
            'action': 'load_fancybox_images',
            'model_id': model_id,
        }
        
        try:
            response = self.session.post(
                self.AJAX_URL,
                headers={
                    **self.headers,
                    'x-requested-with': 'XMLHttpRequest',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                },
                data=data,
                timeout=30
            )
            response.raise_for_status()
            return json.loads(response.text)
        except Exception as e:
            self.logger.error(f"Error fetching images for model {model_id}: {str(e)}")
            return []

    def parse_listing(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Parse a single listing page and return structured data."""            
        soup = self.get_main_page()
        if not soup:
            return None

        box = soup.select_one(f'.coaches-models-box:has(a[data-model-id="{model_id}"])')
        if not box:
            for box_elem in soup.select('.coaches-models-box'):
                if box_elem.select_one(f'a[data-model-id="{model_id}"]'):
                    box = box_elem
                    break
        
        if not box:
            return None

        title_elem = box.select_one('h4')
        if not title_elem:
            return None

        title_text = title_elem.text.strip()
        price_match = re.search(r'\$([\d,]+\.?\d*)', title_text)
        price = price_match.group(1) if price_match else None

        details = box.select_one('.coaches-models-content div')
        if not details:
            return None

        vin = self.extract_detail_text(details, 'VIN#:')
        engine = self.extract_detail_text(details, 'Engine:')
        mileage = self.extract_detail_text(details, 'Mileage:')
        transmission = self.extract_detail_text(details, 'Transmission:')
        gvwr = self.extract_detail_text(details, 'GVWR:')
        wheelchair = self.extract_detail_text(details, 'Wheelchair:')
        location = self.extract_detail_text(details, 'Location:')

        description = self.extract_text(details, '.description')
        features = self.extract_text(details, '.features')
        specifications = self.extract_text(details, '.specifications')

        title_parts = title_text.split('|')[0].strip().split('–')
        if len(title_parts) >= 3:
            year_make_model = title_parts[0].strip()
            unit_number = title_parts[1].strip()
            passengers = title_parts[2].strip()
        else:
            year_make_model = title_parts[0].strip()
            unit_number = ""
            passengers = ""

        words = year_make_model.split()
        year = words[0]
        make = ' '.join(words[1:3])
        model = words[3] if len(words) > 3 else ""

        images = self.get_images(model_id)

        sold_elem = box.select_one('.coaches-models-image span')
        is_sold = sold_elem and sold_elem.text.strip().lower() == 'sold'
        
        has_wheelchair = 'ada' in title_text.lower() or 'wheelchair' in title_text.lower()

        us_region = self._determine_region(location)

        return {
            'title': title_text,
            'year': year,
            'make': make,
            'model': model,
            'unit_number': unit_number,
            'passengers': passengers,
            'wheelchair': has_wheelchair or (wheelchair == 'Yes' if wheelchair else False),
            'vin': vin,
            'engine': engine,
            'transmission': transmission,
            'gvwr': gvwr,
            'mileage': mileage,
            'price': price,
            'sold': is_sold,
            'source': 'Daimler Coaches North America',
            'source_url': self.LISTINGS_URL,
            'location': location,
            'us_region': us_region,
            'description': description,
            'features': features,
            'specifications': specifications,
            'images': [
                {
                    'url': url,
                    'name': f'image_{i}',
                    'description': f'Image {i+1} of {len(images)}'
                }
                for i, url in enumerate(images)
            ]
        }

    def _determine_region(self, location: Optional[str]) -> USRegion:
        """Determine the US region based on location."""
        if not location:
            return USRegion.OTHER

        location = location.lower()
        if any(state in location for state in ['new york', 'massachusetts', 'connecticut', 'rhode island', 'vermont', 'new hampshire', 'maine']):
            return USRegion.NORTHEAST
        elif any(state in location for state in ['florida', 'georgia', 'alabama', 'mississippi', 'louisiana', 'arkansas', 'tennessee', 'kentucky', 'west virginia', 'virginia', 'north carolina', 'south carolina']):
            return USRegion.SOUTH
        elif any(state in location for state in ['ohio', 'indiana', 'illinois', 'michigan', 'wisconsin', 'minnesota', 'iowa', 'missouri', 'north dakota', 'south dakota', 'nebraska', 'kansas']):
            return USRegion.MIDWEST
        elif any(state in location for state in ['washington', 'oregon', 'california', 'nevada', 'idaho', 'utah', 'arizona', 'montana', 'wyoming', 'colorado', 'new mexico', 'alaska', 'hawaii']):
            return USRegion.WEST
        else:
            return USRegion.OTHER