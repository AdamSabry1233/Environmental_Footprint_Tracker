import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from backend.models import RouteEmissions

class CarbonFootprintPredictor:
    def __init__(self):
        """
        AI Model to predict a user's future carbon footprint based on past travel behavior.
        """
        self.model = LinearRegression()  # Initialize model

    def get_user_travel_data(self, user_id: int, db: Session):
        """
        Fetch user's past travel emissions from `route_emissions` for AI predictions.
        """
        emissions_data = db.query(RouteEmissions).filter(RouteEmissions.user_id == user_id).all()

        if not emissions_data:
            return None  # No data available

        travel_data = pd.DataFrame([
            {
                "distance_miles": entry.distance_miles,
                "co2_emissions": entry.co2_emissions
            }
            for entry in emissions_data
        ])

        return travel_data if not travel_data.empty else None

    def train_model(self, user_id: int, db: Session):
        """
        Train AI model using a user's historical travel emissions.
        """
        travel_data = self.get_user_travel_data(user_id, db)

        if travel_data is None or travel_data.empty:
            return None  # No data to train

        X = travel_data[["distance_miles"]].values
        y = travel_data["co2_emissions"].values

        if len(X) < 3:  #  Handle cases with fewer than 3 records
            return None  # Not enough data to train

        self.model.fit(X, y)  #  Train model

    def predict_future_emissions(self, user_id: int, db: Session):
        """
        Predict the user's future carbon footprint based on historical data.
        """
        travel_data = self.get_user_travel_data(user_id, db)

        if travel_data is None or travel_data.empty:
            return None  #  Return None instead of 0 for missing data

        # If <3 records, return the average instead of training
        if len(travel_data) < 3:
            return round(travel_data["co2_emissions"].mean(), 2)

        self.train_model(user_id, db)

        avg_future_distance = np.mean(travel_data["distance_miles"])  

        if np.isnan(avg_future_distance) or avg_future_distance == 0:
            return round(travel_data["co2_emissions"].mean(), 2)  #  Return average emissions

        predicted_emission = self.model.predict(np.array([[avg_future_distance]]))[0]

        return round(float(predicted_emission), 2)  #  Convert np.float64 → Python float
