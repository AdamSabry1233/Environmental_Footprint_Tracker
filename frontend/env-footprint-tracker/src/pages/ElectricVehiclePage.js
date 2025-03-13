import React, { useState } from "react";
import { calculateElectricVehicleEmissions } from "../api";

const ElectricVehiclePage = () => {
    const [formData, setFormData] = useState({
        user_id: localStorage.getItem("user_id"),
        electric_type: "electric_car",
        miles: "",
        miles_per_kwh: ""
    });
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await calculateElectricVehicleEmissions(formData);
        if (response) setResult(response);
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🔌 Electric Vehicle Emissions Calculator</h2>
            <form onSubmit={handleSubmit} style={{ maxWidth: "400px", margin: "auto" }}>
                <input type="number" placeholder="Miles Driven" required
                    value={formData.miles} onChange={(e) => setFormData({ ...formData, miles: e.target.value })} />
                <input type="number" placeholder="Miles per kWh" required
                    value={formData.miles_per_kwh} onChange={(e) => setFormData({ ...formData, miles_per_kwh: e.target.value })} />
                <button type="submit" style={{ background: "#4CAF50", color: "white", padding: "10px" }}>
                    Calculate
                </button>
            </form>

            {result && <p>Estimated Emissions: {result.emissions_lbs_per_person} lbs CO₂</p>}
        </div>
    );
};

export default ElectricVehiclePage;
