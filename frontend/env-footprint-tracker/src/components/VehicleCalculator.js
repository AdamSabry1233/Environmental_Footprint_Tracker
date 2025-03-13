import React, { useState } from "react";
import { calculateFuelVehicleEmissions, calculateElectricVehicleEmissions } from "../api";

const VehicleCalculator = ({ userId }) => {
    const [vehicleType, setVehicleType] = useState("gasoline_car");
    const [miles, setMiles] = useState("");
    const [mpg, setMpg] = useState("");
    const [result, setResult] = useState(null);

    const handleCalculate = async () => {
        let response;
        if (vehicleType.includes("electric")) {
            response = await calculateElectricVehicleEmissions({ user_id: userId, electric_type: vehicleType, miles_per_kwh: mpg, miles });
        } else {
            response = await calculateFuelVehicleEmissions({ user_id: userId, fuel_type: vehicleType, mpg, miles, passengers: 1 });
        }
        setResult(response);
    };

    return (
        <div>
            <h2>Vehicle Emissions Calculator</h2>
            <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)}>
                <option value="gasoline_car">Gasoline Car</option>
                <option value="diesel_car">Diesel Car</option>
                <option value="hybrid_car">Hybrid Car</option>
                <option value="electric_car">Electric Car</option>
            </select>
            <input type="text" placeholder="Miles traveled" value={miles} onChange={(e) => setMiles(e.target.value)} />
            <input type="text" placeholder="MPG or Miles/kWh" value={mpg} onChange={(e) => setMpg(e.target.value)} />
            <button onClick={handleCalculate}>Calculate</button>
            {result && <p>Emissions: {result.emissions_lbs_per_person} lbs</p>}
        </div>
    );
};

export default VehicleCalculator;
