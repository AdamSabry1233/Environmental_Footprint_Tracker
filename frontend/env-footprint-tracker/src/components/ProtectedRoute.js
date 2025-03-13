import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { getUserId } from "../api";  // ✅ Check if user is logged in

const ProtectedRoute = () => {
    return getUserId() ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
