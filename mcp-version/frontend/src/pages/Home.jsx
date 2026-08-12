import { Link } from "react-router-dom";
import { useAuth } from "../../Context/AuthContext.jsx";

function Home() {
    const { isAuthenticated } = useAuth();

    return (
        <div className="bg-gray-50">

            {/* Hero Section */}
            <section className="mx-auto flex min-h-[80vh] max-w-7xl flex-col items-center justify-center px-6 text-center">

                <span className="mb-4 rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700">
                    AI Powered Research Assistant
                </span>

                <h1 className="mb-6 text-5xl font-extrabold text-gray-900">
                    Chat with Your Documents
                </h1>

                <p className="mb-10 max-w-3xl text-lg text-gray-600">
                    Upload PDFs, organize them into collections, search using
                    semantic embeddings, and ask questions powered by AI.
                    Everything is stored securely and retrieved using Retrieval
                    Augmented Generation (RAG).
                </p>

                <div className="flex flex-wrap justify-center gap-4">

                    {isAuthenticated ? (
                        <>
                            <Link
                                to="/upload"
                                className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
                            >
                                Upload Document
                            </Link>

                            <Link
                                to="/collections"
                                className="rounded-lg border border-blue-600 px-6 py-3 font-semibold text-blue-600 transition hover:bg-blue-50"
                            >
                                View Collections
                            </Link>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/signup"
                                className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
                            >
                                Get Started
                            </Link>

                            <Link
                                to="/login"
                                className="rounded-lg border border-blue-600 px-6 py-3 font-semibold text-blue-600 transition hover:bg-blue-50"
                            >
                                Login
                            </Link>
                        </>
                    )}

                </div>

            </section>

            {/* Features */}
            <section className="mx-auto grid max-w-7xl gap-8 px-6 pb-20 md:grid-cols-3">

                <div className="rounded-xl bg-white p-8 shadow">
                    <div className="mb-4 text-4xl">📄</div>

                    <h2 className="mb-3 text-xl font-bold">
                        Upload Documents
                    </h2>

                    <p className="text-gray-600">
                        Upload PDFs and organize them into collections for easy
                        management.
                    </p>
                </div>

                <div className="rounded-xl bg-white p-8 shadow">
                    <div className="mb-4 text-4xl">🧠</div>

                    <h2 className="mb-3 text-xl font-bold">
                        AI Retrieval
                    </h2>

                    <p className="text-gray-600">
                        Documents are chunked, embedded, and searched using
                        semantic similarity for accurate retrieval.
                    </p>
                </div>

                <div className="rounded-xl bg-white p-8 shadow">
                    <div className="mb-4 text-4xl">💬</div>

                    <h2 className="mb-3 text-xl font-bold">
                        Chat Naturally
                    </h2>

                    <p className="text-gray-600">
                        Ask questions in natural language and receive answers
                        grounded in your uploaded documents.
                    </p>
                </div>

            </section>

        </div>
    );
}

export default Home;