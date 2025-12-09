"""ML Model Manager with confidence scoring and blending logic."""
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import numpy as np

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


class MLModelManager:
    """Manages ML models with confidence scoring and blending."""
    
    MODEL_NAMES = ['price', 'rent', 'roi', 'risk', 'future_price_1yr', 'future_price_3yr']
    
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.models: Dict[str, Any] = {}
        self.model_meta: Dict[str, Dict] = {}
        self.feature_stats: Dict[str, Dict] = {}
        self._load_models()
    
    def _load_models(self):
        """Load all available ML models."""
        if not JOBLIB_AVAILABLE:
            return
        
        for name in self.MODEL_NAMES:
            model_path = os.path.join(self.models_dir, f'{name}_model.pkl')
            if os.path.exists(model_path):
                try:
                    self.models[name] = joblib.load(model_path)
                    self.model_meta[name] = {
                        'name': name,
                        'path': model_path,
                        'hash': self._get_file_hash(model_path),
                        'loaded_at': datetime.now().isoformat(),
                        'available': True
                    }
                except Exception as e:
                    self.model_meta[name] = {
                        'name': name,
                        'available': False,
                        'error': str(e)
                    }
            else:
                self.model_meta[name] = {
                    'name': name,
                    'available': False,
                    'error': 'Model file not found'
                }
    
    def _get_file_hash(self, path: str) -> str:
        """Get MD5 hash of a file."""
        try:
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()[:8]
        except:
            return 'unknown'
    
    def get_model_status(self) -> Dict[str, Dict]:
        """Get status of all models."""
        return self.model_meta.copy()
    
    def predict_with_confidence(self, model_name: str, features: Dict[str, Any]) -> Tuple[Optional[float], float]:
        """
        Make prediction with confidence score.
        Returns (prediction, confidence) tuple.
        If model unavailable, returns (None, 0.0).
        """
        if model_name not in self.models:
            return None, 0.0
        
        model = self.models[model_name]
        
        try:
            # Prepare feature vector
            feature_vector = self._prepare_features(features)
            
            # Make prediction
            prediction = model.predict(feature_vector.reshape(1, -1))[0]
            
            # Calculate pseudo-confidence
            confidence = self._calculate_confidence(model_name, feature_vector)
            
            return float(prediction), confidence
        except Exception as e:
            self.model_meta[model_name]['last_error'] = str(e)
            return None, 0.0
    
    def _prepare_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for ML model."""
        # Standard feature order for the models
        feature_list = [
            features.get('area', 100),
            self._encode_property_type(features.get('property_type', 'flat')),
            features.get('bedrooms', 2),
            features.get('bathrooms', 1),
            self._encode_condition(features.get('condition', 'used_good')),
            features.get('age', 10),
            features.get('floor', 1),
            self._encode_parking(features.get('parking', 'none')),
            features.get('amenities_score', 3),
            features.get('demand_score', 3),
            features.get('occupancy_rate', 0.9),
            features.get('market_appreciation_score', 0.03),
            features.get('crime_index', 0.05),
            features.get('market_volatility', 0.1),
            features.get('economic_index', 0.5),
            features.get('development_index', 0.0),
            self._encode_location(features.get('location', 'general'))
        ]
        
        return np.array(feature_list, dtype=np.float64)
    
    def _encode_property_type(self, prop_type: str) -> float:
        """Encode property type to numeric."""
        mapping = {'house': 0, 'flat': 1, 'plot': 2, 'commercial': 3}
        return mapping.get(prop_type.lower(), 1)
    
    def _encode_condition(self, condition: str) -> float:
        """Encode condition to numeric."""
        mapping = {'new': 3, 'like_new': 2, 'used_good': 1, 'needs_renovation': 0}
        return mapping.get(condition.lower(), 1)
    
    def _encode_parking(self, parking: str) -> float:
        """Encode parking type to numeric."""
        mapping = {'none': 0, 'street': 1, 'covered': 2, 'garage': 3}
        return mapping.get(parking.lower(), 0)
    
    def _encode_location(self, location: str) -> float:
        """Encode location to numeric."""
        mapping = {'rural': 0, 'suburban': 1, 'general': 2, 'urban_center': 3, 'premium': 4}
        return mapping.get(location.lower(), 2)
    
    def _calculate_confidence(self, model_name: str, features: np.ndarray) -> float:
        """
        Calculate pseudo-confidence based on feature distribution.
        Uses a simple heuristic based on feature normality.
        """
        # Simple confidence heuristic based on feature ranges
        # In production, would use actual training data statistics
        
        # Check if features are within expected ranges
        expected_ranges = [
            (5, 50000),    # area
            (0, 3),        # property_type
            (0, 10),       # bedrooms
            (0, 10),       # bathrooms
            (0, 3),        # condition
            (0, 200),      # age
            (-5, 100),     # floor
            (0, 3),        # parking
            (0, 5),        # amenities
            (0, 5),        # demand
            (0, 1),        # occupancy
            (-0.5, 0.5),   # appreciation
            (0, 1),        # crime
            (0, 1),        # volatility
            (0, 1),        # economic
            (0, 1),        # development
            (0, 4)         # location
        ]
        
        in_range_count = 0
        for i, (min_val, max_val) in enumerate(expected_ranges):
            if i < len(features):
                if min_val <= features[i] <= max_val:
                    in_range_count += 1
        
        base_confidence = in_range_count / len(expected_ranges)
        
        # Add some randomness to simulate model uncertainty
        # In production, would use actual model uncertainty estimates
        confidence = base_confidence * 0.85 + 0.1
        
        return min(max(confidence, 0.1), 0.95)
    
    def predict_all(self, features: Dict[str, Any]) -> Dict[str, Dict]:
        """Make predictions for all available models."""
        results = {}
        
        for model_name in self.MODEL_NAMES:
            prediction, confidence = self.predict_with_confidence(model_name, features)
            results[model_name] = {
                'prediction': prediction,
                'confidence': confidence,
                'available': prediction is not None,
                'model_meta': self.model_meta.get(model_name, {})
            }
        
        return results


def blend_predictions(expert_value: float, ml_value: Optional[float], ml_confidence: float) -> Tuple[float, Dict]:
    """
    Blend expert and ML predictions using confidence-weighted average.
    
    Args:
        expert_value: Value from rule-based expert system
        ml_value: Value from ML model (None if unavailable)
        ml_confidence: Confidence score from ML model (0-1)
    
    Returns:
        (blended_value, blend_info) tuple
    """
    # Handle None or invalid ML values
    if ml_value is None:
        return expert_value, {
            'method': 'expert_only',
            'expert_weight': 1.0,
            'ml_weight': 0.0,
            'ml_confidence': 0.0,
            'reason': 'ML prediction unavailable',
            'expert_value': expert_value,
            'ml_value': None
        }
    
    # Handle invalid confidence (force lower bound)
    ml_confidence = max(0.0, min(float(ml_confidence), 0.95))
    
    if ml_confidence <= 0.05:
        # Very low confidence - use expert only
        return expert_value, {
            'method': 'expert_only',
            'expert_weight': 1.0,
            'ml_weight': 0.0,
            'ml_confidence': ml_confidence,
            'reason': 'ML confidence too low',
            'expert_value': expert_value,
            'ml_value': ml_value
        }
    
    w_ml = ml_confidence
    w_expert = 1 - w_ml
    
    blended = w_ml * ml_value + w_expert * expert_value
    
    # Check for large discrepancy
    if expert_value > 0 and abs(ml_value - expert_value) / expert_value > 0.3 and ml_confidence < 0.6:
        # Large difference with low confidence - prefer expert
        blended = expert_value
        method = 'expert_preferred'
        reason = 'Large ML-expert discrepancy with low ML confidence'
        w_ml = 0.0
        w_expert = 1.0
    else:
        method = 'confidence_weighted'
        reason = f'Blended with {w_ml*100:.0f}% ML weight'
    
    return blended, {
        'method': method,
        'expert_weight': w_expert,
        'ml_weight': w_ml,
        'ml_confidence': ml_confidence,
        'reason': reason,
        'expert_value': expert_value,
        'ml_value': ml_value
    }


def generate_synthetic_ml_predictions(expert_result: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Generate synthetic ML predictions when no models are available.
    Adds realistic variation to expert predictions for demonstration.
    """
    import random
    random.seed(hash(str(features.get('area', 0))) % 2**32)
    
    results = {}
    
    # Price prediction with variation
    expert_price = expert_result.get('expert_price', 300000)
    ml_price_variation = random.uniform(-0.15, 0.15)
    ml_price = expert_price * (1 + ml_price_variation)
    results['price'] = {
        'prediction': round(ml_price, 2),
        'confidence': random.uniform(0.65, 0.90),
        'available': True,
        'synthetic': True
    }
    
    # Rent prediction
    expert_rent = expert_result.get('estimated_rent', 15000)
    ml_rent_variation = random.uniform(-0.12, 0.12)
    ml_rent = expert_rent * (1 + ml_rent_variation)
    results['rent'] = {
        'prediction': round(ml_rent, 2),
        'confidence': random.uniform(0.60, 0.85),
        'available': True,
        'synthetic': True
    }
    
    # ROI prediction
    expert_roi = expert_result.get('roi', 5.0)
    ml_roi_variation = random.uniform(-1.5, 1.5)
    ml_roi = max(0, expert_roi + ml_roi_variation)
    results['roi'] = {
        'prediction': round(ml_roi, 2),
        'confidence': random.uniform(0.55, 0.80),
        'available': True,
        'synthetic': True
    }
    
    # Risk prediction
    expert_risk = expert_result.get('risk_score', 0.3)
    ml_risk_variation = random.uniform(-0.1, 0.1)
    ml_risk = max(0, min(1, expert_risk + ml_risk_variation))
    results['risk'] = {
        'prediction': round(ml_risk, 2),
        'confidence': random.uniform(0.50, 0.75),
        'available': True,
        'synthetic': True
    }
    
    # Future price 1yr
    expert_1yr = expert_result.get('future_price_1yr', expert_price * 1.03)
    ml_1yr_variation = random.uniform(-0.08, 0.12)
    ml_1yr = expert_1yr * (1 + ml_1yr_variation)
    results['future_price_1yr'] = {
        'prediction': round(ml_1yr, 2),
        'confidence': random.uniform(0.45, 0.70),
        'available': True,
        'synthetic': True
    }
    
    # Future price 3yr
    expert_3yr = expert_result.get('future_price_3yr', expert_price * 1.09)
    ml_3yr_variation = random.uniform(-0.15, 0.20)
    ml_3yr = expert_3yr * (1 + ml_3yr_variation)
    results['future_price_3yr'] = {
        'prediction': round(ml_3yr, 2),
        'confidence': random.uniform(0.35, 0.60),
        'available': True,
        'synthetic': True
    }
    
    return results
