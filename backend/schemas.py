from pydantic import BaseModel

# 🚗 Fuel Vehicle Request & Response
class FuelVehicleRequest(BaseModel):
    fuel_type: str
    mpg: float
    miles: float
    passengers: int

class FuelVehicleResponse(BaseModel):
    fuel_type: str
    mpg: float
    miles: float
    passengers: int
    emissions_lbs_per_person: float

# ⚡ Electric Vehicle Request & Response
class ElectricVehicleRequest(BaseModel):
    miles_per_kwh: float
    miles: float
    passengers: int

class ElectricVehicleResponse(BaseModel):
    miles_per_kwh: float
    miles: float
    passengers: int
    emissions_lbs_per_person: float

# 🚌 Public Transport Request & Response
class PublicTransportRequest(BaseModel):
    transport_type: str
    miles: float
    passengers: int

class PublicTransportResponse(BaseModel):
    transport_type: str
    miles: float
    passengers: int
    emissions_lbs_per_person: float
