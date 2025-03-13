import React, { useEffect, useState } from "react";
import { getUserProgress } from "../api";

const ProgressTracker = ({ userId }) => {
    const [progress, setProgress] = useState(null);

    useEffect(() => {
        async function fetchProgress() {
            const data = await getUserProgress(userId);
            setProgress(data);
        }
        fetchProgress();
    }, [userId]);

    return (
        <div>
            <h2>Progress Tracker</h2>
            {progress ? (
                <div>
                    <p>Goal: {progress.goal}</p>
                    <p>Baseline Emissions: {progress.baseline_emissions} lbs</p>
                    <p>Current Emissions: {progress.current_emissions} lbs</p>
                    <p>Progress: {progress.progress_percentage}%</p>
                </div>
            ) : (
                <p>Loading progress...</p>
            )}
        </div>
    );
};

export default ProgressTracker;
