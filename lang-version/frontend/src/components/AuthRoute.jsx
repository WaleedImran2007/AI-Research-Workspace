import { useAuth } from '../../Context/AuthContext.jsx';
import { Navigate } from 'react-router-dom';

const AuthRoute = ({ children }) => {
    const { token } = useAuth();

    if(!token) {
        return <Navigate to='/login' replace />;
    }

    return children;
}

export default AuthRoute;