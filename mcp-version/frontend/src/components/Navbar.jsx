import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import { useAuth } from "../../Context/AuthContext.jsx";

function Navbar() {
    const { user, logout, isAuthenticated } = useAuth();

    const [showDropdown, setShowDropdown] = useState(false);

    const dropdownRef = useRef(null);

    const navigate = useNavigate();

    useEffect(() => {
        const handleClickOutside = (event) => {
            if(dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        }

        if(showDropdown) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };

    }, [showDropdown]);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav className="bg-blue-600 shadow-md z-50">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

                <Link
                    to="/"
                    className="text-2xl font-bold text-white"
                >
                    AI Research Workspace
                </Link>

                <div className="flex items-center gap-6">

                    <Link
                        to="/"
                        className="text-white hover:text-blue-200"
                    >
                        Home
                    </Link>

                    {isAuthenticated ? (
                        <>
                            <Link
                                to="/collections"
                                className="text-white hover:text-blue-200"
                            >
                                Collections
                            </Link>

                            <Link
                                to="/upload"
                                className="text-white hover:text-blue-200"
                            >
                                Upload
                            </Link>

                            <div className="relative" ref={dropdownRef}>

                                <button
                                    onClick={() =>
                                        setShowDropdown(!showDropdown)
                                    }
                                    className="cursor-pointer rounded-lg bg-white px-4 py-2 font-medium text-blue-600"
                                >
                                    {user.username} ▼
                                </button>

                                {showDropdown && (
                                    <div className="absolute right-0 mt-2 w-40 rounded-lg bg-white shadow-lg">

                                        <Link
                                            to="/profile"
                                            className="block px-4 py-2 hover:bg-gray-100"
                                            onClick={() =>
                                                setShowDropdown(false)
                                            }
                                        >
                                            Profile
                                        </Link>

                                        <button
                                            onClick={handleLogout}
                                            className="block w-full px-4 py-2 text-left hover:bg-gray-100"
                                        >
                                            Logout
                                        </button>

                                    </div>
                                )}

                            </div>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/login"
                                className="text-white hover:text-blue-200"
                            >
                                Login
                            </Link>

                            <Link
                                to="/signup"
                                className="rounded-lg bg-white px-4 py-2 font-medium text-blue-600 hover:bg-blue-100"
                            >
                                Signup
                            </Link>
                        </>
                    )}

                </div>

            </div>
        </nav>
    );
}

export default Navbar;