import React, { useState } from "react";
import { calculateElectricVehicleEmissions } from "../api";

const ElectricVehicleCalculator = ({ userId }) => {
    const [electricType, setElectricType] = useState("electric_car");
    const [milesPerKwh, setMilesPerKwh] = useState("");
    const [miles, setMiles] = useState("");
    const [passengers, setPassengers] = useState(1);
    const [result, setResult] = useState(null);

    const handleCalculate = async () => {
        const response = await calculateElectricVehicleEmissions({
            user_id: userId,
            electric_type: electricType,
            miles_per_kwh: milesPerKwh,
            miles,
            passengers,
        });
        setResult(response);
    };

    return (
        <div>
            <h2>Electric Vehicle Emissions Calculator ⚡</h2>
            <select value={electricType} onChange={(e) => setElectricType(e.target.value)}>
                <option value="electric_car">Electric Car</option>
                <option value="electric_scooter">Electric Scooter</option>
                <option value="electric_bike">Electric Bike</option>
            </select>
            <input
                type="text"
                placeholder="Miles traveled"
                value={miles}
                onChange={(e) => setMiles(e.target.value)}
            />
            <input
                type="text"
                placeholder="Miles per kWh"
                value={milesPerKwh}
                onChange={(e) => setMilesPerKwh(e.target.value)}
            />
            <input
                type="number"
                placeholder="Passengers"
                value={passengers}
                onChange={(e) => setPassengers(e.target.value)}
            />
            <button onClick={handleCalculate}>Calculate</button>
            {result && <p>Emissions: {result.emissions_lbs_per_person} lbs</p>}
        </div>
    );
};

export default ElectricVehicleCalculator;
