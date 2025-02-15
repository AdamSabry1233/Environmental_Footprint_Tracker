from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models.emission_calculator import CarbonCalculator
from .dependencies import get_db # Importing the dependency for database handling
from backend.schemas import FuelVehicleRequest, FuelVehicleResponse, ElectricVehicleRequest, ElectricVehicleResponse, PublicTransportRequest, PublicTransportResponse
from sqlalchemy.orm import Session

app = FastAPI()
calculator = CarbonCalculator()

@app.post("/calculate/fuel_vehicle", response_model=FuelVehicleResponse)
def calculate_fuel_vehicle_emissions(request: FuelVehicleRequest, db: Session = Depends(get_db)):

    """
    API endpoint to calculate emissions for fuel-based vehicles (gasoline, diesel, hybrid, motorcycle, ridshare_solo, rideshare_duo).
    """
    emissions = calculator.estimate_fuel_vehicle_emissions(request.fuel_type, request.mpg, request.miles, request.passengers)
    return FuelVehicleResponse(
        fuel_type=request.fuel_type,
        mpg=request.mpg,
        miles=request.miles,
        passengers=request.passengers,
        emissions_lbs_per_person=emissions
    )

@app.post("/calculate/electric_vehicle", response_model=ElectricVehicleResponse)
def calculate_electric_vehicle_emissions(request: ElectricVehicleRequest, db: Session = Depends(get_db)):
    """
    API endpoint to calculate emissions for electric vehicles ().
    """
    emissions = calculator.estimate_electric_vehicle_emissions(request.miles_per_kwh, request.miles, request.passengers)
    return {
        "miles_per_kwh": request.miles_per_kwh,
        "miles": request.miles,
        "passengers": request.passengers,
        "emissions_lbs_per_person": emissions
    }

@app.post("/calculate/public_transport", response_model=PublicTransportResponse)
def calculate_public_transport_emissions(request: PublicTransportRequest, db: Session = Depends(get_db)):
    """
    API endpoint to calculate emissions for public transport (bus, train, airplane, ferry).
    """
    emissions = calculator.estimate_public_transport_emissions(request.transport_type, request.miles, request.passengers)
    return {
        "transport_type": request.transport_type,
        "miles": request.miles,
        "passengers": request.passengers,
        "emissions_lbs_per_person": emissions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
