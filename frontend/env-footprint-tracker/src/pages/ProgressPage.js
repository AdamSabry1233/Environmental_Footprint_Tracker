import React, { useState, useEffect } from "react";
import { getUserProgress, setProgressGoal } from "../api"; //  Use correct function name

const ProgressPage = () => {
    const [progress, setProgress] = useState(null);
    const [goalInput, setGoalInput] = useState(""); //  Store user's goal input
    const [error, setError] = useState("");
    const userId = localStorage.getItem("user_id");

    useEffect(() => {
        const fetchProgress = async () => {
            const data = await getUserProgress(userId);
            console.log("Fetched progress data:", data); // Debugging log
            if (data) setProgress(data);
        };
        fetchProgress();
    }, [userId]);

    // ✅ Function to set a goal
    const handleSetGoal = async () => {
        if (!goalInput.trim()) {
            setError("Please enter a goal.");
            return;
        }

        const response = await setProgressGoal(userId, goalInput); //  Correct function name
        if (response) {
            alert("🎯 Goal set successfully!");
            setProgress(response); //  Update UI
            setGoalInput(""); //  Clear input
        } else {
            setError("Failed to set goal. Try again.");
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>📊 Progress Tracker</h2>
            <p>Track your sustainability goal and monitor CO₂ reduction.</p>

            {progress ? (
                <div style={{ marginTop: "20px", padding: "15px", border: "1px solid gray" }}>
                    <h3>🎯 Goal: {progress.goal}</h3>
                    <p><strong>Baseline Emissions:</strong> {progress.baseline_emissions} lbs</p>
                    <p><strong>Current Emissions:</strong> {progress.current_emissions} lbs</p>
                    <p><strong>Progress:</strong> {progress.progress_percentage}%</p>
                </div>
            ) : (
                <div>
                    <p>No progress data available. Set a goal to start tracking.</p>
                    {error && <p style={{ color: "red" }}>{error}</p>}
                    <input 
                        type="text" 
                        placeholder="Enter your sustainability goal..." 
                        value={goalInput} 
                        onChange={(e) => setGoalInput(e.target.value)} 
                        style={{ padding: "10px", margin: "10px", borderRadius: "5px", border: "1px solid gray" }}
                    />
                    <button 
                        onClick={handleSetGoal} 
                        style={{ backgroundColor: "#4CAF50", color: "white", padding: "10px", borderRadius: "5px", cursor: "pointer" }}
                    >
                        Set Goal
                    </button>
                </div>
            )}
        </div>
    );
};

export default ProgressPage;
