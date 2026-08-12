import { Link } from "react-router-dom";

function Footer() {
    return (
        <footer className="mt-auto border-t bg-white">
            <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-6 text-sm text-gray-600 md:flex-row">

                <div>
                    © {new Date().getFullYear()} AI Research Workspace
                </div>

                <div className="flex items-center gap-6">
                    <Link
                        to="/"
                        className="hover:text-blue-600"
                    >
                        Home
                    </Link>

                    <Link
                        to="/collections"
                        className="hover:text-blue-600"
                    >
                        Collections
                    </Link>

                    <Link
                        to="/upload"
                        className="hover:text-blue-600"
                    >
                        Upload
                    </Link>
                </div>

                <div>
                    Built with ❤️ using React, FastAPI & AI
                </div>

            </div>
        </footer>
    );
}

export default Footer;