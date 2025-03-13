from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from models.emission_calculator import CarbonCalculator
from models.recommendation_model import RecommendationModel
from .dependencies import get_db # Importing the dependency for database handling
from backend.schemas import FuelVehicleRequest, FuelVehicleResponse, ElectricVehicleRequest, ElectricVehicleResponse, PublicTransportRequest, PublicTransportResponse
from sqlalchemy.sql import func 
from backend.models import EmissionHistory, User, Recommendation, RecommendationFeedback, EcoFriendlyRoute, RouteEmissions, PredictedEmissions, ChatbotResponse, Progress
import datetime, traceback, json
from datetime import datetime, timezone, timedelta
from backend.ai_manager import AIManager
from backend.maps_api import MapsAPI
from backend.llm_integration import chat_with_ai
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  #  Hashing


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change to ["http://localhost:3000"] to be more secure.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

maps_api = MapsAPI()
calculator = CarbonCalculator()
reccomendation_model = RecommendationModel()
ai_manager = AIManager()


class TripLogRequest(BaseModel):
    user_id: int
    origin: str
    destination: str
    transport_mode: str  #  Correct field name
    fuel_type: Optional[str] = None  
    passengers: int = 1
    miles_per_kwh: Optional[float] = None  
    distance_miles: float


@app.post("/log_trip/")
def log_trip(request: TripLogRequest, db: Session = Depends(get_db)):
    """
    Logs a user's trip and calculates emissions using the correct formulas.
    """
    #  Ensure the user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    #  Define emission factors
    emission_factors = {
        "gasoline_car": 0.89, "diesel_car": 1.02, "hybrid_car": 0.43, "motorcycle": 0.46,
        "rideshare_solo": 0.89, "rideshare_shared": 0.45,
        "bus": 6.8, "diesel_bus": 16, "train": 200, "subway": 80, "high_speed_rail": 100,
        "airplane": 54000, "long_haul_flight": 172000, "ferry": 300,
        "electric_car": 0.06, "electric_scooter": 0.02, "electric_bike": 0.01,
        "bike": 0.00, "walking": 0.00
    }
    co2_per_kwh = 0.450  # Grid emissions per kWh
    co2_per_gallon = {"gasoline": 19.6, "diesel": 22.4}  # CO₂ per gallon burned

    #  Ensure transport_mode matches dictionary keys
    mode_map = {
        "driving": "gasoline_car",
        "electric": "electric_car",
        "public_transport": "bus"
    }
    corrected_mode = mode_map.get(request.transport_mode, request.transport_mode)
    print(f"DEBUG: Corrected mode={corrected_mode}")  #  Print for debugging

    #  Calculate emissions based on mode
    emissions = 0
    if corrected_mode in emission_factors:
        emissions = emission_factors[corrected_mode] * request.distance_miles
    elif request.transport_mode == "electric":
        if not request.miles_per_kwh:
            raise HTTPException(status_code=400, detail="Miles per kWh is required for electric vehicles.")
        emissions = (request.distance_miles / request.miles_per_kwh) * co2_per_kwh
    elif request.fuel_type.lower() in co2_per_gallon:
        mpg = request.miles_per_kwh or 25  # Default MPG if not provided
        fuel_type = request.fuel_type.lower()

        if mpg > 0:
            emissions = (co2_per_gallon[fuel_type] / mpg) * request.distance_miles
            print(f"DEBUG: Fuel-based calculation, emissions={emissions}")

    #  Ensure category is set
    category = "transport"

    #  Save trip data
    trip_entry = EmissionHistory(
        user_id=request.user_id,
        origin=request.origin,
        destination=request.destination,
        transport_mode=request.transport_mode,  
        fuel_type=request.fuel_type,
        miles=request.distance_miles,
        passengers=request.passengers,
        emission_value=round(emissions, 2),  #  Round for readability
        timestamp=datetime.now(timezone.utc),
        category=category
    )

    db.add(trip_entry)
    db.commit()
    db.refresh(trip_entry)

    return {
        "message": "Trip logged successfully!",
        "trip_id": trip_entry.id,
        "origin": trip_entry.origin,
        "destination": trip_entry.destination,
        "transport_mode": trip_entry.transport_mode,
        "emission_value": trip_entry.emission_value
    }


