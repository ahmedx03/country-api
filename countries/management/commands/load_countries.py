import requests
from django.core.management.base import BaseCommand
from countries.models import Country

class Command(BaseCommand):
    help = 'Load countries data from REST Countries API'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading countries data from REST Countries API...')
        
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url)
        
        if response.status_code == 200:
            countries_data = response.json()
            
            # Simple exchange rates fallback
            exchange_rates = {
                'USD': 1.0, 'EUR': 0.93, 'GBP': 0.80, 'JPY': 150.0, 
                'CAD': 1.35, 'AUD': 1.55, 'CHF': 0.88, 'CNY': 7.25,
                'INR': 83.0, 'BRL': 5.05, 'ZAR': 18.5, 'RUB': 92.0,
                'MXN': 17.0, 'SGD': 1.35, 'NZD': 1.65, 'SEK': 10.5,
                'NOK': 10.8, 'DKK': 6.95, 'TRY': 32.0, 'KRW': 1330.0
            }
            
            for country_data in countries_data:
                name = country_data.get('name', {}).get('common', 'Unknown')
                
                # Get primary currency
                currencies = list(country_data.get('currencies', {}).keys())
                primary_currency = currencies[0] if currencies else 'USD'
                
                # Calculate GDP (using your existing logic)
                population = country_data.get('population', 0)
                gdp_per_capita = 1500  # Your random range logic
                exchange_rate = exchange_rates.get(primary_currency, 1.0)
                gdp = (population * gdp_per_capita) / exchange_rate
                
                # Create or update country
                Country.objects.update_or_create(
                    name=name,
                    defaults={
                        'population': population,
                        'area': country_data.get('area', 0),
                        'region': country_data.get('region', ''),
                        'subregion': country_data.get('subregion', ''),
                        'capital': country_data.get('capital', [''])[0] if country_data.get('capital') else '',
                        'currencies': currencies,
                        'languages': list(country_data.get('languages', {}).values()),
                        'borders': country_data.get('borders', []),
                        'gdp': gdp,
                    }
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded {len(countries_data)} countries')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to fetch countries data')
            )