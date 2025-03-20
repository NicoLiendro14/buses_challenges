from typing import List, Dict, Any, Optional
import pdfplumber
import logging
from pathlib import Path
import tempfile
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class PDFMixin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def download_pdf(self, url: str, base_url: str = None) -> Optional[Path]:
        try:
            if base_url and not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            
            self.logger.info(f"Downloading PDF from: {url}")
            response = requests.get(url, verify=False)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                return Path(tmp_file.name)
                
        except Exception as e:
            self.logger.error(f"Error downloading PDF from {url}: {str(e)}")
            return None
    
    def extract_tables_from_pdf(self, pdf_path: Path) -> List[List[List[str]]]:
        try:
            self.logger.info(f"Extracting tables from PDF: {pdf_path}")
            tables = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            
            self.logger.info(f"Found {len(tables)} tables in PDF")
            return tables
            
        except Exception as e:
            self.logger.error(f"Error extracting tables from PDF {pdf_path}: {str(e)}")
            return []
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        try:
            self.logger.info(f"Extracting text from PDF: {pdf_path}")
            text = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text.append(page.extract_text() or '')
            
            return '\n'.join(text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return ''
    
    def process_table_data(self, table: List[List[str]]) -> List[Dict[str, str]]:
        try:
            if not table or len(table) < 2:
                return []
            
            headers = [str(h).strip() for h in table[0]]
            result = []
            
            for row in table[1:]:
                if len(row) != len(headers):
                    continue
                    
                row_dict = {}
                for header, value in zip(headers, row):
                    row_dict[header] = str(value).strip() if value is not None else ''
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing table data: {str(e)}")
            return []
    
    def cleanup_pdf(self, pdf_path: Path) -> None:
        try:
            if pdf_path.exists():
                pdf_path.unlink()
                self.logger.info(f"Cleaned up temporary PDF: {pdf_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up PDF {pdf_path}: {str(e)}")