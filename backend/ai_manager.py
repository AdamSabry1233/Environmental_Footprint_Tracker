from sqlalchemy.orm import Session
from models.recommendation_model import RecommendationModel
from models.ai_agents import AIAgent
from models.carbon_footprint_predictor import CarbonFootprintPredictor


class AIManager:
    def __init__(self):
        """
        AI Manager that handles AI processing.
        """
        self.recommendation_model = RecommendationModel()
        self.ai_agent = AIAgent()
        self.carbon_predictor = CarbonFootprintPredictor()  # Load AI model


    def get_ai_recommendations(self, user_id: int, db: Session):
        """
        Generate AI-powered recommendations using static and AI-driven logic.
        """
        # Predict user's future CO₂ footprint
        predicted_footprint = self.carbon_predictor.predict_future_emissions(user_id, db)

        # Generate static recommendations based on emission history
        base_recommendations = self.recommendation_model.generate_recommendations(user_id, db)

        # Modify recommendations based on AI-predicted footprint
        if predicted_footprint > 500:
            base_recommendations.append({
                "description": "Switch to an electric vehicle",
                "impact_value": 100
            })
        elif predicted_footprint > 200:
            base_recommendations.append({
                "description": "Carpool for work commutes",
                "impact_value": 50
            })

        # Use AI clustering to refine recommendations based on user similarity
        refined_recommendations = self.ai_agent.refine_recommendations(user_id, base_recommendations, db)

        return refined_recommendations, predicted_footprint  # Return AI-enhanced recommendations


    def predict_carbon_footprint(self, user_id: int, db: Session):
            """
            Use AI to predict a user's future CO₂ emissions based on travel habits.
            """
            return self.carbon_predictor.predict_future_emissions(user_id, db)