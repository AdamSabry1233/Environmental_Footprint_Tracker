import React, { useState } from "react";
import { calculateElectricVehicleEmissions } from "../api";

const ElectricVehiclePage = () => {
    const [formData, setFormData] = useState({
        electric_type: "electric_car",
        miles: "",
        miles_per_kwh: "",
        passengers: ""
    });
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Ensure correct data types (convert to numbers)
        const payload = {
            electric_type: formData.electric_type,
            miles: parseFloat(formData.miles),
            miles_per_kwh: parseFloat(formData.miles_per_kwh),
            passengers: parseInt(formData.passengers, 10)
        };

        const response = await calculateElectricVehicleEmissions(payload);
        if (response) setResult(response);
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🔌 Electric Vehicle Emissions Calculator</h2>
            <form onSubmit={handleSubmit} style={{ maxWidth: "400px", margin: "auto" }}>
                <select
                    value={formData.electric_type}
                    onChange={(e) => setFormData({ ...formData, electric_type: e.target.value })}
                >
                    <option value="electric_car">Electric Car</option>
                    <option value="electric_scooter">Electric Scooter</option>
                    <option value="electric_bike">Electric Bike</option>
                </select>
                <input
                    type="number"
                    placeholder="Miles Driven"
                    required
                    value={formData.miles}
                    onChange={(e) => setFormData({ ...formData, miles: e.target.value })}
                />
                <input
                    type="number"
                    placeholder="Miles per kWh"
                    required
                    value={formData.miles_per_kwh}
                    onChange={(e) => setFormData({ ...formData, miles_per_kwh: e.target.value })}
                />
                <input
                    type="number"
                    placeholder="Passengers"
                    min="1"
                    required
                    value={formData.passengers}
                    onChange={(e) => setFormData({ ...formData, passengers: e.target.value })}
                />
                <button type="submit" style={{ background: "#4CAF50", color: "white", padding: "10px" }}>
                    Calculate
                </button>
            </form>

            {result && (
                <p>
                    Estimated Emissions:{" "}
                    <strong>{result.emissions_lbs_per_person} lbs CO₂</strong>
                </p>
            )}
        </div>
    );
};

export default ElectricVehiclePage;