class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/get_user_trips/{user_id}")
def get_user_trips(user_id: int, db: Session = Depends(get_db)):
    """
    Fetches all logged trips for a given user.
    """
    trips = db.query(EmissionHistory).filter(EmissionHistory.user_id == user_id).all()
    
    if not trips:
        return []

    return [
        {
            "origin": trip.origin,
            "destination": trip.destination,
            "mode": trip.transport_mode,
            "fuel_type": trip.fuel_type,
            "distance_miles": trip.miles,
            "emission_value": trip.emission_value
        }
        for trip in trips
    ]


@app.post("/login_user/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Verifies user credentials and returns their user ID if successful.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful!", "user_id": db_user.id}

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/create_user/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user and hashes their password.
    """
    print(f"DEBUG: Received request to create user with email {user.email}")  #  Debugging Line

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        print(f"DEBUG: User with email {user.email} already exists!")  #  Debugging Line
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(name=user.username, email=user.email, hashed_password=hashed_password)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"DEBUG: User {user.username} created successfully!")  #  Debugging Line
    except Exception as e:
        print(f"ERROR: {e}")  #  Debugging Line
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

    return {"message": "User created successfully!", "user_id": new_user.id}


@app.post("/progress/set_goal/")
def set_progress_goal(user_id: int, goal: str, db: Session = Depends(get_db)):
    """
    Set a sustainability goal for the user.
    Example Goal: "Reduce emissions by 20% in 3 months"
    """
    existing_progress = db.query(Progress).filter(Progress.user_id == user_id).first()

    if existing_progress:
        raise HTTPException(status_code=400, detail="User already has a progress goal set.")

    # Get baseline emissions (Sum of all recorded emissions)
    baseline_emissions = db.query(func.sum(EmissionHistory.emission_value)).filter(
        EmissionHistory.user_id == user_id
    ).scalar() or 0

    progress_entry = Progress(
        user_id=user_id,
        goal=goal,
        progress_percentage=0.0,  # Start at 0%
        last_updated=datetime.now(timezone.utc),
        baseline_emissions=baseline_emissions  # Store baseline
    )

    db.add(progress_entry)
    db.commit()
    db.refresh(progress_entry)

    return {
        "message": "Progress goal set successfully!",
        "goal": goal,
        "baseline_emissions": baseline_emissions
    }

@app.get("/progress/track_progress/{user_id}")
def track_progress(user_id: int, db: Session = Depends(get_db)):
    """
    Track the user's progress towards their emissions reduction goal.
    Compares baseline emissions to current emissions.
    """
    progress_entry = db.query(Progress).filter(Progress.user_id == user_id).first()

    if not progress_entry:
        raise HTTPException(status_code=404, detail="No progress goal found for this user.")

    #  Get current emissions (Sum of recent emissions from EmissionHistory)
    current_emissions = db.query(func.sum(EmissionHistory.emission_value)).filter(
        EmissionHistory.user_id == user_id
    ).scalar() or 0

    #  Calculate progress percentage
    baseline = progress_entry.baseline_emissions
    if baseline > 0:
        progress_percentage = ((baseline - current_emissions) / baseline) * 100
    else:
        progress_percentage = 0

    #  Update progress in the database
    progress_entry.progress_percentage = round(progress_percentage, 2)
    progress_entry.last_updated = datetime.now(timezone.utc)

    db.commit()

    return {
        "user_id": user_id,
        "goal": progress_entry.goal,
        "baseline_emissions": round(baseline, 2),
        "current_emissions": round(current_emissions, 2),  #  Ensure it's displayed
        "progress_percentage": round(progress_percentage, 2),  #  Now properly displayed
        "last_updated": progress_entry.last_updated
    }


@app.post("/chatbot/")
def chatbot(user_id: int, query: str, db: Session = Depends(get_db)):
    """
    AI-powered chatbot for real-time sustainability advice.
    - Accepts user queries and generates AI responses.
    - Uses user emissions data for personalized recommendations.
    - Saves responses to the database.
    """
    ai_response = chat_with_ai(user_id, query, db)  #  Pass DB to fetch emissions

    #  Save chatbot interaction in the database
    chat_entry = ChatbotResponse(user_id=user_id, user_query=query, bot_response=ai_response)
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)

    return {
        "user_id": user_id,
        "query": query,
        "response": ai_response,
        "timestamp": chat_entry.created_at
    }

import logging

@app.get("/predict_carbon_footprint/{user_id}")
def predict_carbon_footprint(user_id: int, db: Session = Depends(get_db)):
    """
    Predicts future carbon footprint based on past travel habits using AI and saves it.
    """
    logging.info(f"🚀 Predicting carbon footprint for user_id: {user_id}")

    predicted_footprint = ai_manager.predict_carbon_footprint(user_id, db)

    #  Handle missing data
    if predicted_footprint is None:
        logging.warning(f"⚠️ No prediction data available for user_id: {user_id}")
        return {
            "user_id": user_id,
            "predicted_co2_emissions_lbs": 0,
            "message": "No travel history found. Log some trips for predictions."
        }

    if predicted_footprint == 0:
        logging.warning(f"⚠️ Prediction resulted in 0 CO₂ for user_id: {user_id}")
        return {
            "user_id": user_id,
            "predicted_co2_emissions_lbs": 0,
            "message": "Insufficient travel data for a reliable prediction."
        }

    #  Ensure the predicted value is a standard Python float
    predicted_footprint = float(predicted_footprint)  # Convert np.float64 → Python float
    logging.info(f" Prediction for user_id {user_id}: {predicted_footprint} lbs CO₂")

    #  Save only valid predictions
    prediction_entry = PredictedEmissions(
        user_id=user_id,
        predicted_co2=predicted_footprint
    )
    db.add(prediction_entry)
    db.commit()
    db.refresh(prediction_entry)

    return {
        "user_id": user_id,
        "predicted_co2_emissions_lbs": round(predicted_footprint, 2),
        "message": "AI-based carbon footprint prediction completed and saved."
    }


@app.get("/route_emissions/")
def calculate_route_emissions(
    origin: str,
    destination: str,
    mode: str = "driving",
    fuel_type: str = "gasoline_car",
    passengers: int = 1,
    miles_per_kwh: float = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Calculates CO₂ emissions for a route and logs it in the database.
    """
    distance_miles, duration_minutes = maps_api.get_route_details(origin, destination, mode)
    if distance_miles is None:
        return {"error": "Could not retrieve route details."}

    # Calculate emissions based on transport mode
    if mode == "driving":
        emissions = calculator.estimate_fuel_vehicle_emissions(fuel_type, mpg=25, miles=distance_miles, passengers=passengers)
    elif mode == "transit":
        emissions = calculator.estimate_public_transport_emissions(fuel_type, miles=distance_miles, passengers=passengers)
    elif mode in ["walking", "bicycling"]:
        emissions = 0
    elif "electric" in fuel_type:
        if miles_per_kwh is None:
            raise HTTPException(status_code=400, detail="Miles per kWh is required for electric vehicles.")
        emissions = calculator.estimate_electric_vehicle_emissions(fuel_type, miles_per_kwh, distance_miles, passengers)
    else:
        emissions = calculator.estimate_fuel_vehicle_emissions(fuel_type, mpg=25, miles=distance_miles, passengers=passengers)

    # Log emissions data if user_id is provided
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        emission_entry = RouteEmissions(
            user_id=user_id,
            origin=origin,
            destination=destination,
            transport_mode=mode,
            fuel_type=fuel_type,
            distance_miles=distance_miles,
            co2_emissions=emissions
        )
        db.add(emission_entry)
        db.commit()
        db.refresh(emission_entry)
    
    return {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "distance_miles": round(distance_miles, 2),
        "duration_minutes": round(duration_minutes, 2),
        "estimated_emissions_lbs": round(emissions, 2)
    }



