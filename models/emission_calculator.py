class CarbonCalculator:
    def __init__(self):
        """
        Initializes the Carbon Calculator with updated emission factors 
        for transportation activities based on fuel efficiency and energy sources.
        Sources: EPA, IPCC, FAA, national transportation & energy reports.
        """
        # 🚗 Emission factors (lbs CO2 per mile per vehicle)
        self.emission_factors = {
            # Fuel-Based Vehicles (lbs CO₂ per mile per vehicle)
            "gasoline_car": 0.89,  # Solo driver (~25 MPG)
            "diesel_car": 1.02,  # Diesel car (~30 MPG)
            "hybrid_car": 0.43,  # Hybrid (~50 MPG)
            "motorcycle": 0.46,  # (~55 MPG)
            "rideshare_solo": 0.89,  # Same as gasoline car if alone
            "rideshare_shared": 0.45,  # Assumes 2+ people sharing

            # Public Transport (lbs CO₂ per mile per vehicle)
            "bus": 6.8,  # Public transit bus
            "diesel_bus": 16,  # Older diesel buses
            "train": 200,  # Passenger rail (Amtrak)
            "subway": 80,  # Urban transit systems
            "high_speed_rail": 100,  # High-speed electric rail
            "airplane": 54000,  # Short-haul flights
            "long_haul_flight": 172000,  # More efficient over long distances
            "ferry": 300,  # Boat/ferry transport

            # Electric Vehicles (lbs CO₂ per mile)
            "electric_car": 0.06,  # EV based on CA grid
            "electric_scooter": 0.02,  
            "electric_bike": 0.01,  

            # No CO2 emissions
            "bike": 0.00,  
            "walking": 0.00  
        }

        #  CO₂ per kWh of electricity;
        self.co2_per_kwh = 0.450  # U.S. average grid emissions

        #  CO₂ per gallon of fuel burned
        self.co2_per_gallon = {
            "gasoline": 19.6,  # lbs CO2 per gallon of gasoline burned
            "diesel": 22.4   # lbs CO2 per gallon of diesel burned
        }

    def estimate_fuel_vehicle_emissions(self, fuel_type: str, mpg: float, miles: float, passengers: int = 1) -> float:
        """
        Estimates CO₂ emissions for fuel-based vehicles, including:
        - gasoline_car, diesel_car, hybrid_car, motorcycle, rideshare_solo, rideshare_shared.
        - Uses per-mile emission factors if available, else calculates using mpg.

        Args:
        - fuel_type (str): Type of fuel-based vehicle.
        - mpg (float): Fuel efficiency (miles per gallon).
        - miles (float): Distance traveled.
        - passengers (int): Number of people in the vehicle.
        """
        if passengers <= 0:
            passengers = 1  # Avoid division by zero

        # If fuel_type has a direct per-mile emission factor, use it
        if fuel_type in self.emission_factors:
            total_emissions = self.emission_factors[fuel_type] * miles
        elif fuel_type in self.co2_per_gallon and mpg > 0:
            # If not in emission_factors, calculate based on fuel gallons burned
            total_emissions = (self.co2_per_gallon[fuel_type] / mpg) * miles
        else:
            return 0  # Invalid fuel type

        return total_emissions / passengers  # Distribute emissions


    def estimate_electric_vehicle_emissions(self, electric_type: str, miles_per_kwh: float, miles: float, passengers: int = 1) -> float:
        """
        Estimates CO₂ emissions for electric vehicles (EVs, electric trains, subways).
        - miles_per_kwh: Efficiency of the EV (miles per kWh)
        - miles: Distance driven
        - passengers: Number of people in the vehicle (to distribute emissions)
        """
        if passengers <= 0:
            passengers = 1  # Avoid division by zero

        if electric_type in self.emission_factors:
            total_emissions = self.emission_factors[electric_type] * miles
        elif miles_per_kwh > 0:
            total_emissions = (self.co2_per_kwh / miles_per_kwh) * miles
        else:
            return 0

        return total_emissions / passengers

    def estimate_public_transport_emissions(self, transport_type: str, miles: float, passengers: int = 1) -> float:
        """
        Estimates CO₂ emissions for public transport (buses, trains, airplanes, ferries).
        - transport_type: Bus, train, subway, plane, ferry, etc.
        - miles: Distance traveled
        - passengers: Number of people sharing the transport
        """
        if passengers <= 0:
            passengers = 1  # Avoid division by zero

        return self.emission_factors.get(transport_type, 0) * miles / passengers
    

    def calculate_co2_savings(self, default_route: dict, eco_route: dict) -> float:
        """
        Calculates CO₂ saved by choosing an eco-friendly route.

        Args:
            default_route (dict): {'mode': str, 'distance_miles': float}
            eco_route (dict): {'mode': str, 'distance_miles': float}

        Returns:
            float: CO₂ savings in lbs
        """
        co2_default = self.emission_factors.get(default_route["mode"], 0.89) * default_route["distance_miles"]
        co2_eco = self.emission_factors.get(eco_route["mode"], 0.89) * eco_route["distance_miles"]
        return round(co2_default - co2_eco, 2)  # CO₂ saved



