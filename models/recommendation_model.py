from typing import List, Dict
from sqlalchemy.orm import Session
from backend.models import EmissionHistory, RecommendationFeedback, Recommendation

class RecommendationModel:
    def __init__(self):
        """
        Transportation-focused strategies with dynamic AI-driven recommendations.
        """
        self.strategies = {
            'use_public_transport': {'impact': 200, 'description': 'Switch to public transportation for your daily commute'},
            'bike_or_walk': {'impact': 150, 'description': 'Use a bicycle or walk for short distances'},
            'electric_vehicle': {'impact': 300, 'description': 'Consider switching to an electric vehicle'},
            'carpool': {'impact': 100, 'description': 'Share rides with others to reduce emissions'},
            'optimize_routes': {'impact': 50, 'description': 'Plan efficient routes to minimize fuel consumption'}
        }

    def generate_recommendations(self, user_id: int, db: Session) -> List[Dict]:
        """
        Generate recommendations dynamically based on emissions & user behavior.

        - Retrieves user's transport emissions.
        - Sorts based on highest emissions category.
        - Adjusts weights based on previous feedback.
        """
        transport_emissions = db.query(EmissionHistory).filter(
            EmissionHistory.user_id == user_id,
            EmissionHistory.category.in_(['fuel_vehicle', 'electric_vehicle', 'public_transport'])
        ).all()

        total_emissions = sum(entry.emission_value for entry in transport_emissions)
        recommendations = []

        # Find the most common transport mode used by the user
        vehicle_type_counts = {}
        for entry in transport_emissions:
            vehicle_type_counts[entry.category] = vehicle_type_counts.get(entry.category, 0) + 1

        most_used_vehicle_type = max(vehicle_type_counts, key=vehicle_type_counts.get, default="transportation")

        # Adjust recommendations dynamically based on total emissions
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

        # Adjust recommendations based on user feedback history
        recommendations = self.adjust_based_on_feedback(user_id, recommendations, db)

        # Sort recommendations by impact & feasibility
        recommendations.sort(key=lambda x: (x['recommendation_level'] == "small change", -x['potential_savings']))

        return recommendations[:5]  

    def adjust_based_on_feedback(self, user_id: int, recommendations: List[Dict], db: Session):
        """
        Adjusts recommendations based on user feedback.
        - Boosts accepted recommendations.
        - Reduces weight of rejected recommendations.
        """

        feedback = db.query(RecommendationFeedback).filter(
            RecommendationFeedback.user_id == user_id
        ).all()

        # ✅ Fetch `recommendation_text` by joining with `Recommendation` table
        accepted_suggestions = {
            db.query(Recommendation.recommendation_text)
            .filter(Recommendation.id == fb.recommendation_id)
            .scalar() for fb in feedback if fb.accepted
        }

        rejected_suggestions = {
            db.query(Recommendation.recommendation_text)
            .filter(Recommendation.id == fb.recommendation_id)
            .scalar() for fb in feedback if not fb.accepted
        }

        for rec in recommendations:
            if rec["description"] in accepted_suggestions:
                rec["potential_savings"] *= 1.2  #  Boost impact by 20%
            if rec["description"] in rejected_suggestions:
                rec["potential_savings"] *= 0.7  #  Reduce impact by 30%

        return recommendations


    def _format_recommendation(self, strategy: str, current_emissions: float, vehicle_type: str, change_level: str) -> Dict:
        """Formats a recommendation with dynamic AI weight adjustments."""

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
            'category': category,  
            'vehicle_type': vehicle_type,  
            'recommendation_level': change_level  # Classify as "small change" or "major change"
        }
