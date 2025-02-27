from pydantic import BaseModel

# 🚗 Fuel Vehicle Request & Response
class FuelVehicleRequest(BaseModel):
    user_id: int
    fuel_type: str
    mpg: float
    miles: float
    passengers: int

class FuelVehicleResponse(BaseModel):
    user_id: int
    fuel_type: str
    mpg: float
    miles: float
    passengers: int
    emissions_lbs_per_person: float

# ⚡ Electric Vehicle Request & Response
class ElectricVehicleRequest(BaseModel):
    user_id: int
    electric_type: str
    miles_per_kwh: float
    miles: float
    passengers: int

class ElectricVehicleResponse(BaseModel):
    user_id: int
    electric_type: str
    miles_per_kwh: float
    miles: float
    passengers: int
    emissions_lbs_per_person: float

# 🚌 Public Transport Request & Response
class PublicTransportRequest(BaseModel):
    user_id: int
    transport_type: str
    miles: float
    passengers: int

class PublicTransportResponse(BaseModel):
    user_id: int 
    transport_type: str
    miles: float
    passengers: int
    emissions_lbs_per_person: float
