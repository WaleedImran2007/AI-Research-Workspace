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
        <div className="flex h-[calc(100vh-64px)] bg-gray-50 relative">
            {/* Mobile overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/40 z-20 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`fixed lg:static z-30 top-0 left-0 h-full w-72 bg-white border-r flex flex-col
                    transform transition-transform duration-200 ease-in-out
                    ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
            >
                {/* Conversations */}
                <div className="p-4 border-b flex items-center justify-between">
                    <h2 className="font-semibold text-gray-800">Conversations</h2>
                    <button
                        onClick={() => setSidebarOpen(false)}
                        className="lg:hidden text-gray-500 hover:text-gray-800"
                        aria-label="Close sidebar"
                    >
                        ✕
                    </button>
                </div>

                <div className="p-4">
                    <button
                        onClick={handleNewChat}
                        className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                        <span className="text-lg leading-none">+</span> New Chat
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto px-2 space-y-1">
                    {conversationsLoading && (
                        <p className="text-xs text-gray-400 px-3 py-2">Loading...</p>
                    )}

                    {!conversationsLoading && conversations.length === 0 && (
                        <p className="text-xs text-gray-400 px-3 py-2">
                            No conversations yet.
                        </p>
                    )}

                    {conversations.map((conv) => (
                        <div
                            key={conv.id}
                            onClick={() => editingConversationId !== conv.id && handleSelectConversation(conv.id)}
                            className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate flex items-center gap-2 transition group cursor-pointer

                            ${conv.id === activeConversationId
                                    ? "bg-blue-50 text-blue-700 font-medium"
                                    : "text-gray-700 hover:bg-gray-100"
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
                                    onKeyDown={(e) => handleRenameKeyDown(e, conv.id)}
                                    onBlur={() => submitRename(conv.id)}
                                    className="flex-1 min-w-0 border border-blue-300 rounded px-1 py-0.5 text-sm outline-none"
                                />
                            ) : (
                                <>
                                    <span className="truncate flex-1">{conv.title}</span>
                                    <span
                                        onClick={(e) => handleRename(e, conv)}
                                        className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-blue-500 transition"
                                        aria-label="Rename conversation"
                                    >
                                        <Edit2 size={16} />
                                    </span>

                                    <span
                                        onClick={(e) => handleDeleteConversation(e, conv.id)}
                                        className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition"
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
                <div className="border-t p-4">
                    <h2 className="font-semibold text-gray-800 mb-3">Collections</h2>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                        {collections.map((collection) => (
                            <label
                                key={collection.id}
                                className="flex items-center gap-2 cursor-pointer text-sm text-gray-700"
                            >
                                <input
                                    type="checkbox"
                                    checked={selectedCollections.includes(collection.id)}
                                    onChange={() => toggleCollection(collection.id)}
                                />
                                <span className="truncate">{collection.name}</span>
                            </label>
                        ))}
                        {collections.length === 0 && (
                            <p className="text-xs text-gray-400">No collections yet.</p>
                        )}
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Top bar */}
                <div className="flex items-center gap-3 border-b bg-white px-4 py-3 lg:px-6">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="lg:hidden text-gray-600 hover:text-gray-900"
                        aria-label="Open sidebar"
                    >
                        ☰
                    </button>
                    <h1 className="text-xl sm:text-2xl font-bold text-gray-800 truncate">
                        AI Research Assistant
                    </h1>
                </div>

                {/* Chat */}
                <div className="flex-1 flex flex-col min-h-0 max-w-4xl w-full mx-auto px-3 sm:px-6 py-4">
                    <div className="flex-1 overflow-y-auto bg-white rounded-xl shadow p-4 sm:p-5 space-y-4">
                        {messages.map((msg, index) => {
                            const isUser = msg.role === "user";
                            const hasSources = !isUser && msg.sources && msg.sources.length > 0;

                            return (
                                <div
                                    key={index}
                                    className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                                >
                                    <div
                                        className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 prose prose-sm max-w-none ${isUser
                                            ? "bg-blue-600 text-white prose-invert rounded-br-none"
                                            : "bg-gray-100 text-gray-800 rounded-bl-none"
                                            }`}
                                    >
                                        {/* Markdown Content */}
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {msg.content}
                                        </ReactMarkdown>

                                        {/* Sources Section */}
                                        {hasSources && (
                                            <div className="mt-4 pt-3 border-t border-gray-200/60">
                                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                                                    Sources
                                                </p>

                                                <div className="space-y-2">
                                                    {msg.sources.map((source, idx) => {
                                                        // 1. Web Source
                                                        if (source.type === "web") {
                                                            return (
                                                                <a
                                                                    key={idx}
                                                                    href={source.url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="block text-xs text-gray-600 bg-gray-50 hover:bg-gray-200/70 transition-colors px-3 py-2 rounded-lg cursor-pointer"
                                                                >
                                                                    <p className="font-semibold text-blue-600 hover:underline">
                                                                        {source.title || "Web Link"}
                                                                    </p>
                                                                    <p className="text-gray-500 truncate">{source.url}</p>
                                                                </a>
                                                            );
                                                        }

                                                        // 2. Document Source
                                                        if (source.type === "document") {
                                                            return (
                                                                <Link
                                                                    key={idx}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    to={`/documents/${source.documentId}?page=${source.page}&highlight=${encodeURIComponent(
                                                                        source.text || ""
                                                                    )}`}
                                                                    className="block text-xs text-gray-600 bg-gray-50 hover:bg-gray-200/70 transition-colors px-3 py-2 rounded-lg cursor-pointer"
                                                                >
                                                                    <p className="font-semibold text-blue-600 hover:underline">
                                                                        {source.documentName || source.fileName || "Document"}
                                                                    </p>
                                                                    <p className="text-gray-500">Page {source.page}</p>
                                                                </Link>
                                                            );
                                                        }

                                                        if (source.type === "image") {
                                                            return (
                                                                <div key={index}>
                                                                    <img
                                                                        src={`${import.meta.env.VITE_API_URL}/${source.path}`}
                                                                        alt="Generated Graph"
                                                                        className="rounded-lg border max-w-full"
                                                                    />
                                                                </div>
                                                            );
                                                        }

                                                        return null;
                                                    })}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 text-gray-500 rounded-2xl rounded-bl-none px-4 py-3 text-sm flex items-center gap-2">
                                    <span className="animate-pulse">Thinking...</span>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form
                        onSubmit={handleSubmit}
                        className="border-t-0 mt-4 bg-white rounded-xl shadow p-3 flex flex-col sm:flex-row gap-3"
                    >
                        <input
                            type="text"
                            placeholder="Ask something..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="flex-1 border rounded-lg px-4 py-3 outline-none"
                        />

                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-blue-600 text-white px-6 py-3 sm:py-0 rounded-lg hover:bg-blue-700 disabled:opacity-50"
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