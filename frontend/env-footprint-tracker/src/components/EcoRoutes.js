import React, { useState } from "react";
import { getEcoFriendlyRoutes } from "../api";

const EcoRoutes = ({ userId }) => {
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [routes, setRoutes] = useState([]);

    const handleSearch = async () => {
        const data = await getEcoFriendlyRoutes(userId, origin, destination, "DRIVE");
        setRoutes(data?.all_routes || []);
    };

    return (
        <div>
            <h2>Eco-Friendly Routes</h2>
            <input type="text" placeholder="Origin" value={origin} onChange={(e) => setOrigin(e.target.value)} />
            <input type="text" placeholder="Destination" value={destination} onChange={(e) => setDestination(e.target.value)} />
            <button onClick={handleSearch}>Find Routes</button>
            <ul>
                {routes.length > 0 ? (
                    routes.map((route, index) => (
                        <li key={index}>
                            Distance: {route.distance_miles} miles
                        </li>
                    ))
                ) : (
                    <p>No routes found.</p>
                )}
            </ul>
        </div>
    );
};

export default EcoRoutes;
