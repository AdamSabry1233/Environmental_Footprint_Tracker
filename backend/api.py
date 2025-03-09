from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from models.emission_calculator import CarbonCalculator
from models.recommendation_model import RecommendationModel
from .dependencies import get_db # Importing the dependency for database handling
from backend.schemas import FuelVehicleRequest, FuelVehicleResponse, ElectricVehicleRequest, ElectricVehicleResponse, PublicTransportRequest, PublicTransportResponse
from sqlalchemy.orm import Session
from backend.models import EmissionHistory, User, Recommendation, RecommendationFeedback, EcoFriendlyRoute, RouteEmissions, PredictedEmissions, ChatbotResponse
from fastapi import HTTPException
import datetime, traceback, json
from datetime import datetime, timezone
from backend.ai_manager import AIManager
from backend.maps_api import MapsAPI
from backend.llm_integration import chat_with_ai

app = FastAPI()
maps_api = MapsAPI()
calculator = CarbonCalculator()
reccomendation_model = RecommendationModel()
ai_manager = AIManager()

from datetime import datetime, timezone


@app.post("/chatbot/")
def chatbot(user_id: int, query: str, db: Session = Depends(get_db)):
    """
    AI-powered chatbot for real-time sustainability advice.
    - Accepts user queries and generates AI responses.
    - Uses user emissions data for personalized recommendations.
    - Saves responses to the database.
    """
    ai_response = chat_with_ai(user_id, query, db)  # ✅ Pass DB to fetch emissions

    # ✅ Save chatbot interaction in the database
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

