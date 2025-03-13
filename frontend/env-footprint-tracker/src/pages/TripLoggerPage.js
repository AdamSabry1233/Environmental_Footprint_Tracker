import React, { useState } from "react";
import { logTrip } from "../api";

const TripLoggerPage = () => {
    const [tripData, setTripData] = useState({
        user_id: localStorage.getItem("userId"), 
        origin: "",
        destination: "",
        mode: "driving",
        fuel_type: "",
        passengers: 1,
        miles_per_kwh: "",
        distance_miles: ""
    });
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setMessage("");

        if (!tripData.origin || !tripData.destination || !tripData.distance_miles) {
            setError("Please enter all required fields.");
            return;
        }

        const response = await logTrip(tripData);
        if (response) {
            setMessage("Trip logged successfully!");
        } else {
            setError("Failed to log trip.");
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>🚗 Log Your Trip</h2>
            <p>Track your trips and calculate emissions.</p>

            {error && <p style={{ color: "red" }}>{error}</p>}
            {message && <p style={{ color: "green" }}>{message}</p>}

            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Enter Origin"
                    value={tripData.origin}
                    onChange={(e) => setTripData({ ...tripData, origin: e.target.value })}
                    style={{ padding: "10px", margin: "5px", width: "80%" }}
                />
                <input
                    type="text"
                    placeholder="Enter Destination"
                    value={tripData.destination}
                    onChange={(e) => setTripData({ ...tripData, destination: e.target.value })}
                    style={{ padding: "10px", margin: "5px", width: "80%" }}
                />
                <input
                    type="number"
                    placeholder="Distance in miles"
                    value={tripData.distance_miles}
                    onChange={(e) => setTripData({ ...tripData, distance_miles: e.target.value })}
                    style={{ padding: "10px", margin: "5px", width: "80%" }}
                />

                <select
                    value={tripData.mode}
                    onChange={(e) => setTripData({ ...tripData, mode: e.target.value })}
                    style={{ padding: "10px", margin: "5px", width: "80%" }}
                >
                    <option value="driving">🚗 Driving</option>
                    <option value="electric">⚡ Electric Vehicle</option>
                    <option value="public_transport">🚌 Public Transport</option>
                    <option value="biking">🚲 Biking</option>
                    <option value="walking">🚶 Walking</option>
                </select>

                {tripData.mode === "driving" || tripData.mode === "electric" ? (
                    <>
                        <input
                            type="text"
                            placeholder="Fuel Type (gas, diesel, electric)"
                            value={tripData.fuel_type}
                            onChange={(e) => setTripData({ ...tripData, fuel_type: e.target.value })}
                            style={{ padding: "10px", margin: "5px", width: "80%" }}
                        />
                        <input
                            type="number"
                            placeholder="Passengers"
                            value={tripData.passengers}
                            onChange={(e) => setTripData({ ...tripData, passengers: e.target.value })}
                            style={{ padding: "10px", margin: "5px", width: "80%" }}
                        />
                        {tripData.mode === "electric" && (
                            <input
                                type="number"
                                placeholder="Miles per kWh"
                                value={tripData.miles_per_kwh}
                                onChange={(e) => setTripData({ ...tripData, miles_per_kwh: e.target.value })}
                                style={{ padding: "10px", margin: "5px", width: "80%" }}
                            />
                        )}
                    </>
                ) : null}

                <button
                    type="submit"
                    style={{ background: "#4CAF50", color: "white", padding: "10px", borderRadius: "5px", cursor: "pointer" }}
                >
                    Log Trip
                </button>
            </form>
        </div>
    );
};

export default TripLoggerPage;
