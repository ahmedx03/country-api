import requests
from typing import Dict, List, Optional

class CountryService:
    
    @staticmethod
    def fetch_countries_data() -> List[Dict]:
        try:
            response = requests.get(
                'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies',
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Could not fetch data from countries API: {str(e)}")
    
    @staticmethod
    def fetch_exchange_rates() -> Dict:
        try:
            response = requests.get(
                'https://open.er-api.com/v6/latest/USD',
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('rates', {})
        except requests.RequestException as e:
            raise Exception(f"Could not fetch data from exchange rates API: {str(e)}")
    
    @staticmethod
    def extract_currency_code(country_data: Dict) -> Optional[str]:
        currencies = country_data.get('currencies', [])
        if currencies and len(currencies) > 0:
            return currencies[0].get('code')
        return None
    
    @staticmethod
    def process_country_data(country_data: Dict, exchange_rates: Dict) -> Dict:
        currency_code = CountryService.extract_currency_code(country_data)
        exchange_rate = exchange_rates.get(currency_code) if currency_code else None
        
        return {
            'name': country_data.get('name'),
            'capital': country_data.get('capital'),
            'region': country_data.get('region'),
            'population': country_data.get('population', 0),
            'currency_code': currency_code,
            'exchange_rate': exchange_rate,
            'flag_url': country_data.get('flag')
        }