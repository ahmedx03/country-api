from django.db import models
from django.core.exceptions import ValidationError
import random
from decimal import Decimal, ROUND_HALF_UP

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capital = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    population = models.BigIntegerField(default=0)
    currency_code = models.CharField(max_length=10, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True)
    estimated_gdp = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    flag_url = models.URLField(blank=True, null=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'countries'
        ordering = ['name']
    
    def clean(self):
        errors = {}
        if not self.name:
            errors['name'] = 'Name is required'
        if self.population is None:
            errors['population'] = 'Population is required'
        if errors:
            raise ValidationError(errors)
    
    def calculate_estimated_gdp(self):
        """Calculate estimated GDP with proper decimal handling"""
        if self.population and self.exchange_rate:
            try:
                random_multiplier = random.uniform(1000, 2000)
                gdp = (self.population * random_multiplier) / float(self.exchange_rate)
                
                # Round to 2 decimal places properly
                gdp_decimal = Decimal(str(gdp))
                gdp_rounded = gdp_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                return gdp_rounded
            except (TypeError, ZeroDivisionError, ValueError):
                return None
        return None
    
    def save(self, *args, **kwargs):
        # Ensure population has a value
        if self.population is None:
            self.population = 0
            
        # Round exchange_rate to 6 decimal places if it exists
        if self.exchange_rate is not None:
            try:
                exchange_decimal = Decimal(str(self.exchange_rate))
                self.exchange_rate = exchange_decimal.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
            except (TypeError, ValueError):
                self.exchange_rate = None
            
        # Calculate estimated GDP
        self.estimated_gdp = self.calculate_estimated_gdp()
        
        # Round estimated_gdp to 2 decimal places if it exists
        if self.estimated_gdp is not None:
            try:
                gdp_decimal = Decimal(str(self.estimated_gdp))
                self.estimated_gdp = gdp_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except (TypeError, ValueError):
                self.estimated_gdp = None
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name