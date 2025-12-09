"""Rule-based valuation engine for real estate expert system."""
import json
from typing import Dict, Any, List, Tuple


class ValuationTrace:
    """Track all rule applications for transparency."""
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self.base_price: float = 0
        self.final_price: float = 0
    
    def add_step(self, rule: str, factor: float, value_before: float, value_after: float, reason: str):
        delta_pct = ((value_after - value_before) / value_before * 100) if value_before > 0 else 0
        self.steps.append({
            'rule': rule,
            'factor': factor,
            'delta_pct': delta_pct,
            'value_before': value_before,
            'value_after': value_after,
            'reason': reason
        })
    
    def to_dict(self) -> Dict:
        return {
            'base_price': self.base_price,
            'final_price': self.final_price,
            'steps': self.steps,
            'total_adjustments': len(self.steps)
        }


class RuleEngine:
    """Rule-based property valuation engine."""
    
    def __init__(self, rules_path: str = 'rules.json'):
        self.rules = self._load_rules(rules_path)
    
    def _load_rules(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        return {
            "location_base_rates": {"premium": 5000, "urban_center": 4000, "suburban": 3000, "rural": 2000, "general": 3000},
            "property_type_factors": {"house": 1.05, "flat": 1.0, "plot": 0.6, "commercial": 1.25},
            "condition_factors": {"new": 1.15, "like_new": 1.05, "used_good": 1.0, "needs_renovation": 0.8},
            "parking_factors": {"none": 1.0, "street": 0.98, "covered": 1.03, "garage": 1.06},
            "age_depreciation": {"rate_per_year": 0.005, "min_factor": 0.6},
            "amenities": {"base_score": 3, "per_point_adjustment": 0.03},
            "demand": {"base_score": 3, "per_point_adjustment": 0.04},
            "crime": {"weight": 0.6},
            "volatility": {"threshold": 0.2, "max_penalty": 0.12, "weight": 0.4},
            "development": {"uplift_weight": 0.06},
            "price_clamp": {"max_multiplier": 1.7, "min_multiplier": 0.4},
            "rent_yields": {"high_demand": 0.08, "medium_demand": 0.05, "low_demand": 0.03},
            "floor_adjustments": {"ground_commercial_bonus": 0.05, "per_floor_bonus": 0.01, "max_floor_bonus": 0.10}
        }
    
    def evaluate(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate property using rule-based system.
        Returns expert price, rent estimate, ROI, risk score, and trace.
        """
        trace = ValuationTrace()
        
        # Get location base rate
        location = features.get('location', 'general').lower()
        location_rates = self.rules.get('location_base_rates', {})
        base_rate = location_rates.get(location, location_rates.get('general', 3000))
        
        # Property type factor
        property_type = features.get('property_type', 'flat').lower()
        type_factors = self.rules.get('property_type_factors', {})
        type_factor = type_factors.get(property_type, 1.0)
        
        # Age depreciation
        age = features.get('age', 10)
        age_config = self.rules.get('age_depreciation', {})
        age_rate = age_config.get('rate_per_year', 0.005)
        min_age_factor = age_config.get('min_factor', 0.6)
        age_factor = max(1 - age * age_rate, min_age_factor)
        
        # Condition factor
        condition = features.get('condition', 'used_good').lower()
        condition_factors = self.rules.get('condition_factors', {})
        condition_factor = condition_factors.get(condition, 1.0)
        
        # Calculate base price per sqm
        base_price_per_sqm = base_rate * type_factor * age_factor * condition_factor
        
        # Calculate base price
        area = features.get('area', 100)
        base_price = base_price_per_sqm * area
        trace.base_price = base_price
        
        current_price = base_price
        
        # Apply floor adjustment
        floor = features.get('floor', 1)
        floor_config = self.rules.get('floor_adjustments', {})
        if property_type == 'commercial' and floor == 0:
            floor_factor = 1 + floor_config.get('ground_commercial_bonus', 0.05)
        else:
            per_floor = floor_config.get('per_floor_bonus', 0.01)
            max_bonus = floor_config.get('max_floor_bonus', 0.10)
            floor_factor = 1 + min(floor * per_floor, max_bonus)
        
        old_price = current_price
        current_price *= floor_factor
        trace.add_step('floor_adjustment', floor_factor, old_price, current_price, 
                      f"Floor {floor} adjustment")
        
        # Apply parking factor
        parking = features.get('parking', 'none').lower()
        parking_factors = self.rules.get('parking_factors', {})
        parking_factor = parking_factors.get(parking, 1.0)
        
        old_price = current_price
        current_price *= parking_factor
        trace.add_step('parking', parking_factor, old_price, current_price,
                      f"Parking type: {parking}")
        
        # Amenities adjustment
        amenities_score = features.get('amenities_score', 3)
        amenities_config = self.rules.get('amenities', {})
        base_amenities = amenities_config.get('base_score', 3)
        amenities_adj = amenities_config.get('per_point_adjustment', 0.03)
        amenities_factor = 1 + (amenities_score - base_amenities) * amenities_adj
        
        old_price = current_price
        current_price *= amenities_factor
        trace.add_step('amenities', amenities_factor, old_price, current_price,
                      f"Amenities score: {amenities_score}/5")
        
        # Demand adjustment
        demand_score = features.get('demand_score', 3)
        demand_config = self.rules.get('demand', {})
        base_demand = demand_config.get('base_score', 3)
        demand_adj = demand_config.get('per_point_adjustment', 0.04)
        demand_factor = 1 + (demand_score - base_demand) * demand_adj
        
        old_price = current_price
        current_price *= demand_factor
        trace.add_step('demand', demand_factor, old_price, current_price,
                      f"Market demand score: {demand_score}/5")
        
        # Market appreciation adjustment
        appreciation = features.get('market_appreciation_score', 0.03)
        appreciation_factor = 1 + appreciation
        
        old_price = current_price
        current_price *= appreciation_factor
        trace.add_step('appreciation', appreciation_factor, old_price, current_price,
                      f"Market appreciation: {appreciation*100:.1f}%")
        
        # Crime penalty
        crime_index = features.get('crime_index', 0.05)
        crime_weight = self.rules.get('crime', {}).get('weight', 0.6)
        crime_factor = 1 - crime_index * crime_weight
        
        old_price = current_price
        current_price *= crime_factor
        trace.add_step('crime_penalty', crime_factor, old_price, current_price,
                      f"Crime index: {crime_index*100:.0f}%")
        
        # Volatility penalty
        volatility = features.get('market_volatility', 0.1)
        vol_config = self.rules.get('volatility', {})
        vol_threshold = vol_config.get('threshold', 0.2)
        vol_max_penalty = vol_config.get('max_penalty', 0.12)
        vol_weight = vol_config.get('weight', 0.4)
        
        if volatility > vol_threshold:
            vol_factor = 1 - min(vol_max_penalty, volatility * vol_weight)
        else:
            vol_factor = 1.0
        
        old_price = current_price
        current_price *= vol_factor
        trace.add_step('volatility', vol_factor, old_price, current_price,
                      f"Market volatility: {volatility*100:.0f}%")
        
        # Development uplift
        development_index = features.get('development_index', 0.0)
        dev_weight = self.rules.get('development', {}).get('uplift_weight', 0.06)
        dev_factor = 1 + development_index * dev_weight
        
        old_price = current_price
        current_price *= dev_factor
        trace.add_step('development', dev_factor, old_price, current_price,
                      f"Development index: {development_index*100:.0f}%")
        
        # Apply price clamps
        clamp_config = self.rules.get('price_clamp', {})
        max_mult = clamp_config.get('max_multiplier', 1.7)
        min_mult = clamp_config.get('min_multiplier', 0.4)
        
        final_price = max(min(current_price, base_price * max_mult), base_price * min_mult)
        trace.final_price = final_price
        
        if final_price != current_price:
            trace.add_step('price_clamp', final_price / current_price, current_price, final_price,
                          f"Price clamped to {min_mult*100:.0f}%-{max_mult*100:.0f}% of base")
        
        # Calculate rent estimate
        rent_yields = self.rules.get('rent_yields', {})
        if demand_score >= 4:
            rent_yield = rent_yields.get('high_demand', 0.08)
        elif demand_score >= 2:
            rent_yield = rent_yields.get('medium_demand', 0.05)
        else:
            rent_yield = rent_yields.get('low_demand', 0.03)
        
        estimated_annual_rent = final_price * rent_yield
        
        # Calculate ROI
        occupancy_rate = features.get('occupancy_rate', 0.9)
        annual_rent = features.get('annual_rent', estimated_annual_rent)
        expenses = features.get('expenses', annual_rent * 0.1)
        purchase_price = features.get('purchase_price', final_price)
        
        if purchase_price > 0:
            roi = (annual_rent * occupancy_rate - expenses) / purchase_price
        else:
            roi = 0.0
        
        # Calculate risk score (0-1, lower is better)
        risk_score = self._calculate_risk_score(features)
        
        # Calculate future price estimates
        future_1yr = final_price * (1 + appreciation) * (1 - volatility * 0.3)
        future_3yr = final_price * ((1 + appreciation) ** 3) * (1 - volatility * 0.5)
        
        return {
            'expert_price': round(final_price, 2),
            'base_price': round(base_price, 2),
            'estimated_rent': round(estimated_annual_rent, 2),
            'roi': round(roi * 100, 2),
            'risk_score': round(risk_score, 2),
            'future_price_1yr': round(future_1yr, 2),
            'future_price_3yr': round(future_3yr, 2),
            'price_per_sqm': round(final_price / area, 2) if area > 0 else 0,
            'trace': trace.to_dict()
        }
    
    def _calculate_risk_score(self, features: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-1, higher = more risk)."""
        risk = 0.0
        
        # Crime contributes to risk
        risk += features.get('crime_index', 0.05) * 0.25
        
        # Volatility contributes to risk
        risk += features.get('market_volatility', 0.1) * 0.25
        
        # Low economic index increases risk
        economic = features.get('economic_index', 0.5)
        risk += (1 - economic) * 0.2
        
        # Property condition affects risk
        condition = features.get('condition', 'used_good')
        condition_risk = {'new': 0.0, 'like_new': 0.05, 'used_good': 0.1, 'needs_renovation': 0.25}
        risk += condition_risk.get(condition, 0.1)
        
        # Age affects risk
        age = features.get('age', 10)
        risk += min(age * 0.002, 0.15)
        
        # Low demand increases risk
        demand = features.get('demand_score', 3)
        risk += max(0, (3 - demand) * 0.05)
        
        return min(max(risk, 0), 1)
