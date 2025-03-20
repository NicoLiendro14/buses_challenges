import pytest
from unittest.mock import patch, MagicMock
from scrapers import DaimlerScraper
import json

@pytest.fixture
def scraper():
    return DaimlerScraper()

@pytest.fixture
def mock_html():
    return """
    <div class="coaches-models-box">
        <div class="coaches-models-image multi-images">
            <a href="https://example.com/image.jpg" data-model-id="1626" class="fancybox-gallery">
                <img src="https://example.com/image.jpg">
            </a>
            <span>Sold</span>
        </div>
        <div class="coaches-models-content">
            <h4>2023 Mercedes Benz Tourrider Business – 91620 – 56 Pass – ADA – SOLD| $495,000.00</h4>
            <div>
                <strong>VIN#:</strong> WEBS404H3P3291620<br>
                <strong>Engine:</strong> Mercedes<br>
                <strong>Mileage:</strong> 70470<br>
            </div>
            <a href="/contact-page/?model_id=1626" class="elementor-button">CONTACT US</a>
        </div>
    </div>
    """

@pytest.fixture
def mock_images_response():
    return [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
    ]

def test_get_listing_urls(scraper, mock_html):
    with patch.object(scraper, 'get_page') as mock_get_page:
        mock_get_page.return_value = MagicMock(select=lambda x: [MagicMock(
            select_one=lambda y: MagicMock(
                attrs={'data-model-id': '1626'}
            )
        )])
        
        urls = scraper.get_listing_urls()
        assert urls == ['1626']

def test_get_images(scraper, mock_images_response):
    with patch.object(scraper.session, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_images_response)
        mock_post.return_value = mock_response
        
        images = scraper.get_images('1626')
        assert images == mock_images_response

def test_parse_listing(scraper, mock_html, mock_images_response):
    with patch.object(scraper, 'get_page') as mock_get_page, \
         patch.object(scraper, 'get_images') as mock_get_images:
        
        details_mock = MagicMock()
        details_mock.select_one.side_effect = lambda selector: {
            'strong:contains("VIN#:") + br': MagicMock(text='WEBS404H3P3291620'),
            'strong:contains("Engine:") + br': MagicMock(text='Mercedes'),
            'strong:contains("Mileage:") + br': MagicMock(text='70470')
        }.get(selector)

        box_mock = MagicMock()
        box_mock.select_one.side_effect = lambda selector: {
            'h4': MagicMock(text="2023 Mercedes Benz Tourrider Business – 91620 – 56 Pass – ADA – SOLD| $495,000.00"),
            'div': details_mock,
            '.coaches-models-image span': MagicMock(text="Sold")
        }.get(selector)

        mock_get_page.return_value = MagicMock(
            select_one=lambda x: MagicMock(
                find_parent=lambda y: box_mock
            )
        )
        mock_get_images.return_value = mock_images_response
        
        result = scraper.parse_listing('1626')
        
        assert result is not None
        assert result['year'] == '2023'
        assert result['make'] == 'Mercedes Benz'
        assert result['model'] == 'Tourrider'
        assert result['unit_number'] == '91620'
        assert result['passengers'] == '56 Pass'
        assert result['vin'] == 'WEBS404H3P3291620'
        assert result['engine'] == 'Mercedes'
        assert result['mileage'] == '70470'
        assert result['price'] == '495,000.00'
        assert result['sold'] is True
        assert len(result['images']) == 2

def test_parse_listing_with_invalid_data(scraper):
    with patch.object(scraper, 'get_page') as mock_get_page:
        mock_get_page.return_value = None
        result = scraper.parse_listing('invalid_id')
        assert result is None

def test_normalize_price(scraper):
    assert scraper.normalize_price('$495,000.00') == '$495,000.00'
    assert scraper.normalize_price('495000') == '$495,000.00'
    assert scraper.normalize_price('invalid') is None

def test_normalize_mileage(scraper):
    assert scraper.normalize_mileage('70470') == '70,470'
    assert scraper.normalize_mileage('invalid') is None 