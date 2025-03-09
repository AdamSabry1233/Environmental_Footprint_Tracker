from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.dependencies import Base  # ✅ Ensure this is the correct Base
from datetime import UTC


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    emissions = relationship("EmissionHistory", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    eco_friendly_routes = relationship("EcoFriendlyRoute", back_populates="user")
    route_emissions = relationship("RouteEmissions", back_populates="user", cascade="all, delete-orphan")
    chatbot_responses = relationship("ChatbotResponse", back_populates="user", cascade="all, delete-orphan")


class ChatbotResponse(Base):
    __tablename__ = "chatbot_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for guest users
    user_query = Column(String, nullable=False)  # Store user input
    bot_response = Column(String, nullable=False)  # Store chatbot response
    created_at = Column(DateTime, default=datetime.now(UTC))  # Timestamp

    # Relationship to User model (Optional for tracking responses)
    user = relationship("User", back_populates="chatbot_responses")


class PredictedEmissions(Base):
    __tablename__ = "predicted_emissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_co2 = Column(Float, nullable=False)  # Store predicted emissions
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))



class EmissionHistory(Base):
    __tablename__ = "emission_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # transport, energy, diet, etc.
    emission_value = Column(Float, nullable=False)  # kg CO2 equivalent
    fuel_type = Column(String, nullable=False)  # ✅ Store fuel type
    mpg = Column(Float, nullable=True)  # ✅ Store miles per gallon
    miles = Column(Float, nullable=False)  # ✅ Store miles traveled
    passengers = Column(Integer, nullable=False)  # ✅ Store passengers
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


    user = relationship("User", back_populates="emissions")


class RouteEmissions(Base):
    __tablename__ = "route_emissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    transport_mode = Column(String, nullable=False)  # Mode of transport (driving, transit, etc.)
    fuel_type = Column(String, nullable=False)  # Fuel type (gasoline, electric, etc.)
    distance_miles = Column(Float, nullable=False)  # Miles traveled
    co2_emissions = Column(Float, nullable=False)  # CO₂ emissions per trip
    created_at = Column(DateTime, default=datetime.now(UTC))

    # Relationship to User model
    user = relationship("User", back_populates="route_emissions")


class EcoFriendlyRoute(Base):
    __tablename__ = "eco_friendly_routes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    optimal_route = Column(String, nullable=False)  # Renamed from route_details
    transport_mode = Column(String, nullable=False)  # Transport mode column
    distance_miles = Column(Float, nullable=False)  # Store distance in miles
    created_at = Column(DateTime, default=datetime.now(UTC))

    # Relationship to User model
    user = relationship("User", back_populates="eco_friendly_routes")




class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_text = Column(String, nullable=False)
    category = Column(String, nullable=False)
    current_emissions = Column(Float, nullable=False)
    impact_value = Column(Float, nullable=False)
    vehicle_type = Column(String, nullable=True)
    recommendation_level = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    # ✅ Ensure back_populates links to User model
    user = relationship("User", back_populates="recommendations")  

    # ✅ New fields for AI feedback system
    accepted = Column(Boolean, nullable=True, default=None)
    feedback = Column(String, nullable=True)

    # ✅ Relationship to feedback table
    feedbacks = relationship("RecommendationFeedback", back_populates="recommendation")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    accepted = Column(Boolean, nullable=True, default=None)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))

    # Relationship to the recommendations table
    recommendation = relationship("Recommendation", back_populates="feedbacks")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(String, nullable=False)  # e.g., Reduce emissions by 20%
    progress_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.now(UTC))

    user = relationship("User", back_populates="progress")
