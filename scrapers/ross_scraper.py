from typing import List, Dict, Any, Optional
import logging
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import time
import re
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class RossScraper(BaseScraper):
    """Scraper for Ross Bus website."""
    
    BASE_URL = "https://www.rossbus.com"
    SCHOOL_BUSES_URL = f"{BASE_URL}/school-buses"
    
    def __init__(self):
        super().__init__()
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.seen_titles = set()
    
    def normalize_title(self, title: str) -> str:
        """Normaliza un título para comparación."""
        title = title.lower()
        title = re.sub(r'[^\w\s]', '', title)
        title = re.sub(r'\s+', ' ', title)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = title.split()
        words = [w for w in words if w not in common_words]
        return ' '.join(words)
    
    def is_duplicate_title(self, title: str) -> bool:
        """Verifica si un título es un duplicado basado en normalización."""
        normalized_title = self.normalize_title(title)
        if normalized_title in self.seen_titles:
            logger.info(f"Found duplicate title: '{title}' (normalized: '{normalized_title}')")
            return True
        self.seen_titles.add(normalized_title)
        return False
    
    def get_listing_urls(self) -> List[str]:
        """Get all listing URLs from the website."""
        try:
            logger.info("Fetching all listing URLs")
            all_urls = []
            
            main_listings = self.get_listings()
            logger.info(f"Found {len(main_listings)} main listings")
            
            for listing in main_listings:
                try:
                    category_listings = self.get_category_listings(listing['url'])
                    logger.info(f"Found {len(category_listings)} listings in category {listing['title']}")
                    
                    all_urls.extend([item['url'] for item in category_listings])
                    
                except Exception as e:
                    logger.error(f"Error processing main listing {listing['url']}: {str(e)}")
                    continue
            
            return all_urls
            
        except Exception as e:
            logger.error(f"Error getting listing URLs: {str(e)}")
            return []
    
    def get_listings(self) -> List[Dict[str, Any]]:
        """Get all bus listings from the main page."""
        try:
            logger.info("Fetching main listings page")
            response = self.session.get(self.SCHOOL_BUSES_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []
            
            bus_items = soup.select('li .ListGridView')
            
            for item in bus_items:
                try:
                    link_elem = item.select_one('a')
                    if not link_elem:
                        continue
                        
                    link = urljoin(self.BASE_URL, link_elem['href'])
                    title = item.select_one('.Title').text.strip()
                    
                    if self.is_duplicate_title(title):
                        continue
                    
                    desc_elem = item.select_one('.Desc')
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    img_elem = item.select_one('img')
                    image_url = urljoin(self.BASE_URL, img_elem['src']) if img_elem else None
                    
                    listings.append({
                        'title': title,
                        'url': link,
                        'description': description,
                        'image_url': image_url
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing listing item: {str(e)}")
                    continue
            
            return listings
            
        except Exception as e:
            logger.error(f"Error fetching listings: {str(e)}")
            return []
    
    def get_category_listings(self, category_url: str) -> List[Dict[str, Any]]:
        """Get all bus listings from a category page."""
        try:
            logger.info(f"Fetching category page: {category_url}")
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []
            seen_urls = set()
            
            bus_items = soup.select('li .ListGridView.ListInnerWrap')
            
            for item in bus_items:
                try:
                    link_elem = item.select_one('a')
                    if not link_elem:
                        continue
                        
                    link = urljoin(self.BASE_URL, link_elem['href'])
                    
                    if link in seen_urls:
                        logger.info(f"Skipping duplicate URL: {link}")
                        continue
                    seen_urls.add(link)
                    
                    title = item.select_one('.Title').text.strip()
                    
                    if self.is_duplicate_title(title):
                        continue
                    
                    desc_elem = item.select_one('.Desc')
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    img_elem = item.select_one('img')
                    image_url = urljoin(self.BASE_URL, img_elem['src']) if img_elem else None
                    
                    listings.append({
                        'title': title,
                        'url': link,
                        'description': description,
                        'image_url': image_url
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing category listing item: {str(e)}")
                    continue
            
            return listings
            
        except Exception as e:
            logger.error(f"Error fetching category listings: {str(e)}")
            return []
    
    def parse_listing(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a detailed bus listing page."""
        try:
            logger.info(f"Parsing listing: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.select_one('.BlueTitle')
            title = title.text.strip() if title else ""
            
            description = soup.select_one('.Describe')
            description = description.text.strip() if description else ""
            
            images = []
            slider = soup.select_one('#slider .slides')
            if slider:
                for img in slider.select('img'):
                    images.append({
                        'url': urljoin(self.BASE_URL, img['src']),
                        'name': f"image_{len(images)}",
                        'description': ""
                    })
            
            specs = {}
            specs_section = soup.select_one('.Extra_Info_Wrap ul')
            if specs_section:
                for item in specs_section.select('li'):
                    if ':' in item.text:
                        key, value = item.text.split(':', 1)
                        specs[key.strip()] = value.strip()
            
            details = {}
            details_section = soup.select_one('.DeepDetails ul')
            if details_section:
                for item in details_section.select('li.addColon'):
                    key = item.select_one('.First')
                    value = item.select_one('.Last')
                    if key and value:
                        details[key.text.strip()] = value.text.strip()
            
            data = {
                'title': title,
                'description': description,
                'images': images,
                'specs': specs,
                'details': details,
                'source': 'Ross Bus',
                'source_url': url,
                'scraped': True
            }
            
            if 'Capacity' in details:
                data['passengers'] = details['Capacity']
            if 'Engine' in details:
                data['engine'] = details['Engine']
            if 'Transmission' in details:
                data['transmission'] = details['Transmission']
            if 'Brakes' in details:
                data['brake'] = details['Brakes']
            if 'GVWR' in details:
                data['gvwr'] = details['GVWR']
            if 'Overall Height' in details:
                data['dimensions'] = details['Overall Height']
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing listing {url}: {str(e)}")
            return None
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method."""
        all_listings = []
        
        try:
            main_listings = self.get_listings()
            logger.info(f"Found {len(main_listings)} main listings")
            
            for listing in main_listings:
                try:
                    category_listings = self.get_category_listings(listing['url'])
                    logger.info(f"Found {len(category_listings)} listings in category {listing['title']}")
                    
                    for category_listing in category_listings:
                        try:
                            detailed_data = self.parse_listing(category_listing['url'])
                            if detailed_data:
                                all_listings.append(detailed_data)
                                logger.info(f"Successfully scraped listing: {detailed_data['title']}")
                            
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Error processing category listing {category_listing['url']}: {str(e)}")
                            continue
                    
                except Exception as e:
                    logger.error(f"Error processing main listing {listing['url']}: {str(e)}")
                    continue
            
            return all_listings
            
        except Exception as e:
            logger.error(f"Error in main scraping process: {str(e)}")
            return [] 