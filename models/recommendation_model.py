from typing import List, Dict
import numpy as np

class RecommendationModel:
    def __init__(self):
        # Dictionary of reduction strategies and their potential impact (in CO2 kg/year)
        self.strategies = {
            'transportation': {
                'use_public_transport': {'impact': 2000, 'description': 'Switch to public transportation for your daily commute'},
                'bike_or_walk': {'impact': 1500, 'description': 'Use bicycle or walk for short distances'},
                'electric_vehicle': {'impact': 2500, 'description': 'Consider switching to an electric vehicle'}
            },
            'energy': {
                'led_lighting': {'impact': 300, 'description': 'Replace all bulbs with LED lights'},
                'smart_thermostat': {'impact': 600, 'description': 'Install a smart thermostat'},
                'renewable_energy': {'impact': 4000, 'description': 'Switch to renewable energy sources'}
            },
            'lifestyle': {
                'reduce_meat': {'impact': 800, 'description': 'Reduce meat consumption by 50%'},
                'local_produce': {'impact': 400, 'description': 'Buy local and seasonal produce'},
                'reduce_waste': {'impact': 500, 'description': 'Implement comprehensive recycling and composting'}
            }
        }

    def generate_recommendations(self, user_data: Dict) -> List[Dict]:
        """
        Generate personalized recommendations based on user's carbon footprint data.
        
        Args:
            user_data: Dictionary containing user's carbon footprint breakdown
                      (transportation, energy, lifestyle metrics)
        
        Returns:
            List of recommended actions sorted by potential impact
        """
        recommendations = []
        
        # Analyze transportation footprint
        if user_data.get('transportation_footprint', 0) > 4000:
            recommendations.extend(self._get_category_recommendations('transportation'))
            
        # Analyze energy footprint
        if user_data.get('energy_footprint', 0) > 3000:
            recommendations.extend(self._get_category_recommendations('energy'))
            
        # Analyze lifestyle footprint
        if user_data.get('lifestyle_footprint', 0) > 2000:
            recommendations.extend(self._get_category_recommendations('lifestyle'))
            
        # Sort recommendations by impact
        recommendations.sort(key=lambda x: x['potential_impact'], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations

    def _get_category_recommendations(self, category: str) -> List[Dict]:
        """
        Get all recommendations for a specific category.
        
        Args:
            category: The category to get recommendations for
            
        Returns:
            List of recommendations for the category
        """
        category_recommendations = []
        
        for strategy, details in self.strategies[category].items():
            category_recommendations.append({
                'category': category,
                'strategy': strategy,
                'description': details['description'],
                'potential_impact': details['impact']
            })
            
        return category_recommendations

    def calculate_potential_savings(self, selected_recommendations: List[Dict]) -> float:
        """
        Calculate potential CO2 savings from implementing selected recommendations.
        
        Args:
            selected_recommendations: List of recommendations to implement
            
        Returns:
            Total potential CO2 savings in kg/year
        """
        total_savings = sum(rec['potential_impact'] for rec in selected_recommendations)
        return total_savings