from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from .models import Country

class SummaryImageGenerator:
    
    @staticmethod
    def generate_summary_image():
        """Generate and save summary image"""
        try:
            print("=== IMAGE GENERATION STARTED ===")
            
            # Get data for image
            total_countries = Country.objects.count()
            print(f"Total countries: {total_countries}")
            
            top_countries = Country.objects.exclude(estimated_gdp__isnull=True).order_by('-estimated_gdp')[:5]
            print(f"Top countries found: {top_countries.count()}")
            
            last_country = Country.objects.order_by('-last_refreshed_at').first()
            print(f"Last country: {last_country}")
            
            # Create image
            img_width, img_height = 600, 400
            image = Image.new('RGB', (img_width, img_height), color=(240, 240, 240))
            draw = ImageDraw.Draw(image)
            
            # Try to use fonts (fallback to default if not available)
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_medium = ImageFont.truetype("arial.ttf", 18)
                font_small = ImageFont.truetype("arial.ttf", 14)
                print("Using Arial font")
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
                print("Using default font")
            
            # Draw title with background
            draw.rectangle([0, 0, img_width, 50], fill=(70, 130, 180))
            draw.text((20, 15), "Countries Summary", fill='white', font=font_large)
            
            # Draw total countries
            draw.text((20, 70), f"Total Countries: {total_countries}", fill='black', font=font_medium)
            
            # Draw top 5 countries by GDP
            draw.text((20, 110), "Top 5 Countries by Estimated GDP:", fill='black', font=font_medium)
            
            y_position = 140
            for i, country in enumerate(top_countries, 1):
                gdp_str = f"${country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
                text = f"{i}. {country.name}: {gdp_str}"
                draw.text((40, y_position), text, fill=(0, 100, 0), font=font_small)
                y_position += 25
                print(f"Added country to image: {country.name}")
            
            # Draw last refresh time
            if last_country:
                refresh_time = last_country.last_refreshed_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                draw.text((20, y_position + 20), f"Last Updated: {refresh_time}", fill='gray', font=font_small)
            
            # Add border
            draw.rectangle([0, 0, img_width-1, img_height-1], outline='gray', width=2)
            
            # Save image
            image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
            print(f"Saving image to: {image_path}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            image.save(image_path)
            print("=== IMAGE GENERATION COMPLETED SUCCESSFULLY ===")
            
            return image_path
            
        except Exception as e:
            print(f"=== IMAGE GENERATION FAILED: {e} ===")
            import traceback
            print(f"Error details: {traceback.format_exc()}")
            return None