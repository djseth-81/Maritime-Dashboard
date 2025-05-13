import { Navigate } from "react-router-dom"

function isAuthenticated() {
    return sessionStorage.getItem("token") != null;
}

export default function ProtectedRoute({ component, isAuthRequired = true }) {
    if (isAuthRequired && !isAuthenticated()) {
        return <Navigate to="/login" replace />;
    } else {
        return component
    }
}

