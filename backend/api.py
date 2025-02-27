from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models.emission_calculator import CarbonCalculator
from .dependencies import get_db # Importing the dependency for database handling
from backend.schemas import FuelVehicleRequest, FuelVehicleResponse, ElectricVehicleRequest, ElectricVehicleResponse, PublicTransportRequest, PublicTransportResponse
from sqlalchemy.orm import Session
from backend.models import EmissionHistory, User
from fastapi import HTTPException

app = FastAPI()
calculator = CarbonCalculator()

@app.post("/calculate/fuel_vehicle", response_model=FuelVehicleResponse)
def calculate_fuel_vehicle_emissions(request: FuelVehicleRequest, db: Session = Depends(get_db)):

    """
    API endpoint to calculate emissions for fuel-based vehicles (gasoline, diesel, hybrid_car, motorcycle, ridshare_solo, rideshare_duo).
    """
    user = db.query(User).filter(User.id == request.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    emissions = calculator.estimate_fuel_vehicle_emissions(request.fuel_type, request.mpg, request.miles, request.passengers)

    #Saves to the database
    emission_entry = EmissionHistory(
        user_id=request.user_id,
        category = "fuel_vehicle",
        emission_value=emissions
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
        user_id=1,
        category = "electric_vehicle",
        emission_value=emissions
    )
    db.add(emission_entry)
    db.commit()

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
        user_id=1,
        category = "public_transport",
        emission_value=emissions
    )
    db.add(emission_entry)
    db.commit()
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
