# Car Scraper Backend

This is a FastAPI application for scraping car listings from eBay. It provides endpoints to create and retrieve car listings.

## Features

- Create new car listings
- Retrieve car listings
- Validate data using Pydantic models

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd car_scraper_backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

Replace `app.main:app` with the appropriate path to your FastAPI app instance.

## API Endpoints

### Create Listing

- **Endpoint:** `/listings`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "title": "Car Title",
    "vin": "VIN123456789",
    "make": "Car Make",
    "model": "Car Model",
    "year": 2020,
    "mileage": 15000,
    "price": 20000,
    "location": "Location",
    "contact_info": "Contact Info",
    "image_url": "http://example.com/image.jpg",
    "listing_url": "http://example.com/listing"
  }
  ```

### Get Listings

- **Endpoint:** `/listings`
- **Method:** `GET`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI
- Pydantic
- Uvicorn