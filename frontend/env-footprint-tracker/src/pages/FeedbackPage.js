import { submitRecommendationFeedback } from "../api";  
import React, { useState } from "react";

const FeedbackPage = () => {
    const [recommendationId, setRecommendationId] = useState("");
    const [feedback, setFeedback] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleFeedback = async () => {
        setError("");
        setMessage("");

        const userId = localStorage.getItem("userId");

        if (!userId) {
            setError("Please log in to submit feedback.");
            return;
        }

        if (!recommendationId || !feedback) {
            setError("Please enter recommendation ID and feedback.");
            return;
        }

        const response = await submitRecommendationFeedback(userId, recommendationId, true, feedback);

        if (response.message) {
            setMessage("Feedback submitted successfully!");
        } else {
            setError("Failed to submit feedback.");
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>📣 Give Feedback on AI Recommendations</h2>

            {error && <p style={{ color: "red" }}>{error}</p>}
            {message && <p style={{ color: "green" }}>{message}</p>}

            <input
                type="text"
                placeholder="Recommendation ID"
                value={recommendationId}
                onChange={(e) => setRecommendationId(e.target.value)}
                style={{ padding: "10px", margin: "5px", borderRadius: "5px", border: "1px solid #ccc" }}
            />
            <textarea
                placeholder="Enter your feedback..."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                style={{ padding: "10px", margin: "5px", borderRadius: "5px", border: "1px solid #ccc", width: "100%" }}
            />
            <button 
                onClick={handleFeedback} 
                style={{ background: "#008CBA", color: "white", padding: "10px", borderRadius: "5px", cursor: "pointer" }}
            >
                Submit Feedback
            </button>
        </div>
    );
};

export default FeedbackPage;
