import { Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import { useAuth } from "../../Context/AuthContext.jsx";
import ThemeToggle from "./ThemeToggle.jsx";
import { ChevronDown, Menu, Sparkles, X } from "lucide-react";

function Navbar() {
    const { user, logout, isAuthenticated } = useAuth();

    const [showDropdown, setShowDropdown] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const dropdownRef = useRef(null);

    const navigate = useNavigate();
    const location = useLocation();

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

    // Close the mobile menu whenever the route changes.
    useEffect(() => {
        setMobileMenuOpen(false);
    }, [location.pathname]);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const isActive = (path) => location.pathname === path;

    const navLinkClass = (path) =>
        `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
            isActive(path)
                ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300"
                : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white"
        }`;

    const mobileNavLinkClass = (path) =>
        `block rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
            isActive(path)
                ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300"
                : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
        }`;

    return (
        <nav className="sticky top-0 z-50 border-b border-zinc-200 bg-white/85 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/85">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">

                <Link
                    to="/"
                    className="flex items-center gap-2 font-display text-lg font-bold tracking-tight text-zinc-900 dark:text-white"
                >
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
                        <Sparkles size={16} strokeWidth={2.25} />
                    </span>
                    <span className="hidden sm:inline">AI Research Workspace</span>
                    <span className="sm:hidden">ARW</span>
                </Link>

                {/* Desktop nav links */}
                <div className="hidden items-center gap-1 md:flex">
                    <Link to="/" className={navLinkClass("/")}>
                        Home
                    </Link>

                    <Link to="/ai" className={navLinkClass("/ai")}>
                        AI Assistant
                    </Link>

                    {isAuthenticated && (
                        <>
                            <Link to="/collections" className={navLinkClass("/collections")}>
                                Collections
                            </Link>
                        </>
                    )}
                </div>

                {/* Right side controls */}
                <div className="flex items-center gap-2 sm:gap-3">

                    <ThemeToggle className="hidden sm:inline-flex" />

                    {isAuthenticated ? (
                        <div className="relative hidden md:block" ref={dropdownRef}>

                            <button
                                onClick={() =>
                                    setShowDropdown(!showDropdown)
                                }
                                className="focus-ring flex cursor-pointer items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm font-medium text-zinc-800 transition-colors hover:border-zinc-300 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:border-zinc-600"
                            >
                                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 text-xs font-semibold text-white">
                                    {user?.username?.[0]?.toUpperCase() || "U"}
                                </span>
                                <span className="max-w-[9rem] truncate">{user.username}</span>
                                <ChevronDown size={15} className={`text-zinc-400 transition-transform ${showDropdown ? "rotate-180" : ""}`} />
                            </button>

                            {showDropdown && (
                                <div className="absolute right-0 mt-2 w-44 overflow-hidden rounded-xl border border-zinc-200 bg-white py-1 shadow-lg dark:border-zinc-700 dark:bg-zinc-900">

                                    <Link
                                        to="/profile"
                                        className="block px-4 py-2.5 text-sm text-zinc-700 hover:bg-zinc-50 dark:text-zinc-200 dark:hover:bg-zinc-800"
                                        onClick={() =>
                                            setShowDropdown(false)
                                        }
                                    >
                                        Profile
                                    </Link>

                                    <button
                                        onClick={handleLogout}
                                        className="block w-full px-4 py-2.5 text-left text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
                                    >
                                        Logout
                                    </button>

                                </div>
                            )}

                        </div>
                    ) : (
                        <div className="hidden items-center gap-2 md:flex">
                            <Link
                                to="/login"
                                className="rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white"
                            >
                                Login
                            </Link>

                            <Link
                                to="/signup"
                                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-indigo-700"
                            >
                                Sign up
                            </Link>
                        </div>
                    )}

                    {/* Mobile menu toggle */}
                    <button
                        onClick={() => setMobileMenuOpen((prev) => !prev)}
                        className="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-200 text-zinc-600 md:hidden dark:border-zinc-700 dark:text-zinc-300"
                        aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                    >
                        {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
                    </button>

                </div>

            </div>

            {/* Mobile menu panel */}
            {mobileMenuOpen && (
                <div className="border-t border-zinc-200 bg-white px-4 pb-4 pt-2 md:hidden dark:border-zinc-800 dark:bg-zinc-950">
                    <div className="flex flex-col gap-1">
                        <Link to="/" className={mobileNavLinkClass("/")}>
                            Home
                        </Link>

                        <Link to="/ai" className={mobileNavLinkClass("/ai")}>
                            AI Assistant
                        </Link>

                        {isAuthenticated && (
                            <>
                                <Link to="/collections" className={mobileNavLinkClass("/collections")}>
                                    Collections
                                </Link>

                                <Link to="/upload" className={mobileNavLinkClass("/upload")}>
                                    Upload
                                </Link>

                                <Link to="/profile" className={mobileNavLinkClass("/profile")}>
                                    Profile
                                </Link>

                                <button
                                    onClick={handleLogout}
                                    className="mt-1 block rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
                                >
                                    Logout
                                </button>
                            </>
                        )}

                        {!isAuthenticated && (
                            <div className="mt-2 flex items-center gap-2 border-t border-zinc-200 pt-3 dark:border-zinc-800">
                                <Link
                                    to="/login"
                                    className="flex-1 rounded-lg border border-zinc-200 px-3 py-2 text-center text-sm font-medium text-zinc-700 dark:border-zinc-700 dark:text-zinc-200"
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/signup"
                                    className="flex-1 rounded-lg bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white"
                                >
                                    Sign up
                                </Link>
                            </div>
                        )}

                        <div className="mt-2 flex items-center justify-between border-t border-zinc-200 pt-3 dark:border-zinc-800">
                            <span className="text-sm text-zinc-500 dark:text-zinc-400">Appearance</span>
                            <ThemeToggle />
                        </div>
                    </div>
                </div>
            )}

        </nav>
    );
}

export default Navbar;