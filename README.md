# Country Currency & Exchange API

A Django REST API for managing country data with currency exchange rates and GDP calculations.

## Features

- **250 Countries** with real-time data synchronization
- **GDP Calculations** using population and exchange rates
- **RESTful Endpoints** with filtering and sorting
- **Image Generation** for summary reports
- **External API Integration** (REST Countries + Exchange Rates)

## Quick Start

```bash
# Setup
git clone <repo>
cd country-api
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Database
python manage.py migrate
python manage.py setup_countries

# Run
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/countries/refresh` | Sync with external APIs |
| `GET` | `/countries` | List countries (supports filters) |
| `GET` | `/countries/{name}` | Get specific country |
| `GET` | `/status` | API statistics |
| `GET` | `/countries/image` | Summary image |

### Query Parameters
- `region=Africa` - Filter by region
- `currency=USD` - Filter by currency
- `sort=gdp_desc` - Sort by GDP descending

## Usage Examples

```bash
# Refresh data
curl -X POST http://localhost:8000/countries/refresh

# List African countries sorted by GDP
curl "http://localhost:8000/countries?region=Africa&sort=gdp_desc"

# Get specific country
curl "http://localhost:8000/countries/United%20States%20of%20America"

# Generate summary image
curl http://localhost:8000/countries/image -o summary.png
```

## Response Format

```json
{
  "id": 1,
  "name": "United States of America",
  "capital": "Washington, D.C.",
  "region": "Americas", 
  "population": 329484123,
  "currency_code": "USD",
  "exchange_rate": 1.0,
  "estimated_gdp": 463333608865.67,
  "flag_url": "https://flagcdn.com/us.svg",
  "last_refreshed_at": "2025-10-25T22:45:50.432979Z"
}
```

## Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Database**: SQLite (production: PostgreSQL/MySQL)
- **Image Processing**: Pillow
- **External APIs**: REST Countries, Exchange Rate API

## Deployment

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-production-key
ALLOWED_HOSTS=your-domain.com
```

### Supported Platforms
- Railway

## Data Sources

- **Country Data**: https://restcountries.com/v2/all
- **Exchange Rates**: https://open.er-api.com/v6/latest/USD

## Error Handling

Standard JSON error responses with appropriate HTTP status codes:
- `400` - Validation errors
- `404` - Resource not found
- `503` - External API unavailable

---

**Production Ready | Django REST Framework**