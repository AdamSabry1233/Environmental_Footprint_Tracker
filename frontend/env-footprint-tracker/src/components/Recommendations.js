import React, { useEffect, useState } from "react";
import { getRecommendations } from "../api";

const Recommendations = ({ userId }) => {
    const [recommendations, setRecommendations] = useState([]);

    useEffect(() => {
        async function fetchRecommendations() {
            const data = await getRecommendations(userId);
            setRecommendations(data?.recommendations || []);
        }
        fetchRecommendations();
    }, [userId]);

    return (
        <div>
            <h2>AI Recommendations</h2>
            {recommendations.length > 0 ? (
                <ul>
                    {recommendations.map((rec, index) => (
                        <li key={index}>{rec.recommendation_text}</li>
                    ))}
                </ul>
            ) : (
                <p>No recommendations available.</p>
            )}
        </div>
    );
};

export default Recommendations;
