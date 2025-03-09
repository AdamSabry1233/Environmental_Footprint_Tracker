import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sqlalchemy.orm import Session
from backend.models import Recommendation, EmissionHistory, RecommendationFeedback

class AIAgent:
    def __init__(self, n_clusters=3):
        """
        AI Agent using K-Means Clustering to refine recommendations.
        """
        self.n_clusters = n_clusters  # Number of user clusters
        self.kmeans = None  # K-Means model
    
    def _get_user_data(self, db: Session):
        """
        Fetch user emissions with additional transport type & miles.
        Ensures no NaN values exist before clustering.
        """
        records = db.query(EmissionHistory).all()

        if not records:
            return pd.DataFrame(columns=["user_id", "emission_value", "miles_traveled"])  

        data = pd.DataFrame([
            {
                "user_id": rec.user_id,
                "emission_value": rec.emission_value if rec.emission_value is not None else 0,
                "miles_traveled": rec.miles if rec.miles is not None else 0
            }
            for rec in records
        ])

        # ✅ Convert to numeric & replace NaNs with 0
        data["emission_value"] = pd.to_numeric(data["emission_value"], errors="coerce").fillna(0)
        data["miles_traveled"] = pd.to_numeric(data["miles_traveled"], errors="coerce").fillna(0)

        return data


    
    def train_model(self, db: Session):
        """
        Train K-Means Clustering on user emission behavior, transport type & miles.
        """
        user_data = self._get_user_data(db)

        if user_data.empty:
            print("⚠️ No valid training data available. Skipping clustering.")
            return  # No training data

        X = user_data[["emission_value", "miles_traveled"]].values  # ✅ Include miles traveled

        # ✅ Ensure no NaN values before training KMeans
        if np.isnan(X).any():
            print("⚠️ NaN detected in training data. Replacing NaNs with 0.")
            X = np.nan_to_num(X)  # ✅ Replace NaNs with 0 before training

        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.kmeans.fit(X)  # Train model


    
    def predict_cluster(self, user_id: int, db: Session):
        """
        Predict which cluster the user belongs to.
        """
        if self.kmeans is None:
            self.train_model(db)  # Train if not already trained
        
        user_data = self._get_user_data(db)
        if user_id not in user_data["user_id"].values:
            return None  # User not found
        
        # ✅ Extract both 'emission_value' and 'miles_traveled'
        user_features = user_data[user_data["user_id"] == user_id][["emission_value", "miles_traveled"]].values

        # ✅ Ensure shape consistency (no NaN values)
        if np.isnan(user_features).any():
            print(f"⚠️ User {user_id} has NaN values. Replacing NaNs with 0.")
            user_features = np.nan_to_num(user_features)

        return self.kmeans.predict(user_features)[0]  # ✅ Now passes 2D input


    
    def refine_recommendations(self, user_id: int, recommendations: list, db: Session):
        """
        Refine AI recommendations using clustering, user feedback, and past similar users' recommendations.
        """
        user_cluster = self.predict_cluster(user_id, db)
        if user_cluster is None:
            return recommendations  # ✅ Return unmodified recommendations if clustering fails.

        user_data = self._get_user_data(db)

        # ✅ Fetch user feedback from `recommendation_feedback`
        feedback = db.query(RecommendationFeedback).filter(
            RecommendationFeedback.user_id == user_id
        ).all()

        accepted_suggestions = {fb.recommendation_text for fb in feedback if fb.accepted}
        rejected_suggestions = {fb.recommendation_text for fb in feedback if fb.accepted is False}

        # ✅ Get past recommendations from similar users in the same cluster
        similar_users = user_data[user_data["user_id"] != user_id]
        similar_users = similar_users[
            similar_users[["emission_value", "miles_traveled"]].apply(
                lambda x: self.kmeans.predict([x])[0] == user_cluster, axis=1
            )
        ]

        if not similar_users.empty:
            similar_user_ids = similar_users["user_id"].tolist()
            past_recommendations = db.query(Recommendation).filter(
                Recommendation.user_id.in_(similar_user_ids)
            ).all()

            # ✅ Add accepted suggestions from similar users
            for rec in past_recommendations:
                if rec.accepted:
                    accepted_suggestions.add(rec.recommendation_text)
                elif rec.accepted is False:
                    rejected_suggestions.add(rec.recommendation_text)

        # ✅ Sort recommendations based on AI logic:
        refined_recommendations = sorted(
            recommendations,
            key=lambda x: (
                x["description"] in accepted_suggestions,  # ✅ Prioritize accepted
                x["description"] not in rejected_suggestions,  # ❌ Avoid rejected
                -x.get("potential_savings", 0)  # ✅ Ensure default value exists
            ),
            reverse=True
        )

        return refined_recommendations[:5]  # ✅ Return top 5 refined recommendations





