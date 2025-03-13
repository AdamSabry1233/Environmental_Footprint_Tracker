import React, { useState } from "react";
import { createUser } from "../api";
import { useNavigate } from "react-router-dom";

const CreateUserPage = () => {
    const [formData, setFormData] = useState({ username: "", email: "", password: "" });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await createUser(formData);
        
        if (response && response.user_id) {
            setSuccess("🎉 User created successfully! Redirecting to login...");
            setTimeout(() => navigate("/login"), 2000);
        } else {
            setError("⚠️ User creation failed. Email might already exist.");
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px", maxWidth: "400px", margin: "auto", border: "1px solid #ddd", borderRadius: "10px", boxShadow: "2px 2px 10px rgba(0,0,0,0.1)" }}>
            <h2>🚀 Create an Account</h2>
            <p>Start tracking your environmental impact today.</p>

            {error && <p style={{ color: "red" }}>{error}</p>}
            {success && <p style={{ color: "green" }}>{success}</p>}

            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <input
                    type="text"
                    placeholder="Full Name"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                    style={{ padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
                />
                <input
                    type="email"
                    placeholder="Email Address"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    style={{ padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    style={{ padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
                />
                <button type="submit" style={{ background: "#4CAF50", color: "white", padding: "10px", borderRadius: "5px", cursor: "pointer" }}>
                    Create Account
                </button>
            </form>
        </div>
    );
};

export default CreateUserPage;