@app.get("/predict_carbon_footprint/{user_id}")
def predict_carbon_footprint(user_id: int, db: Session = Depends(get_db)):
    """
    Predicts future carbon footprint based on past travel habits using AI and saves it.
    """
    predicted_footprint = ai_manager.predict_carbon_footprint(user_id, db)

    # ✅ Save prediction to database
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

    # ✅ Use actual emissions from route_emissions instead of estimating
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
            "predicted_co2_emissions_lbs": round(predicted_footprint, 2)  # ✅ Ensure response contains prediction.
        }

    # ✅ Clear old recommendations to avoid duplicate storage
    db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
    db.commit()

    # ✅ Store refined recommendations in database
    recommendation_entries = []
    for rec in refined_recommendations:
        new_rec = Recommendation(
            user_id=user_id,
            recommendation_text=rec["description"],
            category=rec.get("category", "transportation"),
            current_emissions=rec.get("current_emissions", 0),  # ✅ Avoid KeyError
            impact_value=rec.get("potential_savings", 0),  # ✅ Ensure default values
            vehicle_type=rec.get("vehicle_type", "Unknown"),
            recommendation_level=rec.get("recommendation_level", "General"),
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_rec)
        recommendation_entries.append(new_rec)

    db.commit()

    return {
        "recommendations": recommendation_entries,
        "predicted_co2_emissions_lbs": round(predicted_footprint, 2)  # ✅ Show predicted footprint in response.
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

    # ✅ Ensure the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print("User not found")
        raise HTTPException(status_code=400, detail="User does not exist")

    # ✅ Ensure the recommendation exists
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == user_id
    ).first()

    if not recommendation:
        print("Recommendation not found")
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    # ✅ Insert feedback into the separate table
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

    # ✅ Step 1: Get transport emissions
    transport_emissions = db.query(EmissionHistory).filter(
        EmissionHistory.user_id == user_id,
        EmissionHistory.category.in_(["fuel_vehicle", "electric_vehicle", "public_transport"])
    ).all()

    if not transport_emissions:
        raise HTTPException(status_code=404, detail="No transport emissions data found.")

    # ✅ Step 2: Calculate total transportation emissions
    total_transportation_emissions = sum(entry.emission_value for entry in transport_emissions)

    # ✅ Step 3: Clear old recommendations before generating new ones
    db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
    db.commit()  # ✅ Clear duplicates

    # ✅ Step 4: Generate new recommendations
    recommendations = reccomendation_model.generate_recommendations(user_id, db)

    if not recommendations:
        return {"message": "No recommendations available for your current footprint."}

    # ✅ Step 5: Store recommendations in the database
    recommendation_entries = []
    for rec in recommendations:
        new_rec = Recommendation(
            user_id=user_id,
            recommendation_text=rec["description"],
            category=rec.get("category", "transportation"), 
            current_emissions=total_transportation_emissions,
            impact_value=rec["potential_impact"],  
            vehicle_type=rec["vehicle_type"],  # ✅ Track user's vehicle habit
            recommendation_level=rec["recommendation_level"],  # ✅ Store small/major change
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_rec)
        recommendation_entries.append(new_rec)

    db.commit()

    # ✅ Step 6: Return stored recommendations
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
def calculate_fuel_vehicle_emissions(request: FuelVehicleRequest, db: Session = Depends(get_db)):

    """
    API endpoint to calculate emissions for fuel-based vehicles (gasoline_car, diesel_car, hybrid_car, motorcycle, ridshare_solo, rideshare_shared).
    """
    user = db.query(User).filter(User.id == request.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    emissions = calculator.estimate_fuel_vehicle_emissions(request.fuel_type, request.mpg, request.miles, request.passengers)

    #Saves to the database
    emission_entry = EmissionHistory(
        user_id=request.user_id,
        category="fuel_vehicle",
        emission_value=emissions,
        fuel_type=request.fuel_type,  # ✅ Store fuel type
        mpg=request.mpg,  # ✅ Store MPG
        miles=request.miles,  # ✅ Store miles traveled
        passengers=request.passengers  # ✅ Store passengers
    )
    db.add(emission_entry)
    db.commit()
    db.refresh(emission_entry)

    return FuelVehicleResponse(
        user_id=request.user_id,
        fuel_type=request.fuel_type,
        mpg=request.mpg,
        miles=request.miles,
        passengers=request.passengers,
        emissions_lbs_per_person=emissions
    )

    

@app.post("/calculate/electric_vehicle", response_model=ElectricVehicleResponse)
def calculate_electric_vehicle_emissions(request: ElectricVehicleRequest, db: Session = Depends(get_db)):
    """
    API endpoint to calculate emissions for electric vehicles (electric_car, electric_scooter, electric_bike).
    """
    user = db.query(User).filter(User.id == request.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    emissions = calculator.estimate_electric_vehicle_emissions(request.electric_type,request.miles_per_kwh, request.miles, request.passengers)
    #Saves to the database
    emission_entry = EmissionHistory(
        user_id=request.user_id,
        category="electric_vehicle",
        emission_value=emissions,
        fuel_type=request.electric_type,  #  Store fuel type
        miles=request.miles,  #  Store miles traveled
        passengers=request.passengers,  #  Store passengers
        mpg = request.miles_per_kwh # Efficiency
    )
    db.add(emission_entry)
    db.commit()
    db.refresh(emission_entry)

    return ElectricVehicleResponse(
        user_id=request.user_id,
        electric_type=request.electric_type,
        miles_per_kwh=request.miles_per_kwh,
        miles=request.miles,
        passengers=request.passengers,
        emissions_lbs_per_person=emissions
    )

@app.post("/calculate/public_transport", response_model=PublicTransportResponse)
def calculate_public_transport_emissions(request: PublicTransportRequest, db: Session = Depends(get_db)):
    """
    API endpoint to calculate emissions for public transport (bus, diesel_bus, subway, high_speed_rail, long_haul_flight, train, airplane, ferry).
    """
    user = db.query(User).filter(User.id == request.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    emissions = calculator.estimate_public_transport_emissions(request.transport_type, request.miles, request.passengers)
    #Saves to the database
    emission_entry = EmissionHistory(
        user_id=request.user_id,
        category="public_transport",
        emission_value=emissions,
        fuel_type=request.transport_type,  #  Store fuel type
        miles=request.miles,  #  Store miles traveled
        passengers=request.passengers,  #  Store passengers
    )
    db.add(emission_entry)
    db.commit()
    db.refresh(emission_entry)
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
