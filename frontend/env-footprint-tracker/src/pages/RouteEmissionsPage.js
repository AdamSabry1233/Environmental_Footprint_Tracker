import React, { useState } from "react";
import { calculateRouteEmissions } from "../api";

const RouteEmissionsPage = () => {
    const [formData, setFormData] = useState({
        user_id: localStorage.getItem("user_id"),
        origin: "",
        destination: "",
        mode: "driving",
    });
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await calculateRouteEmissions(formData);
        if (response) {
            setResult(response);
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🛣️ Route Emissions Calculator</h2>
            <p>Estimate CO₂ emissions for your trip.</p>

            <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "400px", margin: "auto" }}>
                <input type="text" placeholder="Origin" required 
                    value={formData.origin} onChange={(e) => setFormData({ ...formData, origin: e.target.value })} />

                <input type="text" placeholder="Destination" required 
                    value={formData.destination} onChange={(e) => setFormData({ ...formData, destination: e.target.value })} />

                <label>Mode of Transport:
                    <select value={formData.mode} onChange={(e) => setFormData({ ...formData, mode: e.target.value })}>
                        <option value="driving">Driving</option>
                        <option value="transit">Public Transit</option>
                        <option value="bicycling">Bicycling</option>
                        <option value="walking">Walking</option>
                    </select>
                </label>

                <button type="submit" style={{ background: "#4CAF50", color: "white", padding: "10px" }}>Calculate</button>
            </form>

            {result && <div><p>Estimated Emissions: {result.estimated_emissions_lbs} lbs CO₂</p></div>}
        </div>
    );
};

export default RouteEmissionsPage;
