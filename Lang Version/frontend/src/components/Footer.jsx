import { Link } from "react-router-dom";

function Footer() {
    return (
        <footer className="mt-auto border-t border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
            <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-6 text-sm text-zinc-500 md:flex-row dark:text-zinc-400">

                <div>
                    © {new Date().getFullYear()} AI Research Workspace
                </div>

                <div className="flex items-center gap-6">
                    <Link
                        to="/"
                        className="transition-colors hover:text-indigo-600 dark:hover:text-indigo-400"
                    >
                        Home
                    </Link>

                    <Link
                        to="/collections"
                        className="transition-colors hover:text-indigo-600 dark:hover:text-indigo-400"
                    >
                        Collections
                    </Link>
                </div>

                <div>
                    Built with ❤️ using React, FastAPI &amp; AI
                </div>

            </div>
        </footer>
    );
}

export default Footer;