@app.get("/eco_friendly_routes/")
def get_eco_routes(
    user_id: int,
    origin: str = Query(..., description="Starting location"),
    destination: str = Query(..., description="Destination"),
    mode: str = Query("DRIVE", description="Mode of transport (DRIVE, WALK, BICYCLE, TRANSIT)"),
    db: Session = Depends(get_db)
):
    """
    Fetches eco-friendly route alternatives from Google Maps API, selects the optimal route,
    calculates CO₂ savings using actual emissions from route_emissions, and saves them.
    """
    eco_routes = maps_api.get_eco_friendly_routes(origin, destination)
    print("Eco Routes Response:", eco_routes)

    if not eco_routes:
        print("[ERROR] No eco-friendly routes retrieved.")
        return {"error": "Could not retrieve eco-friendly routes."}

    # Select the most eco-friendly route (shortest distance)
    best_route = min(eco_routes, key=lambda r: r["distance_miles"])
    print("[INFO] Best route selected:", best_route)

    #  Use actual emissions from route_emissions instead of estimating
    worst_route_emission = db.query(RouteEmissions).filter(
        RouteEmissions.origin == origin,
        RouteEmissions.destination == destination
    ).order_by(RouteEmissions.co2_emissions.desc()).first()

    if worst_route_emission:
        worst_route_emissions = worst_route_emission.co2_emissions
    else:
        worst_route_distance = max(r["distance_miles"] for r in eco_routes)  # Worst-case distance
        worst_route_emissions = calculator.estimate_fuel_vehicle_emissions(
            "gasoline_car", mpg=25, miles=worst_route_distance, passengers=1
        )  # Estimate only if no real data is found

    # Calculate emissions for the best route
    best_route_emissions = calculator.estimate_fuel_vehicle_emissions(
        "gasoline_car", mpg=25, miles=best_route["distance_miles"], passengers=1
    )

    # Calculate CO₂ savings
    co2_savings = worst_route_emissions - best_route_emissions if worst_route_emissions > best_route_emissions else 0
    print("[INFO] CO₂ Savings Calculated:", co2_savings)

    # Save only the best route to the database
    try:
        route_entry = EcoFriendlyRoute(
            user_id=user_id,
            origin=origin,
            destination=destination,
            optimal_route=json.dumps(best_route),  # Store only the best route
            transport_mode=mode,
            distance_miles=best_route["distance_miles"]
        )
        db.add(route_entry)
        db.commit()
        db.refresh(route_entry)
        print(f"[SUCCESS] Optimal route saved to database with ID: {route_entry.id}")
    except Exception as e:
        db.rollback()
        print("[ERROR] Database Error:", traceback.format_exc())
        return {"error": "Failed to save optimal route to database."}

    return {
        "message": "Optimal eco-friendly route saved successfully!",
        "optimal_route": best_route,
        "all_routes": eco_routes,
    }




