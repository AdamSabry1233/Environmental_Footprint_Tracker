import React, { useState } from "react";
import { calculateFuelVehicleEmissions } from "../api";

const VehicleCalculatorPage = () => {
    const [formData, setFormData] = useState({
        user_id: localStorage.getItem("user_id"),
        fuel_type: "gasoline_car",
        miles: "",
        mpg: "",
        passengers: ""
    });
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await calculateFuelVehicleEmissions(formData);
        if (response) {
            setResult(response);
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🚗 Vehicle Emissions Calculator</h2>
            <p>Enter your trip details to estimate CO₂ emissions.</p>
            
            <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "400px", margin: "auto" }}>
                <label>Fuel Type:
                    <select value={formData.fuel_type} onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value })}>
                        <option value="gasoline_car">Gasoline Car</option>
                        <option value="diesel_car">Diesel Car</option>
                        <option value="hybrid_car">Hybrid Car</option>
                        <option value="motorcycle">Motorcycle</option>
                    </select>
                </label>

                <input type="number" placeholder="Miles Driven" required 
                    value={formData.miles} onChange={(e) => setFormData({ ...formData, miles: e.target.value })} />

                <input type="number" placeholder="MPG (Fuel Efficiency)" required 
                    value={formData.mpg} onChange={(e) => setFormData({ ...formData, mpg: e.target.value })} />

                <input type="number" placeholder="Number of Passengers" required 
                    value={formData.passengers} onChange={(e) => setFormData({ ...formData, passengers: e.target.value })} />

                <button type="submit" style={{ background: "#4CAF50", color: "white", padding: "10px" }}>Calculate</button>
            </form>

            {result && (
                <div style={{ marginTop: "20px", padding: "10px", border: "1px solid gray" }}>
                    <h3>Results:</h3>
                    <p><strong>Fuel Type:</strong> {result.fuel_type}</p>
                    <p><strong>Miles Driven:</strong> {result.miles}</p>
                    <p><strong>Emissions (lbs per person):</strong> {result.emissions_lbs_per_person}</p>
                </div>
            )}
        </div>
    );
};

export default VehicleCalculatorPage;
