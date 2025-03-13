import React, { useState } from "react";
import { loginUser } from "../api";
import { useNavigate } from "react-router-dom";
import "../styles.css"; // Import the CSS file

const LoginPage = () => {
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await loginUser(formData);
        if (response) {
            alert("✅ Login successful!");
            localStorage.setItem("user_id", response.user_id); //  Store user ID
            navigate("/dashboard"); // Redirect to Dashboard
        } else {
            setError(" Invalid email or password. Please try again.");
        }
    };

    return (
        <div style={{
            display: "flex", flexDirection: "column", alignItems: "center", 
            justifyContent: "center", height: "100vh", textAlign: "center"
        }}>
            <h1> Environmental Footprint Tracker</h1>
            <p>Enter your credentials to access your dashboard.</p>

            {error && <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>}

            <form onSubmit={handleSubmit} style={{
                display: "flex", flexDirection: "column", gap: "15px", width: "300px"
            }}>
                <input 
                    type="email" 
                    placeholder="📧 Email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    style={{ padding: "10px", borderRadius: "5px", border: "1px solid gray" }}
                />

                <input 
                    type="password" 
                    placeholder="🔒 Password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    style={{ padding: "10px", borderRadius: "5px", border: "1px solid gray" }}
                />

                <button type="submit" style={{
                    backgroundColor: "#4CAF50", color: "white", padding: "10px", border: "none",
                    borderRadius: "5px", cursor: "pointer", fontSize: "16px"
                }}>
                    Login
                </button>
            </form>

            <p style={{ marginTop: "10px" }}>
                Don't have an account? <a href="/create-user" style={{ color: "#007bff" }}>Sign Up</a>
            </p>
        </div>
    );
};

export default LoginPage;
