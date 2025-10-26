import requests
from countries.services import CountryService

def debug_apis():
    print("Testing external APIs...")
    
    try:
        # Test countries API
        print("\n1. Testing Countries API...")
        countries_data = CountryService.fetch_countries_data()
        print(f"   ✓ Found {len(countries_data)} countries")
        
        # Check currencies for first few countries
        print("\n2. Checking currency codes for first 10 countries:")
        for i, country in enumerate(countries_data[:10]):
            currencies = country.get('currencies', [])
            currency_code = currencies[0].get('code') if currencies else None
            print(f"   {country['name']}: {currency_code}")
        
        # Test exchange rates API
        print("\n3. Testing Exchange Rates API...")
        exchange_rates = CountryService.fetch_exchange_rates()
        print(f"   ✓ Found {len(exchange_rates)} exchange rates")
        
        # Check some common currencies
        common_currencies = ['USD', 'EUR', 'GBP', 'NGN', 'CAD', 'AUD']
        print("\n4. Checking common currency rates:")
        for currency in common_currencies:
            rate = exchange_rates.get(currency)
            print(f"   {currency}: {rate}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_apis()