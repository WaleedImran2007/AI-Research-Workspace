import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "../../api/api.js";
import {
    Trash2,
    Edit2,
    Plus,
    Sparkles,
    Bot,
    Send,
    Globe,
    ImagePlus,
    PanelLeftClose,
    PanelLeftOpen,
    X,
} from "lucide-react";
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

    const [webEnabled, setWebEnabled] = useState(false);

    const [statusMessage, setStatusMessage] = useState("Thinking...");

    const [aiRequestsRemaining, setAiRequestsRemaining] = useState(0);
    const [aiResetDate, setAiResetDate] = useState(null);

    // Purely cosmetic — collapses the sidebar down to an icon rail on desktop.
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const res = await api.get("/user/ai-requests");
                setAiRequestsRemaining(res.data.aiRequestsRemaining);
                setAiResetDate(res.data.aiResetDate);
            } catch (err) {
                console.error(err);
            }
        };

        fetchUserData();
    }, []);

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
    const [selectedImage, setSelectedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const messagesEndRef = useRef(null);

    const messages = messagesByConversation[activeConversationId ?? "null"] || [];
    const activeConversation = conversations.find((c) => c.id === activeConversationId);
    const activeTitle = activeConversation?.title || "New chat";

    const requestsPct = Math.max(0, Math.min(100, (aiRequestsRemaining / 15) * 100));
    const requestsColor =
        aiRequestsRemaining <= 3
            ? "bg-rose-500"
            : aiRequestsRemaining <= 7
                ? "bg-amber-500"
                : "bg-indigo-500";

    useEffect(() => {
        fetchCollections();
        fetchConversations();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    useEffect(() => {
        if (!selectedImage) {
            setImagePreview(null);
            return;
        }

        const url = URL.createObjectURL(selectedImage);
        setImagePreview(url);

        return () => {
            URL.revokeObjectURL(url);
        };
    }, [selectedImage]);

    function formatTimestamp(seconds) {
        if (seconds === undefined || seconds === null) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    }

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
                image: m.image
                    ? `${import.meta.env.VITE_API_URL}/chat/images/${m.image}`
                    : undefined,
                file: m.file
                    ? {
                        filename: m.file.filename,
                        type: m.file.type,
                        url: `${import.meta.env.VITE_API_URL}/chat/documents/${m.file.filename}`
                    }
                    : undefined
            }));

            console.log("LOADED MESSAGE:", res.data.messages);

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
            content: currentQuery,
            image: imagePreview
        };

        setMessagesByConversation((prev) => ({
            ...prev,
            [draftKey]: [
                ...(prev[draftKey] || []),
                userMessage
            ],
        }));

        setQuery("");
        setSelectedImage(null);
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

            const formData = new FormData();

            formData.append("query", currentQuery);
            formData.append("conversation_id", conversationId);
            formData.append("web_enabled", webEnabled);

            if (selectedCollections.length > 0) {
                formData.append(
                    "collection_ids",
                    JSON.stringify(selectedCollections)
                );
            }

            if (selectedImage) {
                formData.append("image", selectedImage);
            }

            const res = await fetch(
                `${import.meta.env.VITE_API_URL}/chat/`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`,
                    },
                    body: formData,
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

                    // Receiving status updates
                    if (parsed.type === "status") {
                        setStatusMessage(parsed.content);
                    }

                    // Receiving tokens
                    if (parsed.type === "token") {
                        setStatusMessage(null);
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
                                sources: parsed.content,
                                file: parsed.file
                                    ? {
                                        ...parsed.file,
                                        url: `${import.meta.env.VITE_API_URL}/chat/documents/${parsed.file.filename}`
                                    }
                                    : undefined
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

            setAiRequestsRemaining((prev) => Math.max(prev - 1, 0));

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
        <div className="relative flex h-[calc(100vh)] overflow-hidden bg-zinc-50 dark:bg-zinc-950">

            {/* Mobile overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-20 bg-black/40 dark:bg-black/60 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`fixed top-0 left-0 z-30 flex h-full flex-col border-r border-zinc-200 bg-white
                transition-[transform,width] duration-200 ease-in-out
                dark:border-zinc-800/80 dark:bg-[#171717]
                ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:static lg:translate-x-0
                ${sidebarCollapsed ? "w-20" : "w-70"}`}
            >

                {/* Brand */}
                <div
                    className={`flex shrink-0 border-b border-zinc-200 dark:border-zinc-800/80 ${sidebarCollapsed
                        ? "flex-col items-center gap-2.5 py-3"
                        : "h-16 items-center justify-between px-4"
                        }`}
                >
                    <div className={`flex items-center overflow-hidden ${sidebarCollapsed ? "" : "gap-2.5"}`}>
                        <Link
                            to="/"
                            className={`flex items-center overflow-hidden ${sidebarCollapsed ? "" : "gap-2.5"}`}
                        >
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
                                <Sparkles size={16} strokeWidth={2.25} />
                            </div>
                            {!sidebarCollapsed && (
                                <span className="font-display truncate font-semibold text-zinc-900 dark:text-zinc-100">
                                    Research AI
                                </span>
                            )}
                        </Link>
                    </div>

                    {!sidebarCollapsed && (
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="text-zinc-400 hover:text-zinc-700 dark:text-zinc-500 dark:hover:text-zinc-200 lg:hidden"
                            aria-label="Close sidebar"
                        >
                            <X size={18} />
                        </button>
                    )}

                    <button
                        onClick={() => setSidebarCollapsed((v) => !v)}
                        className="hidden rounded-md p-1 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700 dark:text-zinc-500 dark:hover:bg-zinc-800 dark:hover:text-zinc-200 lg:block"
                        aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    >
                        {sidebarCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
                    </button>
                </div>

                <div className="p-3">
                    <button
                        onClick={handleNewChat}
                        className={`flex w-full items-center gap-2 rounded-2xl border border-gray-500 cursor-pointer bg-transparent py-2.5 font-medium text-[14px] text-white transition hover:border-[#8A3A22] ${sidebarCollapsed ? "justify-center px-0" : "justify-center px-4"
                            }`}
                    >
                        <Plus className="text-[#E79070]" size={14} strokeWidth={2.5} />
                        {!sidebarCollapsed && "New Chat"}
                    </button>
                </div>

                {!sidebarCollapsed && (
                    <p className="px-4 pt-2 pb-1 text-[11px] font-medium tracking-wide text-zinc-400 dark:text-zinc-500">
                        CHATS
                    </p>
                )}

                <div className="flex-1 space-y-0.5 overflow-y-auto px-2 pt-1">

                    {conversationsLoading && !sidebarCollapsed && (
                        <p className="px-3 py-2 text-xs text-zinc-400 dark:text-zinc-500">Loading...</p>
                    )}

                    {!conversationsLoading && conversations.length === 0 && !sidebarCollapsed && (
                        <p className="px-3 py-2 text-xs text-zinc-400 dark:text-zinc-500">No conversations yet.</p>
                    )}

                    {conversations.map((conv) => {
                        const isActive = conv.id === activeConversationId;
                        return (
                            <div
                                key={conv.id}
                                onClick={() =>
                                    editingConversationId !== conv.id &&
                                    handleSelectConversation(conv.id)
                                }
                                className={`group relative flex w-full cursor-pointer items-center gap-2 truncate rounded-lg py-2 text-left text-sm transition
                                ${sidebarCollapsed ? "justify-center px-0" : "px-3"}
                                ${isActive
                                        ? "bg-indigo-50 font-medium text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300"
                                        : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/70 dark:hover:text-zinc-200"
                                    }`}
                                title={conv.title}
                            >
                                {isActive && (
                                    <span className="absolute top-1/2 left-0 h-4 w-0.5 -translate-y-1/2 rounded-full bg-indigo-500" />
                                )}

                                {sidebarCollapsed ? (
                                    <span className="text-base">💬</span>
                                ) : editingConversationId === conv.id ? (
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
                                        className="min-w-0 flex-1 rounded border border-indigo-300 bg-white px-1.5 py-0.5 text-sm text-zinc-900 outline-none dark:border-indigo-500/50 dark:bg-zinc-950 dark:text-zinc-100"
                                    />
                                ) : (
                                    <>
                                        <span className="flex-1 truncate">
                                            {conv.title}
                                        </span>

                                        <span
                                            onClick={(e) => handleRename(e, conv)}
                                            className="text-zinc-400 opacity-0 transition hover:text-indigo-500 group-hover:opacity-100 dark:text-zinc-500 dark:hover:text-indigo-400"
                                            aria-label="Rename conversation"
                                        >
                                            <Edit2 size={14} />
                                        </span>

                                        <span
                                            onClick={(e) =>
                                                handleDeleteConversation(e, conv.id)
                                            }
                                            className="text-zinc-400 opacity-0 transition hover:text-rose-500 group-hover:opacity-100 dark:text-zinc-500 dark:hover:text-rose-400"
                                            aria-label="Delete conversation"
                                        >
                                            <Trash2 size={14} />
                                        </span>
                                    </>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Collections */}
                <div className="border-t border-zinc-200 p-3 dark:border-zinc-800/80">
                    {!sidebarCollapsed && (
                        <h2 className="mb-2 px-1 text-[11px] font-medium tracking-wide text-zinc-400 dark:text-zinc-500">
                            Collections
                        </h2>
                    )}

                    <div className={`max-h-40 space-y-1.5 overflow-y-auto ${sidebarCollapsed ? "flex flex-col items-center" : ""}`}>
                        {collections.map((collection) => (
                            sidebarCollapsed ? (
                                <button
                                    key={collection.id}
                                    onClick={() => toggleCollection(collection.id)}
                                    title={collection.name}
                                    className={`h-2 w-2 rounded-full transition ${selectedCollections.includes(collection.id)
                                        ? "bg-indigo-500"
                                        : "bg-zinc-300 dark:bg-zinc-700"
                                        }`}
                                />
                            ) : (
                                <label
                                    key={collection.id}
                                    className="flex cursor-pointer items-center gap-2 rounded-md px-1 py-1 text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
                                >
                                    <input
                                        type="checkbox"
                                        checked={selectedCollections.includes(collection.id)}
                                        onChange={() =>
                                            toggleCollection(collection.id)
                                        }
                                        className="accent-indigo-500"
                                    />

                                    <span className="truncate">
                                        {collection.name}
                                    </span>
                                </label>
                            )
                        ))}

                        {collections.length === 0 && !sidebarCollapsed && (
                            <p className="text-xs text-zinc-400 dark:text-zinc-600">
                                No collections yet.
                            </p>
                        )}
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex min-w-0 flex-1 flex-col bg-zinc-50 dark:bg-zinc-950">

                {/* Top bar */}
                <div className="flex h-16 shrink-0 items-center gap-3 border-b border-zinc-200 bg-white/90 px-4 backdrop-blur dark:border-zinc-800/80 dark:bg-zinc-950/90 lg:px-6">

                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 lg:hidden"
                        aria-label="Open sidebar"
                    >
                        ☰
                    </button>

                    <h1 className="truncate text-sm font-medium text-zinc-800 dark:text-zinc-200 sm:text-base">
                        {activeTitle}
                    </h1>

                    <div className="ml-auto flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-100 px-3 py-1.5 dark:border-zinc-800 dark:bg-zinc-900/80">
                        <span className="text-[11px] text-zinc-500 dark:text-zinc-500">
                            Requests
                        </span>
                        <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">
                            {aiRequestsRemaining}/15
                        </span>
                        <div className="h-1.5 w-14 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
                            <div
                                className={`h-full rounded-full transition-all ${requestsColor}`}
                                style={{ width: `${requestsPct}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Chat */}
                <div className="mx-auto flex min-h-0 w-full max-w-4xl flex-1 flex-col px-3 sm:px-6">

                    <div className="flex-1 space-y-6 overflow-y-auto scrollbar-hide py-6">

                        {messages.map((msg, index) => {
                            const isUser = msg.role === "user";
                            const hasSources =
                                !isUser &&
                                msg.sources &&
                                msg.sources.length > 0;

                            if (isUser) {
                                return (
                                    <div key={index} className="flex justify-end">
                                        <div className="max-w-[85%] rounded-2xl rounded-br-sm px-4 py-3 text-white shadow-sm sm:max-w-[75%] bg-[#8A3A22]">
                                            {msg.image && (
                                                <img
                                                    src={msg.image}
                                                    alt="Uploaded"
                                                    className="mb-2 max-h-48 rounded-lg border border-indigo-400/40"
                                                />
                                            )}
                                            <div className="prose prose-sm prose-invert max-w-none">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {msg.content}
                                                </ReactMarkdown>
                                            </div>
                                        </div>
                                    </div>
                                );
                            }

                            return (
                                <div key={index} className="flex items-start gap-3">
                                    <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
                                        <Bot size={16} strokeWidth={2.25} />
                                    </div>

                                    <div className="min-w-0 flex-1 pt-1">
                                        {msg.image && (
                                            <img
                                                src={msg.image}
                                                alt="Uploaded"
                                                className="mb-2 max-h-48 rounded-lg border border-zinc-200 dark:border-zinc-800"
                                            />
                                        )}

                                        <div className="prose prose-sm dark:prose-invert max-w-none text-zinc-800 dark:text-zinc-200">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {msg.content}
                                            </ReactMarkdown>
                                        </div>

                                        {msg.file && (
                                            <a
                                                href={msg.file.url}
                                                download
                                                className="mt-3 flex max-w-sm items-center gap-3 rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-3 transition-colors hover:border-indigo-300 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-indigo-500/40 dark:hover:bg-zinc-800/80"
                                            >
                                                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-green-500/10 text-green-600 dark:text-green-400">
                                                    📊
                                                </div>

                                                <div className="min-w-0">
                                                    <p className="truncate text-sm font-medium text-zinc-800 dark:text-zinc-200">
                                                        {msg.file.filename}
                                                    </p>

                                                    <p className="text-xs text-zinc-500">
                                                        Excel file · Click to download
                                                    </p>
                                                </div>
                                            </a>
                                        )}

                                        {hasSources && (
                                            <div className="mt-4 border-t border-zinc-200 pt-3 dark:border-zinc-800">
                                                <p className="mb-2 text-[11px] font-medium tracking-wide text-zinc-400 dark:text-zinc-500">
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
                                                                        className="block cursor-pointer rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-xs transition-colors hover:border-indigo-300 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-indigo-500/40 dark:hover:bg-zinc-800/80"
                                                                    >
                                                                        <p className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
                                                                            {source.title ||
                                                                                "Web Link"}
                                                                        </p>

                                                                        <p className="truncate text-zinc-500">
                                                                            {
                                                                                source.url
                                                                            }
                                                                        </p>
                                                                    </a>
                                                                );
                                                            }

                                                            {/* Document Source */ }
                                                            if (
                                                                source.type === "document" &&
                                                                source.documentType === "pdf"
                                                            ) {
                                                                return (
                                                                    <Link
                                                                        key={idx}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        to={`/documents/${source.documentId}?page=${source.page}&highlight=${encodeURIComponent(
                                                                            source.text || ""
                                                                        )}`}
                                                                        className="block cursor-pointer rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-xs transition-colors hover:border-indigo-300 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-indigo-500/40 dark:hover:bg-zinc-800/80"
                                                                    >
                                                                        <p className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
                                                                            {source.documentName || source.fileName || "Document"}
                                                                        </p>

                                                                        <p className="text-zinc-500">
                                                                            Page {source.page}
                                                                        </p>
                                                                    </Link>
                                                                );
                                                            }

                                                            {/* Audio Document Source */ }
                                                            if (
                                                                source.type === "document" &&
                                                                source.documentType === "audio"
                                                            ) {
                                                                return (
                                                                    <Link
                                                                        key={idx}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        to={`/audio/${source.documentId}?t=${source.startTime}&highlight=${encodeURIComponent(
                                                                            source.text || ""
                                                                        )}`}

                                                                        className="block cursor-pointer rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-xs transition-colors hover:border-indigo-300 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-indigo-500/40 dark:hover:bg-zinc-800/80"
                                                                    >
                                                                        <p className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
                                                                            🎧 {source.documentName || source.fileName || "Audio"}
                                                                        </p>

                                                                        <p className="text-zinc-500">
                                                                            At {formatTimestamp(source.startTime)}
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
                                                                            src={`${import.meta.env.VITE_API_URL}/ai-images/${source.path}`}
                                                                            alt="Generated Graph"
                                                                            className="max-w-full rounded-lg border border-zinc-200 dark:border-zinc-800"
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

                        {loading && statusMessage && (
                            <div className="flex items-center gap-3">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
                                    <Bot size={16} strokeWidth={2.25} />
                                </div>
                                <span className="animate-pulse text-sm text-zinc-500">
                                    {statusMessage}
                                </span>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form
                        onSubmit={handleSubmit}
                        className="mb-4 rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 dark:shadow-lg dark:shadow-black/20"
                    >
                        {/* Image Preview */}
                        {imagePreview && (
                            <div className="mb-3 flex items-start">
                                <div className="relative">
                                    <img
                                        src={imagePreview}
                                        alt="Selected"
                                        className="h-20 w-20 rounded-lg border border-zinc-200 object-cover dark:border-zinc-700"
                                    />

                                    <button
                                        type="button"
                                        onClick={() => {
                                            setSelectedImage(null);
                                        }}
                                        className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-rose-500 text-xs text-white hover:bg-rose-600"
                                    >
                                        ×
                                    </button>
                                </div>
                            </div>
                        )}

                        <div className="flex items-center gap-2">
                            {/* Image upload */}
                            <input
                                type="file"
                                accept="image/*"
                                id="image-upload"
                                className="hidden"
                                onChange={(e) => {
                                    const file = e.target.files?.[0];

                                    if (!file) return;

                                    setSelectedImage(file);
                                }}
                            />

                            <label
                                htmlFor="image-upload"
                                className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-full text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
                                aria-label="Attach image"
                            >
                                <ImagePlus size={18} />
                            </label>

                            {/* Web Search Toggle */}
                            <button
                                type="button"
                                onClick={() => setWebEnabled((prev) => !prev)}
                                className={`flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-2 text-xs font-medium transition-colors ${webEnabled
                                    ? "border-indigo-300 bg-indigo-50 text-indigo-700 dark:border-indigo-500/50 dark:bg-indigo-500/15 dark:text-indigo-300"
                                    : "border-zinc-300 text-zinc-500 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800"
                                    }`}
                            >
                                <Globe size={14} />
                                Web
                            </button>

                            {/* Query Input */}
                            <input
                                type="text"
                                placeholder="Ask something..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="min-w-0 flex-1 bg-transparent px-2 py-2 text-sm text-zinc-900 outline-none placeholder:text-zinc-400 dark:text-zinc-100 dark:placeholder:text-zinc-500"
                            />

                            {/* Send */}
                            <button
                                type="submit"
                                disabled={loading || !query.trim()}
                                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#E79070] text-black transition hover:bg-[#6B2D1A] cursor-pointer disabled:cursor-not-allowed disabled:opacity-40"
                                aria-label="Send message"
                            >
                                <Send size={16} />
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default AI;