@app.get("/get_ai_recommendations/{user_id}")
def get_ai_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves AI-enhanced recommendations for a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    # AI refines recommendations
    refined_recommendations, predicted_footprint = ai_manager.get_ai_recommendations(user_id, db)

    if not refined_recommendations:
        return {
            "message": "No AI recommendations available.",
            "predicted_co2_emissions_lbs": round(predicted_footprint, 2)  #  Ensure response contains prediction.
        }

    #  Clear old recommendations to avoid duplicate storage
    db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
    db.commit()

    #  Store refined recommendations in database
    recommendation_entries = []
    for rec in refined_recommendations:
        new_rec = Recommendation(
            user_id=user_id,
            recommendation_text=rec["description"],
            category=rec.get("category", "transportation"),
            current_emissions=rec.get("current_emissions", 0),  #  Avoid KeyError
            impact_value=rec.get("potential_savings", 0),  #  Ensure default values
            vehicle_type=rec.get("vehicle_type", "Unknown"),
            recommendation_level=rec.get("recommendation_level", "General"),
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_rec)
        recommendation_entries.append(new_rec)

    db.commit()

    return {
        "recommendations": recommendation_entries,
        "predicted_co2_emissions_lbs": round(predicted_footprint, 2)  #  Show predicted footprint in response.
    }


@app.post("/update_recommendation_feedback")
def update_feedback(
    user_id: int, 
    recommendation_id: int,  
    accepted: bool, 
    feedback: str, 
    db: Session = Depends(get_db)
):
    print(f"Received request: user_id={user_id}, recommendation_id={recommendation_id}, accepted={accepted}, feedback={feedback}")

    #  Ensure the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print("User not found")
        raise HTTPException(status_code=400, detail="User does not exist")

    #  Ensure the recommendation exists
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == user_id
    ).first()

    if not recommendation:
        print("Recommendation not found")
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    #  Insert feedback into the separate table
    feedback_entry = RecommendationFeedback(
        user_id=user_id,
        recommendation_id=recommendation_id,
        accepted=accepted,
        feedback=feedback,
        created_at=datetime.now(timezone.utc)
    )
    db.add(feedback_entry)
    db.commit()

    print("Feedback recorded successfully!")
    return {"message": "Feedback recorded successfully!"}




