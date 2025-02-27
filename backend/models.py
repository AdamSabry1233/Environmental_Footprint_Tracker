from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
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

class EmissionHistory(Base):
    __tablename__ = "emission_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # transport, energy, diet, etc.
    emission_value = Column(Float, nullable=False)  # kg CO2 equivalent
    fuel_type = Column(String, nullable=False)  # ✅ Store fuel type
    mpg = Column(Float, nullable=False)  # ✅ Store miles per gallon
    miles = Column(Float, nullable=False)  # ✅ Store miles traveled
    passengers = Column(Integer, nullable=False)  # ✅ Store passengers
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


    user = relationship("User", back_populates="emissions")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_text = Column(String, nullable=False)
    category = Column(String, nullable=False)  # transport, energy, diet
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(String, nullable=False)  # e.g., Reduce emissions by 20%
    progress_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress")
