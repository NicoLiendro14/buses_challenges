from typing import List, Dict, Any, Optional
import logging
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import time
import re
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.base_scraper import BaseScraper
from scrapers.pdf_mixin import PDFMixin

logger = logging.getLogger(__name__)

class MicroBirdScraper(BaseScraper, PDFMixin):
    BASE_URL = "https://www.microbird.com"
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
    def _is_bus_category_link(self, link) -> bool:
        if not link.get('data-testid') == 'linkElement':
            return False
        if not link.get('target') == '_self':
            return False
        if not link.get('class') or 'wixui-button' not in link.get('class'):
            return False
            
        aria_label = link.get('aria-label', '').lower()
        bus_terms = ['bus', 'vehicle']
        return any(term in aria_label for term in bus_terms)
        
    def _process_specs_table(self, table: List[List[str]]) -> Dict:
        """Process the specs table from PDF to extract structured data."""
        self.logger.info("Processing specifications table")
        
        specs = {
            'dimensions': {},
            'chassis': {},
            'models': []
        }
        
        if not table or len(table) < 3:
            self.logger.warning("Table is too small to process")
            return specs
            
        current_section = None
        manufacturers = []
        
        for row_idx, row in enumerate(table):
            if not row or len(row) < 2:
                continue
                
            first_cell = row[0].strip() if row[0] else ''
            
            if 'BODY DIMENSION' in first_cell:
                current_section = 'dimensions'

                if row_idx + 1 < len(table):
                    mfg_row = table[row_idx + 1]
                    
                    manufacturers = []
                    chevy_cols = []
                    ford_cols = []
                    
                    for col_idx, cell in enumerate(mfg_row):
                        if not cell:
                            continue
                        cell = cell.strip()
                        if 'CHEVY' in cell or 'GMC' in cell:
                            chevy_cols.append(col_idx)
                        elif 'FORD' in cell:
                            ford_cols.append(col_idx)
                    
                    if chevy_cols:
                        manufacturers.append({
                            'name': 'CHEVY/GMC',
                            'start_col': min(chevy_cols),
                            'end_col': ford_cols[0] if ford_cols else len(mfg_row),
                            'models': {}
                        })
                        
                    if ford_cols:
                        manufacturers.append({
                            'name': 'FORD',
                            'start_col': min(ford_cols),
                            'end_col': len(mfg_row),
                            'models': {}
                        })
                
                self.logger.info(f"Found manufacturers: {[m['name'] for m in manufacturers]}")
                continue
                
            elif 'CHASSIS' in first_cell:
                current_section = 'chassis'
                continue
                
            if first_cell == 'Model' and manufacturers:
                for mfg in manufacturers:
                    model_row_values = row[mfg['start_col']:mfg['end_col']]
                    model_indices = {}
                    
                    for col_offset, model_value in enumerate(model_row_values, 0):
                        if model_value and model_value.strip():
                            abs_col_idx = mfg['start_col'] + col_offset
                            model_name = model_value.strip()
                            
                            model_key = f"{mfg['name']}_{model_name}"
                            model_exists = False
                            
                            for idx, model in enumerate(specs['models']):
                                if model['manufacturer'] == mfg['name'] and model['model'] == model_name:
                                    model_indices[abs_col_idx] = idx
                                    model_exists = True
                                    break
                                    
                            if not model_exists:
                                specs['models'].append({
                                    'manufacturer': mfg['name'],
                                    'model': model_name,
                                    'specs': {},
                                    'vehicle_type': 'School Bus'
                                })
                                model_indices[abs_col_idx] = len(specs['models']) - 1
                    
                    mfg['models'] = model_indices
                
                self.logger.info(f"Found models: {[m['model'] for m in specs['models']]}")
                continue
                
            if current_section and first_cell not in ['', 'Model'] and manufacturers:
                spec_name = first_cell.lower()
                spec_name = spec_name.replace('overal', 'overall').replace('capaci', 'capacity')
                
                if 'max passenger capacity' in spec_name:
                    spec_name = 'passengers'
                elif 'number of rows' in spec_name:
                    spec_name = 'number_of_rows'
                
                is_important_spec = any(keyword in spec_name for keyword in 
                                       ['engine', 'transmission', 'gvwr', 'fuel', 'brakes'])
                
                for mfg in manufacturers:
                    if is_important_spec:
                        spec_values = []
                        for col_idx in range(mfg['start_col'], mfg['end_col']):
                            if col_idx < len(row) and row[col_idx] and row[col_idx].strip():
                                spec_values.append(row[col_idx].strip())
                        
                        if spec_values:
                            value = ' '.join(spec_values)
                            specs[current_section][f"{spec_name}_{mfg['name'].lower().replace('/', '_')}"] = value
                            
                            for model_idx in mfg['models'].values():
                                specs['models'][model_idx]['specs'][spec_name] = value
                    else:
                        for col_idx, model_idx in mfg['models'].items():
                            if col_idx < len(row) and row[col_idx] and row[col_idx].strip():
                                specs['models'][model_idx]['specs'][spec_name] = row[col_idx].strip()
        
        for model in specs['models']:
            if 'max passenger capacity' in model['specs'] and 'passengers' not in model['specs']:
                model['specs']['passengers'] = model['specs']['max passenger capacity']
        
        for model in specs['models']:
            mfg_key = model['manufacturer'].lower().replace('/', '_')
            
            for spec in ['engine', 'transmission', 'gvwr']:
                chassis_key = f"{spec}_{mfg_key}"
                if chassis_key in specs['chassis'] and spec not in model['specs']:
                    model['specs'][spec] = specs['chassis'][chassis_key]
        
        self.logger.info(f"Successfully processed {len(specs['models'])} models")
        return specs
        
    def get_listing_urls(self) -> List[str]:
        """Get all listing URLs from the website in a two-step process."""
        try:
            logger.info("Step 1: Fetching main categories")
            soup = self.get_page(f"{self.BASE_URL}/our-buses")
            if not soup:
                return []
            
            main_categories = {
                'school-vehicles',     # School Buses
                'mfsab',              # Multi-Function School Activity Buses
                'mpv',                # Multi-Purpose Vehicles
                'commercial-buses',    # Commercial Buses
                'alternative-fuels'    # Alternative Fuels Vehicles
            }
            
            category_urls = set()
            for link in soup.select('.wixui-button[data-testid="linkElement"]'):
                href = link.get('href', '')
                if any(category in href for category in main_categories):
                    if self.BASE_URL in href:
                        category_urls.add(urljoin(self.BASE_URL, href))
            
            logger.info(f"Found {len(category_urls)} main vehicle categories")
            
            model_urls = set()
            for category_url in category_urls:
                logger.info(f"Fetching models from category: {category_url}")
                soup = self.get_page(category_url)
                if not soup:
                    continue
                
                for link in soup.select('.wixui-button[data-testid="linkElement"]'):
                    href = link.get('href', '')
                    model_urls.add(urljoin(self.BASE_URL, href))
            
            model_urls_list = list(model_urls)
            logger.info(f"Found {len(model_urls_list)} unique vehicle models")
            return model_urls_list
            
        except Exception as e:
            logger.error(f"Error getting listing URLs: {str(e)}")
            return []
        
    def get_listings(self) -> List[Dict]:
        try:
            response = self.session.get(f"{self.BASE_URL}/our-buses")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            listings = []
            links = soup.find_all('a')
            
            for link in links:
                if self._is_bus_category_link(link):
                    url = link['href']
                    title = link.find('span', class_='w4Vxx6 wixui-button__label').text
                    listings.append({
                        'url': url,
                        'title': title
                    })
            
            return listings
            
        except Exception as e:
            self.logger.error(f"Error getting listings: {str(e)}")
            return []
            
    def get_category_listings(self, category_url: str) -> List[Dict]:
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            listings = []
            items = soup.find_all('div', class_='comp-kyd72fuw1-container')
            
            for item in items:
                link = item.find('a', class_='h1DYhE')
                if not link:
                    continue
                    
                url = link['href']
                img = link.find('img')
                img_url = img['src'] if img else None
                
                name_elem = item.find('span', class_='w4Vxx6 wixui-button__label')
                capacity_elem = item.find('p', class_='font_8')
                
                listings.append({
                    'url': url,
                    'title': name_elem.text if name_elem else None,
                    'capacity': capacity_elem.text if capacity_elem else None,
                    'image_url': img_url
                })
            
            return listings
            
        except Exception as e:
            self.logger.error(f"Error getting category listings: {str(e)}")
            return []
            
    def _is_specs_table(self, table: List[List[str]]) -> bool:
        if not table or len(table) < 2:
            return False
            
        first_row = table[0]
        if not first_row or len(first_row) < 2:
            return False
            
        characteristic_headers = ['Model', 'Max passenger capacity', 'Number of rows', 'Exterior length']
        for row in table:
            if row and row[0] and any(header in row[0] for header in characteristic_headers):
                return True
                
        return False
        
    def parse_listing(self, url: str) -> Optional[Dict]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            images = []
            for img in soup.select('[data-testid="imageX"] img[loading="lazy"]'):
                if src := img.get('src'):
                    base_url = src.split('/v1/')[0]
                    images.append({
                        'url': base_url,
                        'name': base_url.split('/')[-1],
                        'description': img.get('alt', '')
                    })
            
            if images:
                images = [images[0]]
            
            pdf_link = soup.find('a', {'href': lambda x: x and x.endswith('.pdf')})
            
            if not pdf_link or 'href' not in pdf_link.attrs:
                self.logger.warning(f"No PDF specsheet found for {url} after trying multiple methods")
                return None
                
            pdf_url = pdf_link['href']
            
            pdf_path = self.download_pdf(pdf_url)
            if not pdf_path:
                return None
                
            try:
                tables = self.extract_tables_from_pdf(pdf_path)
                specs = {}
                
                for table in tables:
                    if self._is_specs_table(table):
                        specs.update(self._process_specs_table(table))
                        break
                
                title = soup.find('h2', class_='font_2')
                title = title.text if title else None
                
                capacity_elem = soup.find('h5', class_='font_5')
                capacity = capacity_elem.text if capacity_elem else None
                
                specs['images'] = images
                
                return {
                    'url': url,
                    'title': title,
                    'capacity': capacity,
                    'specifications': specs
                }
                
            finally:
                self.cleanup_pdf(pdf_path)
                
        except Exception as e:
            self.logger.error(f"Error parsing listing {url}: {str(e)}")
            return None 

