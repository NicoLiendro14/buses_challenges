from .models import Bus, BusOverview, BusImage, AirConditioningType, USRegion
from .db_connector import db, DatabaseConnector

__all__ = [
    'Bus',
    'BusOverview',
    'BusImage',
    'AirConditioningType',
    'USRegion',
    'db',
    'DatabaseConnector'
]

# Exponer create_tables como una función conveniente
def create_tables():
    """Create all tables in the database."""
    db.create_tables()
