import requests
from django.core.management.base import BaseCommand
from countries.models import Country
from countries.services import fetch_exchange_rates  # Your existing service

class Command(BaseCommand):
    help = 'Load countries data from REST Countries API'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading countries data...')
        
        # Your existing data loading logic from services.py
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url)
        
        if response.status_code == 200:
            countries_data = response.json()
            exchange_rates = fetch_exchange_rates()
            
            for country_data in countries_data:
                # Use your existing logic from services.py to create countries
                # This should match how you currently create Country objects
                name = country_data.get('name', {}).get('common', 'Unknown')
                
                # Create or update country
                country, created = Country.objects.update_or_create(
                    name=name,
                    defaults={
                        'population': country_data.get('population', 0),
                        'area': country_data.get('area', 0),
                        'region': country_data.get('region', ''),
                        'subregion': country_data.get('subregion', ''),
                        'capital': country_data.get('capital', [''])[0] if country_data.get('capital') else '',
                        'currencies': list(country_data.get('currencies', {}).keys()) if country_data.get('currencies') else [],
                        # Add other fields from your model
                    }
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded/updated {len(countries_data)} countries')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to fetch countries data from REST Countries API')
            )