from typing import List, Dict, Optional, Any
import json
import re
from urllib.parse import urljoin

from .base_scraper import BaseScraper

class DaimlerScraper(BaseScraper):
    BASE_URL = "https://www.daimlercoachesnorthamerica.com"
    LISTINGS_URL = f"{BASE_URL}/pre-owned-motor-coaches/"
    AJAX_URL = f"{BASE_URL}/wp-admin/admin-ajax.php"

    def get_listing_urls(self) -> List[str]:
        """Get all listing URLs from the main page."""
        soup = self.get_page(self.LISTINGS_URL)
        if not soup:
            return []

        listings = []
        for listing in soup.select('.coaches-models-box'):
            img_link = listing.select_one('.coaches-models-image a')
            if img_link and 'data-model-id' in img_link.attrs:
                listings.append(img_link.attrs['data-model-id'])

        return listings

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
        soup = self.get_page(self.LISTINGS_URL)
        if not soup:
            return None

        listing = soup.select_one(f'.coaches-models-box a[data-model-id="{model_id}"]')
        if not listing:
            return None

        box = listing.find_parent('.coaches-models-box')
        if not box:
            return None

        title_elem = box.select_one('h4')
        if not title_elem:
            return None

        title_text = title_elem.text.strip()
        price_match = re.search(r'\$([\d,]+\.?\d*)', title_text)
        price = price_match.group(1) if price_match else None

        details = box.select_one('div')
        if not details:
            return None

        vin = self.extract_text(details, 'strong:contains("VIN#:") + br')
        engine = self.extract_text(details, 'strong:contains("Engine:") + br')
        mileage = self.extract_text(details, 'strong:contains("Mileage:") + br')

        print(f"Debug - VIN: {vin}")
        print(f"Debug - Engine: {engine}")
        print(f"Debug - Mileage: {mileage}")

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
        model = words[3]

        print(f"Debug - Year: {year}")
        print(f"Debug - Make: {make}")
        print(f"Debug - Model: {model}")

        images = self.get_images(model_id)

        sold_elem = box.select_one('.coaches-models-image span')
        is_sold = sold_elem and sold_elem.text.strip().lower() == 'sold'

        return {
            'title': title_text,
            'year': year,
            'make': make,
            'model': model,
            'unit_number': unit_number,
            'passengers': passengers,
            'vin': vin,
            'engine': engine,
            'mileage': mileage,
            'price': price,
            'sold': is_sold,
            'source': 'Daimler Coaches North America',
            'source_url': self.LISTINGS_URL,
            'images': [
                {
                    'url': url,
                    'name': f'image_{i}',
                    'description': f'Image {i+1} of {len(images)}'
                }
                for i, url in enumerate(images)
            ]
        }
