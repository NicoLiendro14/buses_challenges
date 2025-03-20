import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from scrapers.micro_bird_scraper import MicroBirdScraper

@pytest.fixture
def scraper():
    return MicroBirdScraper()

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.raise_for_status.return_value = None
    return mock

@pytest.fixture
def main_page_html():
    return """
    <div class="wixui-box">
        <a class="PlZyDq VU4Mnk wixui-button" href="/school-vehicles" target="_self">
            <span class="w4Vxx6 wixui-button__label">School Buses</span>
        </a>
        <a class="PlZyDq VU4Mnk wixui-button" href="/mfsab" target="_self">
            <span class="w4Vxx6 wixui-button__label">Multi-Function School Activity Buses</span>
        </a>
    </div>
    """

@pytest.fixture
def category_page_html():
    return """
    <div class="comp-kyd72fuw1-container">
        <a class="h1DYhE" href="/g5-school-bus">
            <img src="g5.png" alt="G5">
        </a>
        <span class="w4Vxx6 wixui-button__label">G5</span>
        <p class="font_8">Up to 36 passengers</p>
    </div>
    """

@pytest.fixture
def listing_page_html():
    return """
    <div>
        <h2 class="font_2">G5 School Bus</h2>
        <h5 class="font_5">Up to 36 passengers</h5>
        <a aria-label="Consult the Specsheet" href="/specs.pdf">Consult the Specsheet</a>
    </div>
    """

def test_get_listings(scraper, mock_response, main_page_html):
    with patch.object(scraper.session, 'get', return_value=mock_response) as mock_get:
        mock_response.text = main_page_html
        
        listings = scraper.get_listings()
        
        assert len(listings) == 2
        assert listings[0]['title'] == 'School Buses'
        assert listings[0]['url'] == '/school-vehicles'
        assert listings[1]['title'] == 'Multi-Function School Activity Buses'
        assert listings[1]['url'] == '/mfsab'
        
        mock_get.assert_called_once_with('https://www.microbird.com/our-buses')

def test_get_category_listings(scraper, mock_response, category_page_html):
    with patch.object(scraper.session, 'get', return_value=mock_response) as mock_get:
        mock_response.text = category_page_html
        
        listings = scraper.get_category_listings('/school-vehicles')
        
        assert len(listings) == 1
        assert listings[0]['title'] == 'G5'
        assert listings[0]['url'] == '/g5-school-bus'
        assert listings[0]['capacity'] == 'Up to 36 passengers'
        assert listings[0]['image_url'] == 'g5.png'
        
        mock_get.assert_called_once_with('/school-vehicles')

def test_parse_listing(scraper, mock_response, listing_page_html):
    with patch.object(scraper.session, 'get', return_value=mock_response) as mock_get, \
         patch.object(scraper, 'download_pdf') as mock_download, \
         patch.object(scraper, 'extract_tables_from_pdf') as mock_extract, \
         patch.object(scraper, 'cleanup_pdf') as mock_cleanup:
        
        mock_response.text = listing_page_html
        mock_download.return_value = 'temp.pdf'
        mock_extract.return_value = [
            [['Specification', 'Value'], ['Length', '25 ft'], ['Width', '7.5 ft']]
        ]
        
        result = scraper.parse_listing('/g5-school-bus')
        
        assert result is not None
        assert result['title'] == 'G5 School Bus'
        assert result['capacity'] == 'Up to 36 passengers'
        assert result['specifications'] == {
            'Length': '25 ft',
            'Width': '7.5 ft'
        }
        
        mock_get.assert_called_once_with('/g5-school-bus')
        mock_download.assert_called_once_with('/specs.pdf')
        mock_cleanup.assert_called_once_with('temp.pdf')

def test_parse_listing_no_pdf(scraper, mock_response):
    with patch.object(scraper.session, 'get', return_value=mock_response) as mock_get:
        mock_response.text = '<div>No PDF link here</div>'
        
        result = scraper.parse_listing('/some-url')
        
        assert result is None
        mock_get.assert_called_once_with('/some-url') 