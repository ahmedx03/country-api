from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import os
from django.conf import settings
from .models import Country
from .services import CountryService
from .image_service import SummaryImageGenerator

@api_view(['POST'])
def refresh_countries(request):
    try:
        countries_data = CountryService.fetch_countries_data()
        exchange_rates = CountryService.fetch_exchange_rates()
        
        processed_count = 0
        created_count = 0
        updated_count = 0
        error_count = 0
        error_samples = []  # Store sample errors
        
        with transaction.atomic():
            for country_data in countries_data:
                try:
                    processed_count += 1
                    
                    # Process country data
                    processed_data = CountryService.process_country_data(country_data, exchange_rates)
                    country_name = processed_data['name']
                    
                    # Show first 5 countries being processed
                    if processed_count <= 5:
                        print(f"✓ Processing {processed_count}: {country_name}")
                        print(f"  Population: {processed_data['population']}")
                        print(f"  Currency: {processed_data['currency_code']}")
                        print(f"  Exchange Rate: {processed_data['exchange_rate']}")
                    
                    # Use update_or_create
                    country, created = Country.objects.update_or_create(
                        name=country_name,
                        defaults={
                            'capital': processed_data['capital'],
                            'region': processed_data['region'],
                            'population': processed_data['population'] or 0,
                            'currency_code': processed_data['currency_code'],
                            'exchange_rate': processed_data['exchange_rate'],
                            'flag_url': processed_data['flag_url']
                        }
                    )
                    
                    if created:
                        created_count += 1
                        if created_count <= 3:
                            print(f"🎉 CREATED: {country_name}")
                    else:
                        updated_count += 1
                        if updated_count <= 3:
                            print(f"🔄 UPDATED: {country_name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"{country_data.get('name')}: {str(e)}"
                    error_samples.append(error_msg)
                    
                    # Show first 10 errors
                    if error_count <= 10:
                        print(f"❌ ERROR #{error_count}: {error_msg}")
                    continue
        
        # Generate summary image
        SummaryImageGenerator.generate_summary_image()
        
        response_data = {
            'message': 'Countries data refreshed successfully',
            'countries_processed': processed_count,
            'countries_created': created_count,
            'countries_updated': updated_count,
            'countries_with_errors': error_count,
            'total_countries_in_db': Country.objects.count(),
            'sample_errors': error_samples[:5]  # Include sample errors in response
        }
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"✅ Processed: {processed_count}")
        print(f"✅ Created: {created_count}") 
        print(f"✅ Updated: {updated_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📊 Total in DB: {Country.objects.count()}")
        
        if error_samples:
            print(f"\n=== SAMPLE ERRORS ===")
            for i, error in enumerate(error_samples[:5], 1):
                print(f"{i}. {error}")
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': 'External data source unavailable', 'details': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
                
@api_view(['GET'])
def list_countries(request):
    countries = Country.objects.all()
    
    region = request.GET.get('region')
    if region:
        countries = countries.filter(region__iexact=region)
    
    currency = request.GET.get('currency')
    if currency:
        countries = countries.filter(currency_code__iexact=currency)
    
    sort = request.GET.get('sort')
    if sort == 'gdp_desc':
        countries = countries.exclude(estimated_gdp__isnull=True).order_by('-estimated_gdp')
    elif sort == 'gdp_asc':
        countries = countries.exclude(estimated_gdp__isnull=True).order_by('estimated_gdp')
    elif sort == 'population_desc':
        countries = countries.order_by('-population')
    elif sort == 'population_asc':
        countries = countries.order_by('population')
    elif sort == 'name_desc':
        countries = countries.order_by('-name')
    else:
        countries = countries.order_by('name')
    
    data = []
    for country in countries:
        data.append({
            'id': country.id,
            'name': country.name,
            'capital': country.capital,
            'region': country.region,
            'population': country.population,
            'currency_code': country.currency_code,
            'exchange_rate': float(country.exchange_rate) if country.exchange_rate else None,
            'estimated_gdp': float(country.estimated_gdp) if country.estimated_gdp else None,
            'flag_url': country.flag_url,
            'last_refreshed_at': country.last_refreshed_at,
        })
    
    return Response(data)

@api_view(['GET'])
def get_country_by_name(request, name):
    country = get_object_or_404(Country, name__iexact=name)
    data = {
        'id': country.id,
        'name': country.name,
        'capital': country.capital,
        'region': country.region,
        'population': country.population,
        'currency_code': country.currency_code,
        'exchange_rate': float(country.exchange_rate) if country.exchange_rate else None,
        'estimated_gdp': float(country.estimated_gdp) if country.estimated_gdp else None,
        'flag_url': country.flag_url,
        'last_refreshed_at': country.last_refreshed_at,
    }
    return Response(data)

@api_view(['DELETE'])
def delete_country(request, name):
    country = get_object_or_404(Country, name__iexact=name)
    country.delete()
    return Response({'message': f'Country {name} deleted successfully'})

@api_view(['GET'])
def get_status(request):
    total_countries = Country.objects.count()
    last_country = Country.objects.order_by('-last_refreshed_at').first()
    
    status_data = {
        'total_countries': total_countries,
        'last_refreshed_at': last_country.last_refreshed_at if last_country else None
    }
    
    return Response(status_data)

@api_view(['GET'])
def get_countries_image(request):
    """Serve the generated summary image"""
    image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
    
    print(f"Looking for image at: {image_path}")  # Debug
    print(f"Image exists: {os.path.exists(image_path)}")  # Debug
    
    if os.path.exists(image_path):
        try:
            return FileResponse(open(image_path, 'rb'), content_type='image/png')
        except Exception as e:
            print(f"Error opening image: {e}")
            return Response(
                {'error': 'Could not open image file'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        print("Image not found, generating now...")
        # Generate image on the fly if missing
        from .image_service import SummaryImageGenerator
        new_image_path = SummaryImageGenerator.generate_summary_image()
        
        if new_image_path and os.path.exists(new_image_path):
            return FileResponse(open(new_image_path, 'rb'), content_type='image/png')
        else:
            return Response(
                {'error': 'Summary image not found and could not be generated'}, 
                status=status.HTTP_404_NOT_FOUND
            )