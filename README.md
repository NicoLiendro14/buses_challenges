# School Bus Scraping Project

## Overview
This project is a comprehensive solution for scraping, processing, and storing school bus listings data from multiple sources. It uses Python-based scrapers to extract detailed information about school buses, processes the data through validation pipelines, and stores it in a structured MySQL database.

## Data Sources
The project scrapes data from three school bus inventory sources:

### 1. Daimler Coaches North America
- URL: https://www.daimlercoachesnorthamerica.com/pre-owned-motor-coaches/
- Data Availability:
  - Title, Year, Make, Model
  - Mileage, Passengers, Wheelchair Accessibility
  - Engine, Transmission, GVWR
  - Price, VIN
  - Location and Region
  - Description, Features, Specifications
  - Images with metadata

### 2. Micro Bird - School Vehicles
- URL: https://www.microbird.com/en/school-vehicles/
- Data Availability:
  - Title, Year, Make, Model
  - Passengers, Wheelchair Accessibility
  - Engine, Transmission details
  - Technical specifications from downloadable spreadsheets
  - Images with metadata

### 3. Ross Bus - School Buses
- URL: https://www.rossbus.com/school-buses
- Data Availability:
  - Title, Make, Model
  - Passengers, Wheelchair Accessibility
  - Engine, Transmission, GVWR
  - Description, Specifications
  - Images with metadata
- Special Note:
  - Operates with an invalid SSL certificate
  - Requires navigation into individual listings for detailed information

## Project Structure
```
buses_challenge/
├── config/               # Configuration files
├── database/             # Database related code
│   ├── sql/              # SQL scripts for setup and testing
│   ├── db_connector.py   # Database connection management
│   ├── models.py         # SQLAlchemy ORM models
│   ├── processor.py      # Data validation and processing
│   └── populate_db.py    # Database population script
├── scrapers/             # Scraper implementations
│   ├── base_scraper.py   # Abstract base class for scrapers
│   ├── daimler_scraper.py
│   ├── micro_bird_scraper.py
│   ├── ross_scraper.py
│   └── pdf_mixin.py      # PDF processing utilities
├── scripts/              # Utility scripts
│   ├── run_scrapers.py   # Script to run all scrapers and save JSON output
│   └── verify_data.py    # Data verification script
├── tests/                # Test suite
├── utils/                # Shared utilities
├── .env                  # Environment variables (not committed)
├── .env.example          # Example environment file
├── requirements.txt      # Project dependencies
└── main.py               # Main entry point
```

## Requirements
- Python 3.8+
- MySQL 5.7+ / MariaDB 10.2+
- Dependencies in requirements.txt

## Installation
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/buses_challenge.git
   cd buses_challenge
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

## Configuration
Edit the `.env` file with your MySQL database credentials:
```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=school_buses
```

## Usage

### Running All Scrapers At Once
To run all three scrapers at once and save their output as JSON files:

```bash
python scripts/run_scrapers.py
```

This will:
- Run all three scrapers (Daimler, Micro Bird, Ross Bus)
- Save the results in a `scraped_data` directory with timestamped JSON files
- Generate a statistics summary file with counts and status for each scraper
- Log the execution details to `scrapers_execution.log`

### Running Individual Scrapers
Run each scraper individually to test or to scrape data from a specific source:

```bash
# Run Daimler scraper
python -m scrapers.daimler_scraper

# Run Micro Bird scraper
python -m scrapers.micro_bird_scraper

# Run Ross Bus scraper
python -m scrapers.ross_scraper
```

Each scraper will produce JSON output in the current directory with the scraped data.

### Database Setup and Integration

1. Set up the database schema:
   ```bash
   mysql -u your_username -p < database/sql/01_create_database.sql
   ```

2. (Optional) Load sample data for testing:
   ```bash
   mysql -u your_username -p < database/sql/02_sample_data.sql
   ```

3. Run the database population script to scrape and store data:
   ```bash
   python database/populate_db.py
   ```

4. Generate a database dump for verification:
   ```bash
   chmod +x database/sql/03_generate_dump.sh
   ./database/sql/03_generate_dump.sh
   ```

## Testing

### Testing Scrapers
Run unit tests for the scrapers:
```bash
pytest tests/test_daimler_scraper.py
pytest tests/test_micro_bird_scraper.py
pytest tests/test_ross_scraper.py
```

### Testing Database Integration
1. Ensure your database is set up with the schema
2. Run the verification script:
   ```bash
   python scripts/verify_data.py
   ```
   This script will:
   - Verify the data integrity in the database
   - Check for duplicate entries
   - Validate relationships between tables
   - Report on data completeness

3. Monitor logs during processing:
   - Scraper logs: check individual scraper log files (e.g., `ross_bus_scraping.log`)
   - Database logs: `database_population.log`

## Database Schema

The database schema consists of three related tables:

### 1. buses (Core Information)
Stores the primary bus listing information including make, model, price, and specs.

### 2. buses_overview (Additional Information)
Contains extended descriptions and specifications linked to each bus.

### 3. buses_images (Images)
Stores image URLs and metadata for each bus.

The schema is fully implemented in SQLAlchemy ORM models in `database/models.py` and raw SQL in `database/sql/01_create_database.sql`.

## Architecture & Design Decisions

### Scraper Design
- Each scraper inherits from a `BaseScraper` abstract class to ensure consistent interfaces
- PDF processing for Micro Bird specifications uses a dedicated mixin class
- Scrapers implement specialized parsing logic for each source website

### Data Processing Pipeline
1. Raw extraction from websites
2. Field normalization and cleaning
3. Data validation against schema requirements
4. Duplicate detection using multiple criteria
5. Database insertion with proper relationships

### Error Handling
- Robust exception handling with detailed logging
- Retry logic for network failures
- Graceful degradation when certain fields are missing

## Performance Considerations

### Scraping Performance
- Asynchronous requests where applicable for improved throughput
- Rate limiting to avoid overloading source websites
- Caching of previously visited pages

### Database Performance
- Connection pooling for efficient database access
- Batch processing for efficient database writes
- Proper indexing on frequently queried fields

## Assumptions and Limitations

### Assumptions
1. Source websites maintain their current structure
2. Required bus fields are available across at least two sources
3. MySQL/MariaDB database is available for storage

### Limitations
1. Some fields may be unavailable from certain sources
2. Image downloads are limited to URLs only, not actual files
3. PDF processing requires external dependencies
4. Ross Bus site may have intermittent availability due to SSL issues

## Future Improvements
1. Implement a scheduling system for regular updates
2. Add a web dashboard for monitoring scraping status
3. Improve image processing and download capabilities
4. Implement more advanced deduplication using fuzzy matching

---

This project was created as part of the AUTOScraping Data Engineer Challenge.
