import React, { useState } from "react";
import { calculatePublicTransportEmissions } from "../api";

const PublicTransportPage = () => {
    const [formData, setFormData] = useState({
        user_id: localStorage.getItem("user_id"),
        transport_type: "bus",
        miles: "",
        passengers: ""
    });
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await calculatePublicTransportEmissions(formData);
        if (response) {
            setResult(response);
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🚋 Public Transport Emissions Calculator</h2>
            <p>Estimate CO₂ emissions for your trip.</p>

            <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "400px", margin: "auto" }}>
                <label>Transport Type:
                    <select value={formData.transport_type} onChange={(e) => setFormData({ ...formData, transport_type: e.target.value })}>
                        <option value="bus">Bus</option>
                        <option value="subway">Subway</option>
                        <option value="train">Train</option>
                        <option value="airplane">Airplane</option>
                    </select>
                </label>

                <input type="number" placeholder="Miles Traveled" required 
                    value={formData.miles} onChange={(e) => setFormData({ ...formData, miles: e.target.value })} />

                <input type="number" placeholder="Passengers" required 
                    value={formData.passengers} onChange={(e) => setFormData({ ...formData, passengers: e.target.value })} />

                <button type="submit" style={{ background: "#4CAF50", color: "white", padding: "10px" }}>Calculate</button>
            </form>

            {result && (
                <div style={{ marginTop: "20px", padding: "10px", border: "1px solid gray" }}>
                    <h3>Results:</h3>
                    <p><strong>Transport Type:</strong> {result.transport_type}</p>
                    <p><strong>Miles Traveled:</strong> {result.miles}</p>
                    <p><strong>Emissions (lbs per person):</strong> {result.emissions_lbs_per_person}</p>
                </div>
            )}
        </div>
    );
};

export default PublicTransportPage;
