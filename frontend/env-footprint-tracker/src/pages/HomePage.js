import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { getUserId } from "../api";
import "../styles.css"; // Import the CSS file

const HomePage = () => {
    const navigate = useNavigate();
    const userId = getUserId(); // Check if user is logged in

    const handleLogout = () => {
        localStorage.removeItem("user_id");
        navigate("/login");
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h1>🌍 Welcome to the Environmental Footprint Tracker</h1>
            
            {!userId ? (
                <div>
                    <p>Join us in tracking & reducing your carbon footprint with AI-powered insights.</p>
                    <button onClick={() => navigate("/create-user")}>Sign Up</button>
                    <button onClick={() => navigate("/login")}>Login</button>
                </div>
            ) : (
                <div>
                    <h2>Welcome back! 🌱</h2>
                    <p>Use AI insights & tracking tools to lower your environmental impact.</p>
                    
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px", marginTop: "20px" }}>
                        <div>
                            <h3>📊 My Carbon Footprint</h3>
                            <Link to="/progress"><button>Track My Progress</button></Link>
                            <Link to="/carbon-prediction"><button>Predict My Carbon Footprint</button></Link>
                        </div>

                        <div>
                            <h3>🤖 AI Sustainability Advisor</h3>
                            <Link to="/chatbot"><button>Chat with AI</button></Link>
                        </div>

                        <div>
                            <h3>💡 Smart AI Recommendations</h3>
                            <Link to="/recommendations"><button>See AI Suggestions</button></Link>
                        </div>

                        <div>
                            <h3>🚗 Eco-Friendly Travel</h3>
                            <Link to="/vehicle-calculator"><button>Compare Vehicle Emissions</button></Link>
                            <Link to="/public-transport"><button>Public Transport Calculator</button></Link>
                            <Link to="/eco-routes"><button>Eco-Friendly Routes</button></Link>
                        </div>

                        <div>
                            <h3>💬 Community & Feedback</h3>
                            <Link to="/feedback"><button>Give Feedback</button></Link>
                        </div>
                    </div>

                    <button onClick={handleLogout} style={{ marginTop: "20px" }}>Logout</button>
                </div>
            )}
        </div>
    );
};

export default HomePage;
