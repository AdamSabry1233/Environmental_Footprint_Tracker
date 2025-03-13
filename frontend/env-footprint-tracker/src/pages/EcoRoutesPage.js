import { getEcoFriendlyRoutes } from "../api";  
import React, { useState } from "react";

const EcoRoutesPage = () => {
    const [routes, setRoutes] = useState([]);
    const [optimalRoute, setOptimalRoute] = useState(null); //  Store optimal route separately
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [error, setError] = useState("");

    const fetchEcoRoutes = async () => {
        setError(""); // Reset error message
        const userId = localStorage.getItem("user_id"); // Ensure correct user ID retrieval

        if (!userId) {
            setError("Please log in to view eco-friendly routes.");
            return;
        }

        const data = await getEcoFriendlyRoutes(userId, origin, destination);
        
        if (data.error) {
            setError("Failed to fetch eco-routes.");
        } else {
            setRoutes(data.all_routes || []); //  Store all routes
            setOptimalRoute(data.optimal_route || null); //  Store best route separately
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🚲 Eco-Friendly Routes</h2>
            <p>Find the most sustainable travel routes.</p>

            {error && <p style={{ color: "red" }}>{error}</p>}

            <input 
                type="text" 
                placeholder="Enter Origin" 
                value={origin} 
                onChange={(e) => setOrigin(e.target.value)}
                style={{ padding: "10px", margin: "5px", borderRadius: "5px", border: "1px solid #ccc" }}
            />
            <input 
                type="text" 
                placeholder="Enter Destination" 
                value={destination} 
                onChange={(e) => setDestination(e.target.value)}
                style={{ padding: "10px", margin: "5px", borderRadius: "5px", border: "1px solid #ccc" }}
            />
            <button 
                onClick={fetchEcoRoutes} 
                style={{ background: "#4CAF50", color: "white", padding: "10px", borderRadius: "5px", cursor: "pointer" }}
            >
                Find Routes
            </button>

            {/* Display the Optimal Route Separately */}
            {optimalRoute && (
                <div style={{ marginTop: "20px", padding: "10px", border: "2px solid green", borderRadius: "5px" }}>
                    <h3>🌿 Best Eco-Friendly Route</h3>
                    <p><strong>Summary:</strong> {optimalRoute.summary}</p>
                    <p><strong>Distance:</strong> {optimalRoute.distance_miles.toFixed(2)} miles</p>
                    <p><strong>Duration:</strong> {optimalRoute.duration_minutes.toFixed(1)} minutes</p>
                </div>
            )}

            {/* Display All Available Routes */}
            <div>
                {routes.length > 0 && (
                    <ul style={{ listStyleType: "none", padding: 0 }}>
                        {routes.map((route, index) => (
                            <li key={index} style={{ padding: "10px", borderBottom: "1px solid #ddd" }}>
                                🌍 <strong>Route {index + 1}</strong>: {route.distance_miles.toFixed(2)} miles - {route.duration_minutes.toFixed(1)} minutes
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default EcoRoutesPage;
