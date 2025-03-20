from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class AirConditioningType(str, Enum):
    REAR = "REAR"
    DASH = "DASH"
    BOTH = "BOTH"
    OTHER = "OTHER"
    NONE = "NONE"

class USRegion(str, Enum):
    NORTHEAST = "NORTHEAST"
    MIDWEST = "MIDWEST"
    WEST = "WEST"
    SOUTHWEST = "SOUTHWEST"
    SOUTHEAST = "SOUTHEAST"
    OTHER = "OTHER"

class Bus(Base):
    __tablename__ = 'buses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256))
    year = Column(String(10))
    make = Column(String(25))
    model = Column(String(50))
    body = Column(String(25))
    chassis = Column(String(25))
    engine = Column(String(300))
    transmission = Column(String(300))
    mileage = Column(String(100))
    passengers = Column(String(300))
    wheelchair = Column(String(60))
    color = Column(String(60))
    interior_color = Column(String(60))
    exterior_color = Column(String(60))
    published = Column(Boolean, default=False)
    featured = Column(Boolean, default=False)
    sold = Column(Boolean, default=False)
    scraped = Column(Boolean, default=False)
    draft = Column(Boolean, default=False)
    source = Column(String(300))
    source_url = Column(String(1000))
    price = Column(String(30))
    cprice = Column(String(30))
    vin = Column(String(60))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    gvwr = Column(String(50))
    dimensions = Column(String(300))
    luggage = Column(Boolean, default=False)
    state_bus_standard = Column(String(25))
    airconditioning = Column(SQLEnum(AirConditioningType), default=AirConditioningType.OTHER)
    location = Column(String(30))
    brake = Column(String(300))
    contact_email = Column(String(100))
    contact_phone = Column(String(100))
    us_region = Column(SQLEnum(USRegion), default=USRegion.OTHER)
    description = Column(Text)
    score = Column(Boolean, default=False)
    category_id = Column(Integer, default=0)

    overview = relationship("BusOverview", back_populates="bus", uselist=False)
    images = relationship("BusImage", back_populates="bus", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bus(id={self.id}, title='{self.title}', year={self.year}, make='{self.make}')>"

class BusOverview(Base):
    __tablename__ = 'buses_overview'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey('buses.id'))
    mdesc = Column(Text)
    intdesc = Column(Text)
    extdesc = Column(Text)
    features = Column(Text)
    specs = Column(Text)

    bus = relationship("Bus", back_populates="overview")

    def __repr__(self):
        return f"<BusOverview(id={self.id}, bus_id={self.bus_id})>"

class BusImage(Base):
    __tablename__ = 'buses_images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))
    url = Column(String(1000))
    description = Column(Text)
    image_index = Column(Integer, default=0)
    bus_id = Column(Integer, ForeignKey('buses.id'))

    bus = relationship("Bus", back_populates="images")

    def __repr__(self):
        return f"<BusImage(id={self.id}, name='{self.name}', bus_id={self.bus_id})>"
