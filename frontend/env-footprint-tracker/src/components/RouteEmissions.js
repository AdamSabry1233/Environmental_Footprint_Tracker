import React, { useState } from "react";
import { calculateRouteEmissions } from "../api";

const RouteEmissions = ({ userId }) => {
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [result, setResult] = useState(null);

    const handleCalculate = async () => {
        const params = { origin, destination, mode: "driving", user_id: userId };
        const data = await calculateRouteEmissions(params);
        setResult(data);
    };

    return (
        <div>
            <h2>Route Emissions Calculator</h2>
            <input type="text" placeholder="Origin" value={origin} onChange={(e) => setOrigin(e.target.value)} />
            <input type="text" placeholder="Destination" value={destination} onChange={(e) => setDestination(e.target.value)} />
            <button onClick={handleCalculate}>Calculate</button>
            {result && <p>Emissions: {result.estimated_emissions_lbs} lbs</p>}
        </div>
    );
};

export default RouteEmissions;