@app.get("/get_recommendations/{user_id}")
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a user's transport-related emissions and generates personalized recommendations.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    #  Step 1: Get transport emissions
    transport_emissions = db.query(EmissionHistory).filter(
        EmissionHistory.user_id == user_id,
        EmissionHistory.category.in_(["fuel_vehicle", "electric_vehicle", "public_transport"])
    ).all()

    if not transport_emissions:
        raise HTTPException(status_code=404, detail="No transport emissions data found.")

    #  Step 2: Calculate total transportation emissions
    total_transportation_emissions = sum(entry.emission_value for entry in transport_emissions)

    #  Step 3: Clear old recommendations before generating new ones
    db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
    db.commit()  #  Clear duplicates

    #  Step 4: Generate new recommendations
    recommendations = reccomendation_model.generate_recommendations(user_id, db)

    if not recommendations:
        return {"message": "No recommendations available for your current footprint."}

    #  Step 5: Store recommendations in the database
    recommendation_entries = []
    for rec in recommendations:
        new_rec = Recommendation(
            user_id=user_id,
            recommendation_text=rec["description"],
            category=rec.get("category", "transportation"), 
            current_emissions=total_transportation_emissions,
            impact_value=rec["potential_impact"],  
            vehicle_type=rec["vehicle_type"],  #  Track user's vehicle habit
            recommendation_level=rec["recommendation_level"],  #  Store small/major change
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_rec)
        recommendation_entries.append(new_rec)

    db.commit()

    #  Step 6: Return stored recommendations
    return [
        {
            "strategy": rec.recommendation_text,
            "category": rec.category,
            "current_emissions": rec.current_emissions,
            "potential_savings": rec.impact_value,  
            "vehicle_type": rec.vehicle_type,  
            "recommendation_level": rec.recommendation_level,  
            "created_at": rec.created_at
        }
        for rec in recommendation_entries
    ]




@app.post("/calculate/fuel_vehicle", response_model=FuelVehicleResponse)
def calculate_fuel_vehicle_emissions(request: FuelVehicleRequest):
    """
    API endpoint to calculate emissions for fuel-based vehicles 
    (gasoline_car, diesel_car, hybrid_car, motorcycle, rideshare_solo, rideshare_shared).
    """
    emissions = calculator.estimate_fuel_vehicle_emissions(
        request.fuel_type, request.mpg, request.miles, request.passengers
    )

    return FuelVehicleResponse(
        user_id=request.user_id,
        fuel_type=request.fuel_type,
        mpg=request.mpg,
        miles=request.miles,
        passengers=request.passengers,
        emissions_lbs_per_person=emissions
    )


@app.post("/calculate/electric_vehicle", response_model=ElectricVehicleResponse)
def calculate_electric_vehicle_emissions(request: ElectricVehicleRequest):
    """
    API endpoint to calculate emissions for electric vehicles 
    (electric_car, electric_scooter, electric_bike).
    """
    emissions = calculator.estimate_electric_vehicle_emissions(
        request.electric_type, request.miles_per_kwh, request.miles, request.passengers
    )

    return ElectricVehicleResponse(
        user_id=request.user_id,
        electric_type=request.electric_type,
        miles_per_kwh=request.miles_per_kwh,
        miles=request.miles,
        passengers=request.passengers,
        emissions_lbs_per_person=emissions
    )


@app.post("/calculate/public_transport", response_model=PublicTransportResponse)
def calculate_public_transport_emissions(request: PublicTransportRequest):
    """
    API endpoint to calculate emissions for public transport 
    (bus, diesel_bus, subway, high_speed_rail, long_haul_flight, train, airplane, ferry).
    """
    emissions = calculator.estimate_public_transport_emissions(
        request.transport_type, request.miles, request.passengers
    )

    return PublicTransportResponse(
        user_id=request.user_id,
        transport_type=request.transport_type,
        miles=request.miles,
        passengers=request.passengers,
        emissions_lbs_per_person=emissions
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
