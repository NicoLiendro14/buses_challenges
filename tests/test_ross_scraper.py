import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from scrapers.ross_scraper import RossScraper
from database.processor import DataProcessor
from database import db, Bus, BusOverview, BusImage

@pytest.fixture
def scraper():
    return RossScraper()

@pytest.fixture
def processor():
    return DataProcessor()

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    return mock

@pytest.fixture
def main_page_html():
    return """
    <html>
        <body>
            <li>
                <div class="Col">
                    <div class="ListGridView">
                        <div class="ImgWrapper BusImgBal">
                            <a href="/vision">
                                <img src="/siteuploads/rossbus/crop_nhJNqvision-propane.jpg">
                            </a>
                        </div>
                        <div class="Information">
                            <h6 class="Title BusTitleBal">Vision</h6>
                            <div class="Desc FParagraph1 BusDescBal">
                                Our Blue Bird Vision earns its name due to the exceptional driver visibility.
                            </div>
                        </div>
                    </div>
                </div>
            </li>
            <li>
                <div class="Col">
                    <div class="ListGridView">
                        <div class="ImgWrapper BusImgBal">
                            <a href="/micro-bird">
                                <img src="/siteuploads/rossbus/1240_img2_micro-bird-g5-propane.png">
                            </a>
                        </div>
                        <div class="Information">
                            <h6 class="Title BusTitleBal">Micro Bird</h6>
                            <div class="Desc FParagraph1 BusDescBal">
                                Micro Bird has been manufacturing buses for over 50 years.
                            </div>
                        </div>
                    </div>
                </div>
            </li>
        </body>
    </html>
    """

@pytest.fixture
def category_page_html():
    return """
    <html>
        <body>
            <li>
                <div class="Col">
                    <div class="ListGridView ListInnerWrap">
                        <div class="ImgWrapper BusImgBal">
                            <a href="/vision-propane">
                                <img src="/siteimgs/370X250/2/1/siteuploads/rossbus/1241_img2_vision-propane.png">
                            </a>
                        </div>
                        <div class="Information">
                            <h6 class="Title BusTitleBal">Vision Propane</h6>
                            <div class="Desc FParagraph1 BusDescBal">
                                With over 12,000 sold, Blue Bird's 4th Generation Vision Propane bus.
                            </div>
                        </div>
                    </div>
                </div>
            </li>
            <!-- Duplicado intencional -->
            <li>
                <div class="Col">
                    <div class="ListGridView ListInnerWrap">
                        <div class="ImgWrapper BusImgBal">
                            <a href="/vision-propane">
                                <img src="/siteimgs/370X250/2/1/siteuploads/rossbus/1241_img2_vision-propane.png">
                            </a>
                        </div>
                        <div class="Information">
                            <h6 class="Title BusTitleBal">Vision Propane</h6>
                            <div class="Desc FParagraph1 BusDescBal">
                                With over 12,000 sold, Blue Bird's 4th Generation Vision Propane bus.
                            </div>
                        </div>
                    </div>
                </div>
            </li>
        </body>
    </html>
    """

@pytest.fixture
def detail_page_html():
    return """
    <html>
        <body>
            <section class="IdxDetailPageWrap">
                <div class="InnerContainWrapper">
                    <div class="TopSection">
                        <h5 class="BlueTitle">Vision Propane</h5>
                        <div class="Describe FParagraph1 EditorText">
                            With over 12,000 sold, Blue Bird's 4th Generation Vision Propane bus.
                        </div>
                    </div>
                    <div id="slider" class="flexslider">
                        <ul class="slides">
                            <li>
                                <img src="/siteimgs/775X520/2/1/siteuploads/photogalleryimg/124vision-propane.jpg">
                            </li>
                        </ul>
                    </div>
                    <div class="Extra_Info_Wrap">
                        <ul>
                            <li>Seating Capacity: 83</li>
                            <li>Lift Equipped: No</li>
                            <li>Brakes: Hydraulic</li>
                            <li>Fuel: Gas</li>
                            <li>A/C: No</li>
                        </ul>
                    </div>
                    <div class="DeepDetails">
                        <ul>
                            <li class="addColon">
                                <div class="First">Capacity</div>
                                <div class="Last">Multiple floor plans available with passenger seating up to 78</div>
                            </li>
                            <li class="addColon">
                                <div class="First">Engine</div>
                                <div class="Last">Ford® 6.8L with ROUSH CleanTech Propane Fuel System, 320 hp</div>
                            </li>
                            <li class="addColon">
                                <div class="First">Transmission</div>
                                <div class="Last">Ford® 6R140 - 6 speed automatic</div>
                            </li>
                            <li class="addColon">
                                <div class="First">GVWR</div>
                                <div class="Last">Up to 33,000 lbs.</div>
                            </li>
                        </ul>
                    </div>
                </div>
            </section>
        </body>
    </html>
    """

