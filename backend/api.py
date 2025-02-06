from fastapi import FastAPI
from models.emission_calculator import CarbonCalculator

app = FastAPI()
calculator = CarbonCalculator()

@app.post("/calculate/fuel_vehicle")
def calculate_fuel_vehicle_emissions(fuel_type: str, mpg: float, miles: float, passengers: int = 1):
    """
    API endpoint to calculate emissions for fuel-based vehicles (gasoline, diesel).
    """
    emissions = calculator.estimate_fuel_vehicle_emissions(fuel_type, mpg, miles, passengers)
    return {
        "fuel_type": fuel_type,
        "mpg": mpg,
        "miles": miles,
        "passengers": passengers,
        "emissions_lbs_per_person": emissions
    }

@app.post("/calculate/electric_vehicle")
def calculate_electric_vehicle_emissions(miles_per_kwh: float, miles: float, passengers: int = 1):
    """
    API endpoint to calculate emissions for electric vehicles (EVs, electric trains, subways).
    """
    emissions = calculator.estimate_electric_vehicle_emissions(miles_per_kwh, miles, passengers)
    return {
        "miles_per_kwh": miles_per_kwh,
        "miles": miles,
        "passengers": passengers,
        "emissions_lbs_per_person": emissions
    }

@app.post("/calculate/public_transport")
def calculate_public_transport_emissions(transport_type: str, miles: float, passengers: int = 1):
    """
    API endpoint to calculate emissions for public transport (bus, train, airplane, ferry).
    """
    emissions = calculator.estimate_public_transport_emissions(transport_type, miles, passengers)
    return {
        "transport_type": transport_type,
        "miles": miles,
        "passengers": passengers,
        "emissions_lbs_per_person": emissions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
