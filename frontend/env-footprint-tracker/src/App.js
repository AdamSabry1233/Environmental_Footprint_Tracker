import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ProgressPage from "./pages/ProgressPage";
import RecommendationsPage from "./pages/RecommendationsPage";
import ChatbotPage from "./pages/ChatbotPage";
import CarbonPredictionPage from "./pages/CarbonPredictionPage";
import RouteEmissionsPage from "./pages/RouteEmissionsPage";
import EcoRoutesPage from "./pages/EcoRoutesPage";
import FeedbackPage from "./pages/FeedbackPage";
import VehicleCalculatorPage from "./pages/VehicleCalculatorPage";
import PublicTransportPage from "./pages/PublicTransportPage";
import ElectricVehiclePage from "./pages/ElectricVehiclePage";
import CreateUserPage from "./pages/CreateUserPage";
import DashboardPage from "./pages/DashboardPage";  
import LoginPage from "./pages/LoginPage";  
import ProtectedRoute from "./components/ProtectedRoute";
import TripLoggerPage from "./pages/TripLoggerPage";  


const App = () => {
    return (
        <Router>
            <Routes>
                {/* Public Routes */}
                <Route path="/" element={<HomePage />} />
                <Route path="/create-user" element={<CreateUserPage />} />
                <Route path="/login" element={<LoginPage />} />

                {/* ✅ Protected Routes (Require Login) */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/progress" element={<ProgressPage />} />
                    <Route path="/recommendations" element={<RecommendationsPage />} />
                    <Route path="/chatbot" element={<ChatbotPage />} />
                    <Route path="/carbon-prediction" element={<CarbonPredictionPage />} />
                    <Route path="/route-emissions" element={<RouteEmissionsPage />} />
                    <Route path="/eco-routes" element={<EcoRoutesPage />} />
                    <Route path="/feedback" element={<FeedbackPage />} />
                    <Route path="/vehicle-calculator" element={<VehicleCalculatorPage />} />
                    <Route path="/public-transport" element={<PublicTransportPage />} />
                    <Route path="/electric-vehicle" element={<ElectricVehiclePage />} />
                    <Route path="/log-trip" element={<TripLoggerPage />} />
                </Route>
            </Routes>
        </Router>
    );
};

export default App;
