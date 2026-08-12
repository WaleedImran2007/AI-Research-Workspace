import { useAuth } from "../../Context/AuthContext.jsx";
import { Navigate } from "react-router-dom";

const ProtectedRoute =({ allowedRoles, children }) => {
    const { isAuthenticated, user } = useAuth();

    if(!isAuthenticated) {
        return <Navigate to='/login' replace />;
    }

    if(allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to='/unauthorized' replace />;
    }

    return children;
}