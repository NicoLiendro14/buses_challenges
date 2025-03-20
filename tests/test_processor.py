import pytest
from datetime import datetime, UTC
from database.processor import DataProcessor
from database import Bus, BusOverview, BusImage, db

@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown database for each test."""
    db.create_tables()
    yield
    session = db.session
    try:
        session.query(BusImage).delete()
        session.query(BusOverview).delete()
        session.query(Bus).delete()
        session.commit()
    finally:
        session.close()

@pytest.fixture
def processor():
    return DataProcessor()

@pytest.fixture
def sample_bus_data():
    return {
        'title': '2023 Mercedes Benz Tourrider Business',
        'year': 2023,
        'make': 'Mercedes Benz',
        'model': 'Tourrider',
        'vin': 'WEBS404H3P3291620',
        'engine': 'Mercedes',
        'mileage': '70470',
        'passengers': '56 Pass',
        'price': '495000',
        'source': 'Daimler Coaches North America',
        'source_url': 'https://example.com',
        'images': [
            {
                'url': 'https://example.com/image1.jpg',
                'name': 'image_1',
                'description': 'Front view'
            }
        ]
    }

@pytest.fixture
def sample_overview_data():
    return {
        'mdesc': 'Main description',
        'intdesc': 'Interior description',
        'extdesc': 'Exterior description',
        'features': 'Feature 1, Feature 2',
        'specs': 'Spec 1, Spec 2'
    }

def test_process_bus_data(processor, sample_bus_data):
    bus = processor.process_bus_data(sample_bus_data)
    assert bus is not None
    assert bus.title == sample_bus_data['title']
    assert bus.year == sample_bus_data['year']
    assert bus.make == sample_bus_data['make']
    assert bus.model == sample_bus_data['model']
    assert bus.vin == sample_bus_data['vin']
    assert bus.engine == sample_bus_data['engine']
    assert bus.mileage == sample_bus_data['mileage']
    assert bus.passengers == sample_bus_data['passengers']
    assert bus.price == sample_bus_data['price']
    assert bus.source == sample_bus_data['source']
    assert bus.source_url == sample_bus_data['source_url']
    assert bus.scraped is True

def test_process_overview_data(processor, sample_overview_data):
    overview = processor.process_overview_data(1, sample_overview_data)
    assert overview is not None
    assert overview.bus_id == 1
    assert overview.mdesc == sample_overview_data['mdesc']
    assert overview.intdesc == sample_overview_data['intdesc']
    assert overview.extdesc == sample_overview_data['extdesc']
    assert overview.features == sample_overview_data['features']
    assert overview.specs == sample_overview_data['specs']

def test_process_image_data(processor):
    images_data = [
        {
            'url': 'https://example.com/image1.jpg',
            'name': 'image_1',
            'description': 'Front view'
        }
    ]
    images = processor.process_image_data(1, images_data)
    assert len(images) == 1
    assert images[0].bus_id == 1
    assert images[0].url == images_data[0]['url']
    assert images[0].name == images_data[0]['name']
    assert images[0].description == images_data[0]['description']
    assert images[0].image_index == 0

def test_save_bus_data(processor, sample_bus_data):
    bus = processor.save_bus_data(sample_bus_data)
    assert bus is not None
    assert bus.id is not None
    assert bus.vin == sample_bus_data['vin']
    
    session = db.session
    try:
        saved_bus = session.query(Bus).filter_by(vin=sample_bus_data['vin']).first()
        assert saved_bus is not None
        assert saved_bus.id == bus.id
    finally:
        session.close()
    
    updated_data = sample_bus_data.copy()
    updated_data['price'] = '500000'
    updated_bus = processor.save_bus_data(updated_data)
    assert updated_bus is not None
    assert updated_bus.id == bus.id
    assert updated_bus.price == '500000'
    assert updated_bus.updated_at > bus.updated_at

def test_save_multiple_buses(processor, sample_bus_data):
    data_list = [
        sample_bus_data,
        {**sample_bus_data, 'vin': 'WEBS404H3P3291621'}
    ]
    saved_buses = processor.save_multiple_buses(data_list)
    assert len(saved_buses) == 2
    assert all(bus.id is not None for bus in saved_buses)
    assert saved_buses[0].vin != saved_buses[1].vin

    session = db.session
    try:
        saved_buses_db = session.query(Bus).filter(Bus.vin.in_([sample_bus_data['vin'], 'WEBS404H3P3291621'])).all()
        assert len(saved_buses_db) == 2
    finally:
        session.close()

def test_save_bus_with_overview(processor, sample_bus_data, sample_overview_data):
    data = {**sample_bus_data, **sample_overview_data}
    bus = processor.save_bus_data(data)
    assert bus is not None
    assert bus.id is not None
    
    session = db.session
    try:
        overview = session.query(BusOverview).filter_by(bus_id=bus.id).first()
        assert overview is not None
        assert overview.mdesc == sample_overview_data['mdesc']
        assert overview.intdesc == sample_overview_data['intdesc']
    finally:
        session.close()

def test_save_bus_with_images(processor, sample_bus_data):
    bus = processor.save_bus_data(sample_bus_data)
    assert bus is not None
    assert bus.id is not None
    
    session = db.session
    try:
        images = session.query(BusImage).filter_by(bus_id=bus.id).all()
        assert len(images) == 1
        assert images[0].url == sample_bus_data['images'][0]['url']
        assert images[0].name == sample_bus_data['images'][0]['name']
    finally:
        session.close() 