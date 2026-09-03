import { Link } from "react-router-dom";
import { useAuth } from "../../Context/AuthContext.jsx";
import { FileText, MessageSquare, Sparkles, UploadCloud } from "lucide-react";

function Home() {
    const { isAuthenticated } = useAuth();

    return (
        <div className="bg-zinc-50 dark:bg-zinc-950">

            {/* Hero Section */}
            <section className="mx-auto flex min-h-[80vh] max-w-7xl flex-col items-center justify-center px-6 text-center">

                <span className="mb-5 inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-4 py-1.5 text-sm font-medium text-indigo-700 dark:border-indigo-500/20 dark:bg-indigo-500/10 dark:text-indigo-300">
                    <Sparkles size={14} strokeWidth={2.25} />
                    AI Powered Research Assistant
                </span>

                <h1 className="font-display mb-6 max-w-3xl text-4xl font-bold tracking-tight text-zinc-900 sm:text-5xl md:text-6xl dark:text-white">
                    Chat with your documents
                </h1>

                <p className="mb-10 max-w-2xl text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
                    Upload PDFs, organize them into collections, search using
                    semantic embeddings, and ask questions powered by AI.
                    Everything is stored securely and retrieved using Retrieval
                    Augmented Generation (RAG).
                </p>

                <div className="flex flex-wrap justify-center gap-4">

                    {isAuthenticated ? (
                        <>
                            <Link
                                to="/ai"
                                className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-indigo-700"
                            >
                                Ask AI
                            </Link>

                            <Link
                                to="/collections"
                                className="rounded-lg border border-zinc-300 px-6 py-3 font-semibold text-zinc-700 transition-colors hover:border-indigo-300 hover:text-indigo-600 dark:border-zinc-700 dark:text-zinc-200 dark:hover:border-indigo-500/40 dark:hover:text-indigo-400"
                            >
                                View Collections
                            </Link>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/signup"
                                className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-indigo-700"
                            >
                                Get Started
                            </Link>

                            <Link
                                to="/login"
                                className="rounded-lg border border-zinc-300 px-6 py-3 font-semibold text-zinc-700 transition-colors hover:border-indigo-300 hover:text-indigo-600 dark:border-zinc-700 dark:text-zinc-200 dark:hover:border-indigo-500/40 dark:hover:text-indigo-400"
                            >
                                Login
                            </Link>
                        </>
                    )}

                </div>

            </section>

            {/* Features */}
            <section className="mx-auto grid max-w-7xl gap-6 px-6 pb-24 md:grid-cols-3">

                <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900">
                    <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400">
                        <FileText size={20} strokeWidth={2} />
                    </div>

                    <h2 className="mb-2.5 text-lg font-semibold text-zinc-900 dark:text-white">
                        Upload documents
                    </h2>

                    <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                        Upload PDFs and organize them into collections for easy
                        management.
                    </p>
                </div>

                <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900">
                    <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400">
                        <UploadCloud size={20} strokeWidth={2} />
                    </div>

                    <h2 className="mb-2.5 text-lg font-semibold text-zinc-900 dark:text-white">
                        AI retrieval
                    </h2>

                    <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                        Documents are chunked, embedded, and searched using
                        semantic similarity for accurate retrieval.
                    </p>
                </div>

                <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900">
                    <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400">
                        <MessageSquare size={20} strokeWidth={2} />
                    </div>

                    <h2 className="mb-2.5 text-lg font-semibold text-zinc-900 dark:text-white">
                        Chat naturally
                    </h2>

                    <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                        Ask questions in natural language and receive answers
                        grounded in your uploaded documents.
                    </p>
                </div>

            </section>

        </div>
    );
}

export default Home;