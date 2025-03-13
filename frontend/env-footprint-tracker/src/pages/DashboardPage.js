import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getUserId, logTrip, getUserTrips } from "../api";

const DashboardPage = () => {
    const navigate = useNavigate();
    const userId = getUserId();
    const [trips, setTrips] = useState([]);
    const [tripData, setTripData] = useState({
        origin: "",
        destination: "",
        transport_mode: "driving",  // Updated to match FastAPI field
        fuel_type: "",
        passengers: 1,
        miles_per_kwh: null,  // Default to null for non-electric vehicles
        distance_miles: ""
    });

    // Fetch user's trips when the page loads
    useEffect(() => {
        const fetchTrips = async () => {
            if (userId) {
                const data = await getUserTrips(userId);
                setTrips(data || []);
            }
        };
        fetchTrips();
    }, [userId]);

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
    
        //  Constructing request data properly
        const tripPayload = {
            user_id: userId,  // Ensure user_id is included
            origin: tripData.origin,
            destination: tripData.destination,
            transport_mode: tripData.transport_mode,  // Updated field name
            fuel_type: tripData.fuel_type || null,
            passengers: tripData.passengers,
            miles_per_kwh: tripData.transport_mode === "electric" ? tripData.miles_per_kwh : null,
            distance_miles: parseFloat(tripData.distance_miles)
        };

        console.log("Logging trip with payload:", tripPayload); // Debugging

        const response = await logTrip(tripPayload);

        if (response) {
            alert(`Trip logged successfully! CO₂: ${response.emission_value} lbs`);
            setTrips([...trips, response]); // Add to list dynamically
        } else {
            alert("Failed to log trip. Check console for details.");
        }
    };

    // Handle logout
    const handleLogout = () => {
        localStorage.removeItem("user_id");
        navigate("/login");
    };

    return (
        <div style={{ textAlign: "center", padding: "30px" }}>
            <h1>🌱 Welcome to Your Environmental Footprint Tracker</h1>
            <p><strong>User ID:</strong> {userId}</p>

            {/* Trip Logging Form */}
            <h2>🚗 Log a New Trip</h2>
            <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "400px", margin: "0 auto" }}>
                <input type="text" placeholder="Origin" required onChange={(e) => setTripData({ ...tripData, origin: e.target.value })} />
                <input type="text" placeholder="Destination" required onChange={(e) => setTripData({ ...tripData, destination: e.target.value })} />
                <select onChange={(e) => setTripData({ ...tripData, transport_mode: e.target.value })}>
                    <option value="driving">Driving</option>
                    <option value="electric">Electric Vehicle</option>
                    <option value="public_transport">Public Transport</option>
                    <option value="biking">Biking</option>
                    <option value="walking">Walking</option>
                </select>
                {tripData.transport_mode === "electric" && (
                    <input type="number" placeholder="Miles per kWh" onChange={(e) => setTripData({ ...tripData, miles_per_kwh: e.target.value })} />
                )}
                {tripData.transport_mode !== "biking" && tripData.transport_mode !== "walking" && (
                    <input type="text" placeholder="Fuel Type (Gasoline, Diesel, Electric, etc.)" onChange={(e) => setTripData({ ...tripData, fuel_type: e.target.value })} />
                )}
                <input type="number" placeholder="Passengers" min="1" required onChange={(e) => setTripData({ ...tripData, passengers: parseInt(e.target.value) })} />
                <input type="number" placeholder="Distance (miles)" required onChange={(e) => setTripData({ ...tripData, distance_miles: parseFloat(e.target.value) })} />
                <button type="submit">Log Trip</button>
            </form>

            {/* Display User Trips */}
            <h2>📍 Your Logged Trips</h2>
            {trips.length > 0 ? (
                <ul style={{ listStyleType: "none", padding: 0 }}>
                    {trips.map((trip, index) => (
                        <li key={index}>
                            <strong>{trip.origin} ➝ {trip.destination}</strong> | 
                            Mode: <strong>{trip.transport_mode}</strong> |  
                            CO₂: <strong>{trip.emission_value !== undefined ? trip.emission_value.toFixed(2) : "N/A"} lbs</strong>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No trips logged yet.</p>
            )}


            {/* Navigation Buttons */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "20px" }}>
                <div>
                    <h3>📊 Carbon Tracking & AI Insights</h3>
                    <Link to="/progress"><button>Track My Progress</button></Link>
                    <Link to="/carbon-prediction"><button>Carbon Footprint Prediction</button></Link>
                </div>
                <div>
                    <h3>🤖 AI-Powered Sustainability</h3>
                    <Link to="/chatbot"><button>Chat with AI</button></Link>
                    {/*  <Link to="/recommendations"><button>AI Recommendations</button></Link>-->*/}
                </div>
                <div>
                    <h3>🚗 Transportation & Emissions</h3>
                    <Link to="/route-emissions"><button>Route Emissions</button></Link>
                    <Link to="/vehicle-calculator"><button>Gasoline Vehicle Calculator</button></Link>
                    <Link to="/public-transport"><button>Public Transport Calculator</button></Link>
                    <Link to="/electric-vehicle"><button>Electric Vehicle Calculator</button></Link>
                </div>
                <div>
                    <h3>🌍 Eco-Friendly Choices</h3>
                    <Link to="/eco-routes"><button>Determine Route Distance</button></Link>
                  {/*  <Link to="/feedback"><button>Give Feedback</button></Link>*/}
                </div>
            </div>

            {/* Logout Button */}
            <button 
                onClick={handleLogout} 
                style={{ marginTop: "30px", background: "red", color: "white", padding: "10px 20px", border: "none", borderRadius: "5px" }}
            >
                Logout
            </button>
        </div>
    );
};

export default DashboardPage;
