import React, { useState } from "react";
import { calculatePublicTransportEmissions } from "../api";

const PublicTransportCalculator = ({ userId }) => {
    const [transportType, setTransportType] = useState("bus");
    const [miles, setMiles] = useState("");
    const [passengers, setPassengers] = useState(1);
    const [result, setResult] = useState(null);

    const handleCalculate = async () => {
        const response = await calculatePublicTransportEmissions({
            user_id: userId,
            transport_type: transportType,
            miles,
            passengers,
        });
        setResult(response);
    };

    return (
        <div>
            <h2>Public Transport Emissions Calculator</h2>
            <select value={transportType} onChange={(e) => setTransportType(e.target.value)}>
                <option value="bus">Bus</option>
                <option value="diesel_bus">Diesel Bus</option>
                <option value="subway">Subway</option>
                <option value="high_speed_rail">High-Speed Rail</option>
                <option value="long_haul_flight">Long-Haul Flight</option>
                <option value="train">Train</option>
                <option value="airplane">Airplane</option>
                <option value="ferry">Ferry</option>
            </select>
            <input type="text" placeholder="Miles traveled" value={miles} onChange={(e) => setMiles(e.target.value)} />
            <input type="number" placeholder="Passengers" value={passengers} onChange={(e) => setPassengers(e.target.value)} />
            <button onClick={handleCalculate}>Calculate</button>
            {result && <p>Emissions: {result.emissions_lbs_per_person} lbs</p>}
        </div>
    );
};

export default PublicTransportCalculator;
