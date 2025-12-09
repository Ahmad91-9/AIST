"""Input validation module for real estate expert system."""
import os
import json
from typing import Dict, Any, List, Tuple

# Get the base directory for resolving paths relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ValidationResult:
    """Container for validation results."""
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.cleaned_data: Dict[str, Any] = {}
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    def add_error(self, message: str):
        self.errors.append(message)
    
    def add_warning(self, message: str):
        self.warnings.append(message)


def load_rules() -> Dict:
    """Load rules configuration."""
    try:
        rules_path = os.path.join(BASE_DIR, 'rules.json')
        with open(rules_path, 'r') as f:
            return json.load(f)
    except:
        return {}


def validate_inputs(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate all input fields for the real estate expert system.
    Returns ValidationResult with errors, warnings, and cleaned data.
    """
    result = ValidationResult()
    rules = load_rules()
    defaults = rules.get('defaults', {})
    
    # Required field: area
    area = data.get('area')
    if area is None or area == '':
        result.add_error("Area (sqm) is required")
    else:
        try:
            area = float(area)
            if area <= 0:
                result.add_error("Area must be greater than 0")
            elif area < 5:
                result.add_warning("Area is very small (< 5 sqm)")
            elif area > 50000:
                result.add_warning("Area is very large (> 50,000 sqm) - please verify")
            result.cleaned_data['area'] = area
        except (ValueError, TypeError):
            result.add_error("Area must be a valid number")
    
    # Required field: property_type
    property_type = data.get('property_type', '')
    valid_types = list(rules.get('property_type_factors', {}).keys())
    if not valid_types:
        valid_types = ['house', 'flat', 'plot', 'commercial']
    
    if not property_type:
        result.add_error("Property type is required")
    elif property_type.lower() not in valid_types:
        result.add_error(f"Property type must be one of: {', '.join(valid_types)}")
    else:
        result.cleaned_data['property_type'] = property_type.lower()
    
    # Location (optional with default)
    location = data.get('location', '').strip()
    if not location:
        location = defaults.get('location', 'general')
        result.add_warning("Location not specified - using 'general' baseline")
    result.cleaned_data['location'] = location
    
    # Bedrooms (required for house/flat)
    bedrooms = data.get('bedrooms')
    prop_type = result.cleaned_data.get('property_type', '')
    if prop_type in ['house', 'flat']:
        if bedrooms is None or bedrooms == '':
            result.add_warning("Bedrooms not specified for residential property")
            result.cleaned_data['bedrooms'] = 0
        else:
            try:
                bedrooms = int(bedrooms)
                if bedrooms < 0:
                    result.add_error("Bedrooms cannot be negative")
                elif bedrooms > 20:
                    result.add_warning("Unusually high number of bedrooms (> 20)")
                result.cleaned_data['bedrooms'] = max(0, bedrooms)
            except (ValueError, TypeError):
                result.add_error("Bedrooms must be a valid integer")
    else:
        result.cleaned_data['bedrooms'] = int(bedrooms) if bedrooms else 0
    
    # Bathrooms (required for house/flat)
    bathrooms = data.get('bathrooms')
    if prop_type in ['house', 'flat']:
        if bathrooms is None or bathrooms == '':
            result.add_warning("Bathrooms not specified for residential property")
            result.cleaned_data['bathrooms'] = 0
        else:
            try:
                bathrooms = int(bathrooms)
                if bathrooms < 0:
                    result.add_error("Bathrooms cannot be negative")
                elif bathrooms > 15:
                    result.add_warning("Unusually high number of bathrooms (> 15)")
                result.cleaned_data['bathrooms'] = max(0, bathrooms)
            except (ValueError, TypeError):
                result.add_error("Bathrooms must be a valid integer")
    else:
        result.cleaned_data['bathrooms'] = int(bathrooms) if bathrooms else 0
    
    # Condition (optional with default)
    condition = data.get('condition', '')
    valid_conditions = list(rules.get('condition_factors', {}).keys())
    if not valid_conditions:
        valid_conditions = ['new', 'like_new', 'used_good', 'needs_renovation']
    
    if not condition:
        condition = defaults.get('condition', 'used_good')
    elif condition.lower() not in valid_conditions:
        result.add_warning(f"Unknown condition '{condition}' - using 'used_good'")
        condition = 'used_good'
    result.cleaned_data['condition'] = condition.lower()
    
    # Age (optional with default)
    age = data.get('age')
    if age is None or age == '':
        age = defaults.get('age', 10)
    else:
        try:
            age = int(age)
            if age < 0:
                result.add_error("Age cannot be negative")
                age = 0
            elif age > 200:
                result.add_warning("Property age > 200 years - please verify")
        except (ValueError, TypeError):
            result.add_warning("Invalid age - using default")
            age = defaults.get('age', 10)
    result.cleaned_data['age'] = age
    
    # Floor (optional, relevant for flats)
    floor = data.get('floor')
    if floor is None or floor == '':
        floor = defaults.get('floor', 1)
    else:
        try:
            floor = int(floor)
            if floor < -5:
                result.add_warning("Floor level below -5 is unusual")
            elif floor > 200:
                result.add_warning("Floor level > 200 is unusual")
        except (ValueError, TypeError):
            floor = defaults.get('floor', 1)
    result.cleaned_data['floor'] = floor
    
    # Parking (optional with default)
    parking = data.get('parking', '')
    valid_parking = list(rules.get('parking_factors', {}).keys())
    if not valid_parking:
        valid_parking = ['none', 'street', 'covered', 'garage']
    
    if not parking:
        parking = defaults.get('parking', 'none')
    elif parking.lower() not in valid_parking:
        result.add_warning(f"Unknown parking type '{parking}' - using 'none'")
        parking = 'none'
    result.cleaned_data['parking'] = parking.lower()
    
    # Amenities score (0-5)
    amenities_score = data.get('amenities_score')
    if amenities_score is None or amenities_score == '':
        amenities_score = defaults.get('amenities_score', 3)
    else:
        try:
            amenities_score = float(amenities_score)
            if amenities_score < 0:
                amenities_score = 0
            elif amenities_score > 5:
                amenities_score = 5
        except (ValueError, TypeError):
            amenities_score = defaults.get('amenities_score', 3)
    result.cleaned_data['amenities_score'] = amenities_score
    
    # Demand score (0-5)
    demand_score = data.get('demand_score')
    if demand_score is None or demand_score == '':
        demand_score = defaults.get('demand_score', 3)
    else:
        try:
            demand_score = float(demand_score)
            if demand_score < 0:
                demand_score = 0
            elif demand_score > 5:
                demand_score = 5
        except (ValueError, TypeError):
            demand_score = defaults.get('demand_score', 3)
    result.cleaned_data['demand_score'] = demand_score
    
    # Occupancy rate (0-1)
    occupancy_rate = data.get('occupancy_rate')
    if occupancy_rate is None or occupancy_rate == '':
        occupancy_rate = defaults.get('occupancy_rate', 0.9)
    else:
        try:
            occupancy_rate = float(occupancy_rate)
            if occupancy_rate > 1:
                occupancy_rate = occupancy_rate / 100.0
            if occupancy_rate < 0:
                occupancy_rate = 0
            elif occupancy_rate > 1:
                occupancy_rate = 1
        except (ValueError, TypeError):
            occupancy_rate = defaults.get('occupancy_rate', 0.9)
    result.cleaned_data['occupancy_rate'] = occupancy_rate
    
    # Market appreciation score
    market_appreciation = data.get('market_appreciation_score')
    if market_appreciation is None or market_appreciation == '':
        market_appreciation = defaults.get('market_appreciation_score', 0.03)
    else:
        try:
            market_appreciation = float(market_appreciation)
            if market_appreciation < -0.5:
                market_appreciation = -0.5
            elif market_appreciation > 0.5:
                market_appreciation = 0.5
        except (ValueError, TypeError):
            market_appreciation = defaults.get('market_appreciation_score', 0.03)
    result.cleaned_data['market_appreciation_score'] = market_appreciation
    
    # Crime index (0-1)
    crime_index = data.get('crime_index')
    if crime_index is None or crime_index == '':
        crime_index = defaults.get('crime_index', 0.05)
    else:
        try:
            crime_index = float(crime_index)
            if crime_index < 0:
                crime_index = 0
            elif crime_index > 1:
                crime_index = 1
        except (ValueError, TypeError):
            crime_index = defaults.get('crime_index', 0.05)
    result.cleaned_data['crime_index'] = crime_index
    
    # Market volatility (0-1)
    market_volatility = data.get('market_volatility')
    if market_volatility is None or market_volatility == '':
        market_volatility = defaults.get('market_volatility', 0.1)
    else:
        try:
            market_volatility = float(market_volatility)
            if market_volatility < 0:
                market_volatility = 0
            elif market_volatility > 1:
                market_volatility = 1
        except (ValueError, TypeError):
            market_volatility = defaults.get('market_volatility', 0.1)
    result.cleaned_data['market_volatility'] = market_volatility
    
    # Economic index (0-1)
    economic_index = data.get('economic_index')
    if economic_index is None or economic_index == '':
        economic_index = defaults.get('economic_index', 0.5)
    else:
        try:
            economic_index = float(economic_index)
            if economic_index < 0:
                economic_index = 0
            elif economic_index > 1:
                economic_index = 1
        except (ValueError, TypeError):
            economic_index = defaults.get('economic_index', 0.5)
    result.cleaned_data['economic_index'] = economic_index
    
    # Development index (0-1)
    development_index = data.get('development_index')
    if development_index is None or development_index == '':
        development_index = defaults.get('development_index', 0.0)
    else:
        try:
            development_index = float(development_index)
            if development_index < 0:
                development_index = 0
            elif development_index > 1:
                development_index = 1
        except (ValueError, TypeError):
            development_index = defaults.get('development_index', 0.0)
    result.cleaned_data['development_index'] = development_index
    
    # Purchase price (optional)
    purchase_price = data.get('purchase_price')
    if purchase_price is not None and purchase_price != '':
        try:
            purchase_price = float(purchase_price)
            if purchase_price <= 0:
                result.add_warning("Purchase price should be positive")
            result.cleaned_data['purchase_price'] = purchase_price
        except (ValueError, TypeError):
            result.add_warning("Invalid purchase price - ignoring")
    
    # Current price (optional)
    current_price = data.get('current_price')
    if current_price is not None and current_price != '':
        try:
            current_price = float(current_price)
            if current_price <= 0:
                result.add_warning("Current price should be positive")
            result.cleaned_data['current_price'] = current_price
        except (ValueError, TypeError):
            result.add_warning("Invalid current price - ignoring")
    
    # Annual rent (optional)
    annual_rent = data.get('annual_rent')
    if annual_rent is not None and annual_rent != '':
        try:
            annual_rent = float(annual_rent)
            if annual_rent < 0:
                result.add_warning("Annual rent cannot be negative")
            result.cleaned_data['annual_rent'] = annual_rent
        except (ValueError, TypeError):
            result.add_warning("Invalid annual rent - ignoring")
    
    # Expenses (optional)
    expenses = data.get('expenses')
    if expenses is not None and expenses != '':
        try:
            expenses = float(expenses)
            if expenses < 0:
                result.add_warning("Expenses cannot be negative")
            result.cleaned_data['expenses'] = expenses
        except (ValueError, TypeError):
            pass
    
    # Cross-field validations
    if 'current_price' in result.cleaned_data and 'purchase_price' in result.cleaned_data:
        if result.cleaned_data['current_price'] < result.cleaned_data['purchase_price']:
            result.add_warning("Current price is less than purchase price - potential loss")
    
    return result
