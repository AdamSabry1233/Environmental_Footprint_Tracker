import React, { useState } from "react";
import { submitRecommendationFeedback } from "../api";

const FeedbackForm = ({ userId, recommendationId }) => {
    const [feedback, setFeedback] = useState("");
    const [accepted, setAccepted] = useState(false);
    const [message, setMessage] = useState("");

    const handleSubmit = async () => {
        const response = await submitRecommendationFeedback(userId, recommendationId, accepted, feedback);
        setMessage(response?.message || "Feedback submission failed.");
    };

    return (
        <div>
            <h3>Submit Feedback</h3>
            <label>
                <input type="checkbox" checked={accepted} onChange={() => setAccepted(!accepted)} />
                Accept Recommendation?
            </label>
            <textarea
                placeholder="Your feedback..."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
            />
            <button onClick={handleSubmit}>Submit</button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default FeedbackForm;