if __name__ == "__main__":
    from database import db, Bus, BusOverview, BusImage

    def test_micro_bird_scraper():
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("MicroBirdTest")
        
        scraper = MicroBirdScraper()
        
        listing_urls = scraper.get_listing_urls()
        total_listings = len(listing_urls)
        logger.info(f"Found {total_listings} listings to process")
        #assert total_listings > 30, f"Expected at least 30 listings, found {total_listings}"
        
        successful = 0
        failed = 0
        results = []
        
        required_fields = [
            'title', 'description', 'images', 'source', 'source_url'
        ]

        for i, url in enumerate(listing_urls, 1):
            logger.info(f"Processing listing {i}/{total_listings} (URL: {url})")
            
            try:
                listing = scraper.parse_listing(url)
                if not listing:
                    logger.error(f"Failed to parse listing {url}")
                    failed += 1
                    continue

                missing_fields = [field for field in required_fields if field not in listing]
                if missing_fields:
                    logger.warning(f"Listing {url} missing fields: {missing_fields}")
                
                if not listing.get('specifications').get('images'):
                    logger.warning(f"Listing {url} has no images")
                
                results.append(listing)
                successful += 1
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing listing {url}: {str(e)}")
                failed += 1

        logger.info("\nScraping Summary:")
        logger.info(f"Total listings found: {total_listings}")
        logger.info(f"Successfully processed: {successful}")
        logger.info(f"Failed to process: {failed}")
        logger.info(f"Success rate: {(successful/total_listings)*100:.2f}%")

        if results:
            logger.info("\nSample data from first successful listing:")
            for key, value in results[0].items():
                if key != 'images':
                    logger.info(f"{key}: {value}")
            logger.info(f"Number of images: {len(results[0].get('images', []))}")
            
        return results

    results = test_micro_bird_scraper() 