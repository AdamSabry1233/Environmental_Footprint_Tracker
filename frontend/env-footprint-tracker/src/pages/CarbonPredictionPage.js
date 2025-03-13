import React, { useEffect, useState } from "react";
import { predictCarbonFootprint, getUserTrips } from "../api";

const CarbonPredictionPage = () => {
    const [prediction, setPrediction] = useState(null);
    const [trips, setTrips] = useState([]);  
    const [loading, setLoading] = useState(true);
    const userId = localStorage.getItem("user_id");

    //  Fetch trips only once when `userId` changes
    useEffect(() => {
        const fetchTrips = async () => {
            if (userId) {
                setLoading(true);
                const tripsData = await getUserTrips(userId);
                console.log("🚗 Logged Trips:", tripsData);
                setTrips(tripsData);
                setLoading(false);
            }
        };
        fetchTrips();
    }, [userId]); //  Run only when userId changes

    //  Fetch prediction only when trips are loaded
    useEffect(() => {
        const fetchPrediction = async () => {
            if (userId && trips.length > 0) {
                console.log("📊 Fetching Carbon Prediction...");
                setLoading(true);
                const data = await predictCarbonFootprint(userId);
                console.log("🔮 Carbon Prediction:", data);
                setPrediction(data);
                setLoading(false);
            }
        };
        fetchPrediction();
    }, [userId, trips.length]); // Run only when trips are updated

    return (
        <div style={{ textAlign: "center", padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
            <h1>📅 Monthly Carbon Footprint Prediction</h1>
            <p>Predict your future carbon footprint based on your past emissions data.</p>

            {loading ? (
                <p>Loading prediction...</p>
            ) : prediction ? (
                <div style={{
                    marginTop: "20px",
                    padding: "15px",
                    border: "1px solid gray",
                    borderRadius: "10px",
                    backgroundColor: "#f4f4f4"
                }}>
                    <h3>🔮 Predicted CO₂ Emissions for the Next Month:</h3>
                    <p style={{ fontSize: "22px", fontWeight: "bold", color: "red" }}>
                        {prediction.predicted_co2_emissions_lbs} lbs
                    </p>
                    <p><strong>🕐 Last Updated:</strong> {new Date().toLocaleString()}</p>
                </div>
            ) : (
                <p>No prediction data available.</p>
            )}
        </div>
    );
};

export default CarbonPredictionPage;
