import React, { useState, useEffect } from "react";
import { getRecommendations } from "../api";

const RecommendationsPage = () => {
    const [recommendations, setRecommendations] = useState([]);
    const userId = localStorage.getItem("user_id");

    useEffect(() => {
        const fetchRecommendations = async () => {
            const data = await getRecommendations(userId);
            if (data) setRecommendations(data.recommendations || []);
        };
        fetchRecommendations();
    }, [userId]);

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>💡 AI Recommendations</h2>
            <p>Personalized suggestions to reduce your carbon footprint.</p>

            {recommendations.length > 0 ? (
                <ul style={{ listStyle: "none", padding: "0" }}>
                    {recommendations.map((rec, index) => (
                        <li key={index} style={{ padding: "10px", borderBottom: "1px solid #ccc" }}>
                            <strong>💬 {rec.strategy}</strong> <br />
                            <small>Category: {rec.category} | Savings: {rec.potential_savings} lbs CO₂</small>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No recommendations available yet.</p>
            )}
        </div>
    );
};

export default RecommendationsPage;
