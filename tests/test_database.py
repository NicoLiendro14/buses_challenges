import pytest
from database import db, Bus, BusOverview, BusImage, AirConditioningType, USRegion
from datetime import datetime

@pytest.fixture(scope="function")
def session():
    with db.get_session() as session:
        yield session
        session.rollback()

def test_create_tables():
    db.create_tables()
    assert True

def test_create_bus(session):
    bus = Bus(
        title="Test Bus",
        year="2023",
        make="Blue Bird",
        model="Vision",
        price="50000",
        location="New York",
        us_region=USRegion.NORTHEAST
    )
    session.add(bus)
    session.flush()
    
    assert bus.id is not None
    assert bus.title == "Test Bus"
    assert bus.year == "2023"
    assert bus.make == "Blue Bird"
    assert bus.model == "Vision"
    assert bus.price == "50000"
    assert bus.location == "New York"
    assert bus.us_region == USRegion.NORTHEAST

def test_create_bus_with_overview(session):
    bus = Bus(
        title="Test Bus with Overview",
        year="2023",
        make="Blue Bird",
        model="Vision"
    )
    session.add(bus)
    session.flush()

    overview = BusOverview(
        bus_id=bus.id,
        mdesc="Main description",
        intdesc="Interior description",
        extdesc="Exterior description",
        features="Feature 1, Feature 2",
        specs="Spec 1, Spec 2"
    )
    session.add(overview)
    session.flush()

    assert bus.overview is not None
    assert bus.overview.mdesc == "Main description"
    assert bus.overview.intdesc == "Interior description"
    assert bus.overview.extdesc == "Exterior description"
    assert bus.overview.features == "Feature 1, Feature 2"
    assert bus.overview.specs == "Spec 1, Spec 2"

def test_create_bus_with_images(session):
    bus = Bus(
        title="Test Bus with Images",
        year="2023",
        make="Blue Bird",
        model="Vision"
    )
    session.add(bus)
    session.flush()

    image1 = BusImage(
        bus_id=bus.id,
        name="front_view",
        url="http://example.com/front.jpg",
        description="Front view of the bus",
        image_index=0
    )
    image2 = BusImage(
        bus_id=bus.id,
        name="side_view",
        url="http://example.com/side.jpg",
        description="Side view of the bus",
        image_index=1
    )
    session.add(image1)
    session.add(image2)
    session.flush()

    assert len(bus.images) == 2
    assert bus.images[0].name == "front_view"
    assert bus.images[1].name == "side_view"
    assert bus.images[0].image_index == 0
    assert bus.images[1].image_index == 1

def test_bus_enum_fields(session):
    bus = Bus(
        title="Test Bus with Enums",
        year="2023",
        make="Blue Bird",
        model="Vision",
        airconditioning=AirConditioningType.BOTH,
        us_region=USRegion.WEST
    )
    session.add(bus)
    session.flush()

    assert bus.airconditioning == AirConditioningType.BOTH
    assert bus.us_region == USRegion.WEST

def test_bus_boolean_fields(session):
    bus = Bus(
        title="Test Bus with Booleans",
        year="2023",
        make="Blue Bird",
        model="Vision",
        published=True,
        featured=True,
        sold=False,
        scraped=True,
        draft=False,
        luggage=True
    )
    session.add(bus)
    session.flush()

    assert bus.published is True
    assert bus.featured is True
    assert bus.sold is False
    assert bus.scraped is True
    assert bus.draft is False
    assert bus.luggage is True 