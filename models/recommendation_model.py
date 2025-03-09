from typing import List, Dict
from sqlalchemy.orm import Session
from backend.models import EmissionHistory

class RecommendationModel:
    def __init__(self):
        # Transportation-focused strategies with potential CO2 savings
        self.strategies = {
            'use_public_transport': {'impact': 200, 'description': 'Switch to public transportation for your daily commute'},
            'bike_or_walk': {'impact': 150, 'description': 'Use a bicycle or walk for short distances'},
            'electric_vehicle': {'impact': 300, 'description': 'Consider switching to an electric vehicle'},
            'carpool': {'impact': 100, 'description': 'Share rides with others to reduce emissions'},
            'optimize_routes': {'impact': 50, 'description': 'Plan efficient routes to minimize fuel consumption'}
        }

    def generate_recommendations(self, user_id: int, db: Session) -> List[Dict]:
        """
        Generate transportation-focused recommendations based on user's emissions history.

        Args:
            user_id (int): The user's ID
            db (Session): Database session

        Returns:
            List of recommendations with current emissions & potential savings.
        """
        transport_emissions = db.query(EmissionHistory).filter(
            EmissionHistory.user_id == user_id,
            EmissionHistory.category.in_(['fuel_vehicle', 'electric_vehicle', 'public_transport'])
        ).all()

        total_emissions = sum(entry.emission_value for entry in transport_emissions)
        recommendations = []

        # ✅ Step 1: Determine the most common vehicle type used
        vehicle_type_counts = {}
        for entry in transport_emissions:
            vehicle_type_counts[entry.category] = vehicle_type_counts.get(entry.category, 0) + 1

        most_used_vehicle_type = max(vehicle_type_counts, key=vehicle_type_counts.get, default="transportation")

        # ✅ Step 2: Dynamically generate recommendations
        if total_emissions > 1000:  
            recommendations.append(self._format_recommendation('use_public_transport', total_emissions, most_used_vehicle_type, "major change"))  

        elif total_emissions > 700:  
            recommendations.append(self._format_recommendation('electric_vehicle', total_emissions, most_used_vehicle_type, "major change"))  

        elif total_emissions > 500:  
            recommendations.append(self._format_recommendation('carpool', total_emissions, most_used_vehicle_type, "small change"))  

        elif total_emissions > 300:  
            recommendations.append(self._format_recommendation('optimize_routes', total_emissions, most_used_vehicle_type, "small change"))  

        elif total_emissions > 100:  
            recommendations.append(self._format_recommendation('bike_or_walk', total_emissions, most_used_vehicle_type, "small change"))  

        # ✅ Step 3: Sort by feasibility & impact
        recommendations.sort(key=lambda x: (x['recommendation_level'] == "small change", -x['potential_savings']))

        return recommendations[:5]  

    def _format_recommendation(self, strategy: str, current_emissions: float, vehicle_type: str, change_level: str) -> Dict:
        """Formats a recommendation with potential savings & level of change."""

        # Map vehicle types to categories
        category_mapping = {
            "fuel_vehicle": "fuel_vehicle",
            "electric_vehicle": "electric_vehicle",
            "public_transport": "public_transport"
        }
        category = category_mapping.get(vehicle_type, "sustainable_transport")

        # Calculate potential CO₂ savings
        potential_savings = min(self.strategies[strategy]['impact'], current_emissions)

        return {
            'strategy': strategy,
            'description': self.strategies[strategy]['description'],
            'current_emissions': current_emissions,  
            'potential_savings': potential_savings,  
            'potential_impact': self.strategies[strategy]['impact'],
            'category': category,  
            'vehicle_type': vehicle_type,  
            'recommendation_level': change_level  # ✅ Classify as "small change" or "major change"
        }



