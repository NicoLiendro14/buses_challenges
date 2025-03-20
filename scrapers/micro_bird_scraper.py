from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
from .base_scraper import BaseScraper
from .pdf_mixin import PDFMixin

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
        specs = {
            'dimensions': {},
            'chassis': {},
            'models': []
        }
        
        current_section = None
        current_manufacturer = None
        
        for row in table:
            if not row or not any(row):
                continue
                
            first_cell = row[0].strip() if row[0] else ''
            
            if any('CHEVY/GMC' in str(cell) or 'FORD' in str(cell) for cell in row):
                for cell in row:
                    if cell and ('CHEVY/GMC' in cell or 'FORD' in cell):
                        current_manufacturer = cell.strip()
                continue
            
            if first_cell == 'Model' and current_manufacturer:
                model_values = []
                for cell in row[1:]:
                    if cell and cell.strip():
                        model_values.extend(cell.strip().split())
                
                for model in model_values:
                    specs['models'].append({
                        'manufacturer': current_manufacturer,
                        'model': model,
                        'specs': {}
                    })
        
        current_manufacturer = None
        current_section = None
        
        for row in table:
            if not row or not any(row):
                continue
                
            first_cell = row[0].strip() if row[0] else ''
            
            if 'BODY DIMENS' in first_cell:
                current_section = 'dimensions'
                continue
            elif 'CHASSIS' in first_cell:
                current_section = 'chassis'
                continue
            
            if any('CHEVY/GMC' in str(cell) or 'FORD' in str(cell) for cell in row):
                for cell in row:
                    if cell and ('CHEVY/GMC' in cell or 'FORD' in cell):
                        current_manufacturer = cell.strip()
                continue
            
            if first_cell in ['Model', ''] or not current_section or not current_manufacturer:
                continue
            
            spec_name = first_cell.replace('overal', 'overall').replace('capaci', 'capacity')
            
            values = []
            for cell in row[1:]:
                if cell and cell.strip():
                    values.append(cell.strip())
            
            if values:
                if any(keyword in spec_name for keyword in ['Engine', 'Transmission', 'GVWR', 'Brakes']):
                    value = ' '.join(values)
                    specs[current_section][f"{spec_name.lower()}_{current_manufacturer.lower().replace('/', '_')}"] = value
                else:
                    current_models = [m for m in specs['models'] if m['manufacturer'] == current_manufacturer]
                    for i, value in enumerate(values):
                        if i < len(current_models):
                            current_models[i]['specs'][spec_name.lower()] = value
        
        return specs
        
    def get_listing_urls(self) -> List[str]:
        try:
            response = self.session.get(f"{self.BASE_URL}/our-buses")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            urls = []
            links = soup.find_all('a')
            
            for link in links:
                if self._is_bus_category_link(link):
                    url = link['href']
                    urls.append(url)
            
            return urls
            
        except Exception as e:
            self.logger.error(f"Error getting listing URLs: {str(e)}")
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
            
            pdf_link = soup.find('a', {'aria-label': 'Consult the Specsheet'})
            if not pdf_link or 'href' not in pdf_link.attrs:
                self.logger.warning(f"No PDF specsheet found for {url}")
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