import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8001"; // FastAPI Backend


export const setProgressGoal = async (userId, goal) => {
    try {
        const response = await axios.post(`http://127.0.0.1:8001/progress/set_goal/`, null, {
            params: { user_id: userId, goal }
        });
        return response.data;
    } catch (error) {
        console.error("Error setting progress goal:", error.response?.data || error);
        return null;
    }
};


// ✅ User Login API
export const loginUser = async (userData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/login_user/`, userData);
        localStorage.setItem("user_id", response.data.user_id);  // ✅ Store User ID
        return response.data;
    } catch (error) {
        console.error("Error logging in:", error.response?.data || error);
        return null;
    }
};

export const logTrip = async (tripData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/log_trip/`, tripData);
        return response.data;
    } catch (error) {
        console.error("Error logging trip:", error.response?.data || error);
        return null;
    }
};


// Fetch user trips from the database
export const getUserTrips = async (userId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/get_user_trips/${userId}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching user trips:", error);
        return [];
    }
};


// ✅ Get Logged-In User ID
export const getUserId = () => {
    return localStorage.getItem("user_id");  // ✅ Retrieve User ID
};

// Create a new user
export const createUser = async (userData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/create_user/`, userData);
        return response.data;
    } catch (error) {
        console.error("Error creating user:", error.response?.data || error);
        return null;
    }
};

// Fetch user progress
export const getUserProgress = async (userId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/progress/track_progress/${userId}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching progress:", error);
        return null;
    }
};

// Fetch AI-powered recommendations
export const getRecommendations = async (userId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/get_ai_recommendations/${userId}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        return null;
    }
};

// Send a message to the chatbot
export const sendChatMessage = async (userId, query) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chatbot/`, null, {
            params: { user_id: userId, query }
        });
        return response.data;
    } catch (error) {
        console.error("Chatbot error:", error);
        return null;
    }
};

// Predict future carbon footprint
export const predictCarbonFootprint = async (userId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/predict_carbon_footprint/${userId}`);
        return response.data;
    } catch (error) {
        console.error("Error predicting carbon footprint:", error);
        return null;
    }
};

// Calculate route emissions
export const calculateRouteEmissions = async (params) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/route_emissions/`, { params });
        return response.data;
    } catch (error) {
        console.error("Error calculating route emissions:", error);
        return null;
    }
};

// Get eco-friendly routes
export const getEcoFriendlyRoutes = async (userId, origin, destination, mode) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/eco_friendly_routes/`, {
            params: { user_id: userId, origin, destination, mode }
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching eco-friendly routes:", error);
        return null;
    }
};

// Submit recommendation feedback
export const submitRecommendationFeedback = async (userId, recommendationId, accepted, feedback) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/update_recommendation_feedback`, null, {
            params: { user_id: userId, recommendation_id: recommendationId, accepted, feedback }
        });
        return response.data;
    } catch (error) {
        console.error("Error submitting feedback:", error);
        return null;
    }
};

// Calculate emissions for fuel-based vehicles
export const calculateFuelVehicleEmissions = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/calculate/fuel_vehicle`, data);
        return response.data;
    } catch (error) {
        console.error("Error calculating fuel vehicle emissions:", error);
        return null;
    }
};

// Calculate emissions for electric vehicles
export const calculateElectricVehicleEmissions = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/calculate/electric_vehicle`, data);
        return response.data;
    } catch (error) {
        console.error("Error calculating electric vehicle emissions:", error);
        return null;
    }
};

// Calculate emissions for public transport
export const calculatePublicTransportEmissions = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/calculate/public_transport`, data);
        return response.data;
    } catch (error) {
        console.error("Error calculating public transport emissions:", error);
        return null;
    }
};
