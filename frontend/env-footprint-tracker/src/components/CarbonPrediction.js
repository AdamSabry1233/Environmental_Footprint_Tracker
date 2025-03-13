import React, { useEffect, useState } from "react";
import { predictCarbonFootprint } from "../api";

const CarbonPrediction = ({ userId }) => {
    const [prediction, setPrediction] = useState(null);

    useEffect(() => {
        async function fetchPrediction() {
            const data = await predictCarbonFootprint(userId);
            setPrediction(data);
        }
        fetchPrediction();
    }, [userId]);

    return (
        <div>
            <h2>Carbon Footprint Prediction</h2>
            {prediction ? (
                <p>Predicted CO₂ emissions: {prediction.predicted_co2_emissions_lbs} lbs</p>
            ) : (
                <p>Loading prediction...</p>
            )}
        </div>
    );
};

export default CarbonPrediction;