def test_get_listings(scraper, mock_response, main_page_html):
    """Test getting main listings."""
    mock_response.text = main_page_html
    with patch.object(scraper.session, 'get', return_value=mock_response):
        listings = scraper.get_listings()
        assert len(listings) == 2
        assert any(listing['title'] == 'Vision' for listing in listings)
        assert any(listing['title'] == 'Micro Bird' for listing in listings)

def test_get_category_listings_duplicates(scraper, mock_response, category_page_html):
    """Test handling of duplicate listings in category page."""
    mock_response.text = category_page_html
    with patch.object(scraper.session, 'get', return_value=mock_response):
        listings = scraper.get_category_listings('https://www.rossbus.com/vision')
        assert len(listings) == 1  # Should only return one listing despite duplicate in HTML
        assert listings[0]['title'] == 'Vision Propane'

def test_parse_listing(scraper, mock_response, detail_page_html):
    """Test parsing detailed listing page."""
    mock_response.text = detail_page_html
    with patch.object(scraper.session, 'get', return_value=mock_response):
        data = scraper.parse_listing('https://www.rossbus.com/vision-propane')
        assert data is not None
        assert data['title'] == 'Vision Propane'
        assert len(data['images']) == 1
        assert data['passengers'] == 'Multiple floor plans available with passenger seating up to 78'
        assert 'Ford® 6.8L' in data['engine']
        assert '6 speed automatic' in data['transmission']
        assert '33,000 lbs' in data['gvwr']

def test_save_bus_data(processor):
    """Test saving bus data to database."""
    test_data = {
        'title': 'Vision Propane',
        'description': 'Test description',
        'vin': 'TEST123456789',
        'source': 'Ross Bus',
        'source_url': 'https://www.rossbus.com/vision-propane',
        'images': [{
            'url': 'https://example.com/image1.jpg',
            'name': 'image_1',
            'description': 'Front view'
        }]
    }
    
    bus = processor.save_bus_data(test_data)
    assert bus is not None
    assert bus.title == test_data['title']
    assert bus.vin == test_data['vin']
    
    session = db.session
    try:
        saved_bus = session.query(Bus).filter_by(vin=test_data['vin']).first()
        assert saved_bus is not None
        assert saved_bus.id == bus.id
    finally:
        session.close()

def test_save_multiple_buses(processor):
    """Test saving multiple bus records."""
    test_data_list = [
        {
            'title': 'Vision Propane 1',
            'description': 'Test description 1',
            'vin': 'TEST123456789',
            'source': 'Ross Bus',
            'source_url': 'https://www.rossbus.com/vision-propane-1'
        },
        {
            'title': 'Vision Propane 2',
            'description': 'Test description 2',
            'vin': 'TEST987654321',
            'source': 'Ross Bus',
            'source_url': 'https://www.rossbus.com/vision-propane-2'
        }
    ]
    
    saved_buses = processor.save_multiple_buses(test_data_list)
    assert len(saved_buses) == 2
    assert all(bus.id is not None for bus in saved_buses)
    assert saved_buses[0].vin == test_data_list[0]['vin']
    assert saved_buses[1].vin == test_data_list[1]['vin'] 