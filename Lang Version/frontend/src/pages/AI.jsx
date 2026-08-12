import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "../../api/api.js";
import { Trash2, Edit2 } from "lucide-react";
import { Link } from "react-router-dom";

function AI() {
    const [collections, setCollections] = useState([]);
    const [selectedCollections, setSelectedCollections] = useState([]);

    // Conversations come straight from GET /conversations/
    // Shape (ConversationResponse): { id, title, created_at, updated_at }
    const [conversations, setConversations] = useState([]);
    const [conversationsLoading, setConversationsLoading] = useState(true);

    const [editingConversationId, setEditingConversationId] = useState(null);
    const [editTitleValue, setEditTitleValue] = useState("");

    // null = "new chat, not yet created on the backend" (lazy creation).
    // A real id only exists once POST /conversations/ has actually run.
    const [activeConversationId, setActiveConversationId] = useState(localStorage.getItem('activeConversationId') || null);

    // Messages keyed by conversation id. The "null" bucket holds the
    // greeting for a not-yet-created conversation.
    const [messagesByConversation, setMessagesByConversation] = useState({
        null: [
            {
                role: "assistant",
                content: "Hello! 👋 Ask me anything about your uploaded documents.",
            },
        ],
    });

    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const messagesEndRef = useRef(null);

    const messages = messagesByConversation[activeConversationId ?? "null"] || [];

    useEffect(() => {
        fetchCollections();
        fetchConversations();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    const fetchCollections = async () => {
        try {
            const res = await api.get("/collections/");
            setCollections(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    // GET /conversations/  -> list[ConversationResponse]
    const fetchConversations = async () => {
        setConversationsLoading(true);
        try {
            const res = await api.get("/conversations/");
            setConversations(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setConversationsLoading(false);
        }
    };

    // GET /conversations/{id} -> { conversation, messages }
    const fetchConversationDetail = async (conversationId) => {
        try {
            const res = await api.get(`/conversations/${conversationId}`);
            const loadedMessages = res.data.messages.map((m) => ({
                role: m.role,
                content: m.content,
                sources: m.sources || [],
            }));

            setMessagesByConversation((prev) => ({
                ...prev,
                [conversationId]: loadedMessages.length
                    ? loadedMessages
                    : [
                        {
                            role: "assistant",
                            content: "Hello! 👋 Ask me anything about your uploaded documents.",
                        },
                    ],
            }));
        } catch (err) {
            console.error(err);
        }
    };

    const toggleCollection = (id) => {
        setSelectedCollections((prev) =>
            prev.includes(id)
                ? prev.filter((item) => item !== id)
                : [...prev, id]
        );
    };

    // Doesn't call the backend yet — the conversation only gets created
    // (POST /conversations/) once the user actually sends a message.
    const handleNewChat = () => {
        setActiveConversationId(null);
        setMessagesByConversation((prev) => ({
            ...prev,
            null: [
                {
                    role: "assistant",
                    content: "Hello! 👋 Ask me anything about your uploaded documents.",
                },
            ],
        }));
        setSidebarOpen(false);
    };

    const handleSelectConversation = (id) => {
        setActiveConversationId(id);
        setSidebarOpen(false);

        localStorage.setItem('activeConversationId', id);

        // Only fetch if we haven't already loaded this conversation's messages.
        if (!messagesByConversation[id]) {
            fetchConversationDetail(id);
        }
    };

    // PATCH /conversations/{id} — rename "new chat" once we know the first message.
    const renameConversation = async (conversationId, firstMessage) => {
        const title =
            firstMessage.length > 32 ? `${firstMessage.slice(0, 32)}...` : firstMessage;

        try {
            const res = await api.patch(`/conversations/${conversationId}`, { title });
            setConversations((prev) =>
                prev.map((c) => (c.id === conversationId ? res.data : c))
            );
        } catch (err) {
            console.error(err);
        }
    };

    const handleRename = (e, conv) => {
        e.stopPropagation();
        setEditingConversationId(conv.id);
        setEditTitleValue(conv.title)
    }

    const submitRename = async (conversationId) => {
        const trimmed = editTitleValue.trim();
        if (!trimmed) {
            return
        }

        try {
            const res = await api.patch(`/conversations/${conversationId}`, { title: trimmed });
            setConversations((prev) =>
                prev.map((c) => (c.id === conversationId ? res.data : c))
            );
            setEditingConversationId(null);
        }

        catch (err) {
            console.error(err);
        }
    }

    const handleRenameKeyDown = (e, conversationId) => {
        if (e.key === "Enter") {
            e.preventDefault();
            submitRename(conversationId);
        } else if (e.key === "Escape") {
            setEditingConversationId(null);
        }
    }

    // DELETE /conversations/{id}
    const handleDeleteConversation = async (e, conversationId) => {
        if (!window.confirm("Are you sure you want to delete this conversation?")) {
            return;
        }

        e.stopPropagation();
        try {
            await api.delete(`/conversations/${conversationId}`);

            if (activeConversationId === conversationId) {
                localStorage.removeItem('activeConversationId');
            }

            setConversations((prev) => prev.filter((c) => c.id !== conversationId));
            setMessagesByConversation((prev) => {
                const next = { ...prev };
                delete next[conversationId];
                return next;
            });

            if (activeConversationId === conversationId) {
                handleNewChat();
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!query.trim()) return;

        const currentQuery = query;
        const isNewConversation = activeConversationId === null;
        const draftKey = activeConversationId ?? "null";

        const userMessage = {
            role: "user",
            content: currentQuery
        };

        setMessagesByConversation((prev) => ({
            ...prev,
            [draftKey]: [
                ...(prev[draftKey] || []),
                userMessage
            ],
        }));

        setQuery("");
        setLoading(true);

        try {
            let conversationId = activeConversationId;

            // Create conversation if this is the first message
            if (isNewConversation) {
                const createRes = await api.post("/conversations/");
                conversationId = createRes.data.id;

                setConversations((prev) => [
                    createRes.data,
                    ...prev
                ]);

                setMessagesByConversation((prev) => {
                    const next = { ...prev };

                    next[conversationId] = next["null"] || [userMessage];

                    delete next["null"];
                    return next;
                });

                setActiveConversationId(conversationId);
            }

            const body = {
                query: currentQuery,
                conversation_id: conversationId
            };

            if (selectedCollections.length > 0) {
                body.collection_ids = selectedCollections;
            }

            const res = await fetch(
                `${import.meta.env.VITE_API_URL}/chat/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${localStorage.getItem("token")}`,
                    },

                    body: JSON.stringify(body),
                }
            );

            if (!res.ok) {
                throw new Error("Chat request failed");
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let assistantText = "";

            // Add empty assistant message
            setMessagesByConversation((prev) => ({
                ...prev,
                [conversationId]: [
                    ...(prev[conversationId] || []),
                    {
                        role: "assistant",
                        content: "",
                        sources: []
                    }
                ]
            }));

            // Read SSE stream
            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value, {
                    stream: true
                });

                const events = chunk
                    .split("\n\n")
                    .filter(Boolean);

                for (const event of events) {
                    const data = event.replace("data: ", "");
                    const parsed = JSON.parse(data);

                    // Receiving tokens
                    if (parsed.type === "token") {
                        assistantText += parsed.content;
                        setMessagesByConversation((prev) => {
                            const messages = [
                                ...(prev[conversationId] || [])
                            ];

                            messages[messages.length - 1] = {
                                ...messages[messages.length - 1],
                                content: assistantText
                            };

                            return {
                                ...prev,
                                [conversationId]: messages
                            };
                        });
                    }

                    // Receiving sources
                    if (parsed.type === "sources") {
                        setMessagesByConversation((prev) => {
                            const messages = [
                                ...(prev[conversationId] || [])
                            ];

                            messages[messages.length - 1] = {
                                ...messages[messages.length - 1],
                                sources: parsed.content
                            };

                            return {
                                ...prev,
                                [conversationId]: messages
                            };
                        });
                    }
                }
            }

            // Rename first conversation after first response
            if (isNewConversation) {
                renameConversation(
                    conversationId,
                    currentQuery
                );
            }

        } catch (err) {

            console.error(err);

            const failKey = isNewConversation
                ? "null"
                : draftKey;

            setMessagesByConversation((prev) => ({
                ...prev,
                [failKey]: [
                    ...(prev[failKey] || []),
                    {
                        role: "assistant",
                        content: "Something went wrong."
                    }
                ]
            }));

        }

        setLoading(false);
    };

    useEffect(() => {
        if (activeConversationId && !messagesByConversation[activeConversationId]) {
            fetchConversationDetail(activeConversationId);
        }
    }, [activeConversationId]);

    return (
        <div className="relative flex h-[calc(100vh-64px)] bg-gray-50 dark:bg-zinc-950">

            {/* Mobile overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-20 bg-black/40 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`fixed top-0 left-0 z-30 flex h-full w-72 flex-col border-r border-gray-200 bg-white
                transform transition-transform duration-200 ease-in-out
                dark:border-zinc-800 dark:bg-zinc-900
                ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:static lg:translate-x-0`}
            >

                {/* Conversations */}
                <div className="flex items-center justify-between border-b border-gray-200 p-4 dark:border-zinc-800">
                    <h2 className="font-semibold text-gray-800 dark:text-zinc-100">
                        Conversations
                    </h2>

                    <button
                        onClick={() => setSidebarOpen(false)}
                        className="text-gray-500 hover:text-gray-800 dark:text-zinc-400 dark:hover:text-white lg:hidden"
                        aria-label="Close sidebar"
                    >
                        ✕
                    </button>
                </div>

                <div className="p-4">
                    <button
                        onClick={handleNewChat}
                        className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-2 text-white transition hover:bg-blue-700"
                    >
                        <span className="text-lg leading-none">+</span> New Chat
                    </button>
                </div>

                <div className="flex-1 space-y-1 overflow-y-auto px-2">

                    {conversationsLoading && (
                        <p className="px-3 py-2 text-xs text-gray-400 dark:text-zinc-500">
                            Loading...
                        </p>
                    )}

                    {!conversationsLoading && conversations.length === 0 && (
                        <p className="px-3 py-2 text-xs text-gray-400 dark:text-zinc-500">
                            No conversations yet.
                        </p>
                    )}

                    {conversations.map((conv) => (
                        <div
                            key={conv.id}
                            onClick={() =>
                                editingConversationId !== conv.id &&
                                handleSelectConversation(conv.id)
                            }
                            className={`group flex w-full cursor-pointer items-center gap-2 truncate rounded-lg px-3 py-2 text-left text-sm transition

                        ${conv.id === activeConversationId
                                    ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-950/50 dark:text-blue-400"
                                    : "text-gray-700 hover:bg-gray-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                }`}
                            title={conv.title}
                        >
                            <span>💬</span>

                            {editingConversationId === conv.id ? (
                                <input
                                    type="text"
                                    autoFocus
                                    value={editTitleValue}
                                    onChange={(e) => setEditTitleValue(e.target.value)}
                                    onClick={(e) => e.stopPropagation()}
                                    onKeyDown={(e) =>
                                        handleRenameKeyDown(e, conv.id)
                                    }
                                    onBlur={() => submitRename(conv.id)}
                                    className="min-w-0 flex-1 rounded border border-blue-300 bg-white px-1 py-0.5 text-sm text-gray-900 outline-none dark:border-blue-700 dark:bg-zinc-800 dark:text-zinc-100"
                                />
                            ) : (
                                <>
                                    <span className="flex-1 truncate">
                                        {conv.title}
                                    </span>

                                    <span
                                        onClick={(e) => handleRename(e, conv)}
                                        className="text-gray-400 opacity-0 transition hover:text-blue-500 group-hover:opacity-100 dark:text-zinc-500 dark:hover:text-blue-400"
                                        aria-label="Rename conversation"
                                    >
                                        <Edit2 size={16} />
                                    </span>

                                    <span
                                        onClick={(e) =>
                                            handleDeleteConversation(e, conv.id)
                                        }
                                        className="text-gray-400 opacity-0 transition hover:text-red-500 group-hover:opacity-100 dark:text-zinc-500 dark:hover:text-red-400"
                                        aria-label="Delete conversation"
                                    >
                                        <Trash2 size={16} />
                                    </span>
                                </>
                            )}
                        </div>
                    ))}
                </div>

                {/* Collections */}
                <div className="border-t border-gray-200 p-4 dark:border-zinc-800">
                    <h2 className="mb-3 font-semibold text-gray-800 dark:text-zinc-100">
                        Collections
                    </h2>

                    <div className="max-h-48 space-y-2 overflow-y-auto">
                        {collections.map((collection) => (
                            <label
                                key={collection.id}
                                className="flex cursor-pointer items-center gap-2 text-sm text-gray-700 dark:text-zinc-300"
                            >
                                <input
                                    type="checkbox"
                                    checked={selectedCollections.includes(collection.id)}
                                    onChange={() =>
                                        toggleCollection(collection.id)
                                    }
                                />

                                <span className="truncate">
                                    {collection.name}
                                </span>
                            </label>
                        ))}

                        {collections.length === 0 && (
                            <p className="text-xs text-gray-400 dark:text-zinc-500">
                                No collections yet.
                            </p>
                        )}
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex min-w-0 flex-1 flex-col">

                {/* Top bar */}
                <div className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900 lg:px-6">

                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="text-gray-600 hover:text-gray-900 dark:text-zinc-400 dark:hover:text-white lg:hidden"
                        aria-label="Open sidebar"
                    >
                        ☰
                    </button>

                    <h1 className="truncate text-xl font-bold text-gray-800 dark:text-zinc-100 sm:text-2xl">
                        AI Research Assistant
                    </h1>
                </div>

                {/* Chat */}
                <div className="mx-auto flex min-h-0 w-full max-w-4xl flex-1 flex-col px-3 py-4 sm:px-6">

                    <div className="flex-1 space-y-4 overflow-y-auto rounded-xl bg-white p-4 shadow dark:bg-zinc-900 dark:shadow-black/20 sm:p-5">

                        {messages.map((msg, index) => {
                            const isUser = msg.role === "user";
                            const hasSources =
                                !isUser &&
                                msg.sources &&
                                msg.sources.length > 0;

                            return (
                                <div
                                    key={index}
                                    className={`flex ${isUser
                                            ? "justify-end"
                                            : "justify-start"
                                        }`}
                                >
                                    <div
                                        className={`prose prose-sm max-w-none max-w-[85%] rounded-2xl px-4 py-3 dark:prose-invert sm:max-w-[75%] ${isUser
                                                ? "rounded-br-none bg-blue-600 text-white prose-invert"
                                                : "rounded-bl-none bg-gray-100 text-gray-800 dark:bg-zinc-800 dark:text-zinc-100"
                                            }`}
                                    >

                                        {/* Markdown Content */}
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>

                                        {/* Sources Section */}
                                        {hasSources && (
                                            <div className="mt-4 border-t border-gray-200/60 pt-3 dark:border-zinc-700">

                                                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-zinc-400">
                                                    Sources
                                                </p>

                                                <div className="space-y-2">

                                                    {msg.sources.map(
                                                        (source, idx) => {

                                                            {/* Web Source */ }
                                                            if (
                                                                source.type ===
                                                                "web"
                                                            ) {
                                                                return (
                                                                    <a
                                                                        key={idx}
                                                                        href={
                                                                            source.url
                                                                        }
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="block cursor-pointer rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-600 transition-colors hover:bg-gray-200/70 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
                                                                    >
                                                                        <p className="font-semibold text-blue-600 hover:underline dark:text-blue-400">
                                                                            {source.title ||
                                                                                "Web Link"}
                                                                        </p>

                                                                        <p className="truncate text-gray-500 dark:text-zinc-500">
                                                                            {
                                                                                source.url
                                                                            }
                                                                        </p>
                                                                    </a>
                                                                );
                                                            }

                                                            {/* Document Source */ }
                                                            if (
                                                                source.type ===
                                                                "document"
                                                            ) {
                                                                return (
                                                                    <Link
                                                                        key={idx}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        to={`/documents/${source.documentId}?page=${source.page}&highlight=${encodeURIComponent(
                                                                            source.text ||
                                                                            ""
                                                                        )}`}
                                                                        className="block cursor-pointer rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-600 transition-colors hover:bg-gray-200/70 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
                                                                    >
                                                                        <p className="font-semibold text-blue-600 hover:underline dark:text-blue-400">
                                                                            {source.documentName ||
                                                                                source.fileName ||
                                                                                "Document"}
                                                                        </p>

                                                                        <p className="text-gray-500 dark:text-zinc-500">
                                                                            Page{" "}
                                                                            {
                                                                                source.page
                                                                            }
                                                                        </p>
                                                                    </Link>
                                                                );
                                                            }

                                                            {/* Image Source */ }
                                                            if (
                                                                source.type ===
                                                                "image"
                                                            ) {
                                                                return (
                                                                    <div
                                                                        key={index}
                                                                    >
                                                                        <img
                                                                            src={`${import.meta.env.VITE_API_URL}/${source.path}`}
                                                                            alt="Generated Graph"
                                                                            className="max-w-full rounded-lg border border-gray-200 dark:border-zinc-700"
                                                                        />
                                                                    </div>
                                                                );
                                                            }

                                                            return null;
                                                        }
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="flex items-center gap-2 rounded-2xl rounded-bl-none bg-gray-100 px-4 py-3 text-sm text-gray-500 dark:bg-zinc-800 dark:text-zinc-400">
                                    <span className="animate-pulse">
                                        Thinking...
                                    </span>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form
                        onSubmit={handleSubmit}
                        className="mt-4 flex flex-col gap-3 rounded-xl bg-white p-3 shadow dark:bg-zinc-900 dark:shadow-black/20 sm:flex-row"
                    >
                        <input
                            type="text"
                            placeholder="Ask something..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder:text-zinc-500"
                        />

                        <button
                            type="submit"
                            disabled={loading}
                            className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50 sm:py-0"
                        >
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default AI;