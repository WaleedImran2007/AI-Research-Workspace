import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

// Presentational-only: toggles a `.dark` class on <html> and remembers the
// choice in localStorage under its own key ("ui-theme") so it never
// collides with the app's auth/session storage keys.
function ThemeToggle({ className = "" }) {
    const [isDark, setIsDark] = useState(() => {
        if (typeof document === "undefined") return false;
        return document.documentElement.classList.contains("dark");
    });

    useEffect(() => {
        const root = document.documentElement;

        if (isDark) {
            root.classList.add("dark");
            localStorage.setItem("ui-theme", "dark");
        } else {
            root.classList.remove("dark");
            localStorage.setItem("ui-theme", "light");
        }
    }, [isDark]);

    return (
        <button
            type="button"
            onClick={() => setIsDark((prev) => !prev)}
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
            title={isDark ? "Switch to light mode" : "Switch to dark mode"}
            className={`focus-ring inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-zinc-200 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white ${className}`}
        >
            {isDark ? <Sun size={17} strokeWidth={2} /> : <Moon size={17} strokeWidth={2} />}
        </button>
    );
}

export default ThemeToggle;