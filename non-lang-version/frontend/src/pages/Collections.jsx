import { useEffect, useState } from "react";
import api from '../../api/api.js';
import { useNavigate, useSearchParams, Link } from "react-router-dom";

function Collections() {
    const [collections, setCollections] = useState([]);
    const [loading, setLoading] = useState(true);

    const [searchParams] = useSearchParams();
    const collectionId = searchParams.get("collectionId");

    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        name: "",
        description: "",
    });

    const fetchCollections = async () => {
        try {
            const response = await api.get("/collections");
            setCollections(response.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchCollectionById = async (id) => {
        try {
            const response = await api.get(`/collections/${id}`);
            setFormData({
                name: response.data.name,
                description: response.data.description,
            });

        } catch (err) {
            console.error(err);
        }
    }

    useEffect(() => {
        fetchCollections();
    }, []);

    useEffect(() => {
        if (collectionId) {
            fetchCollectionById(collectionId);
        }

    }, [collectionId]);


    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            if (collectionId) {
                await api.put(`/collections/${collectionId}`, formData);
                alert("Collection updated successfully!");
            }

            else {
                await api.post("/collections", formData);
                alert("Collection created successfully!");
            }


            setFormData({
                name: "",
                description: "",
            });

            fetchCollections();
            navigate("/collections");
        } catch (err) {
            console.error(err);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Delete this collection?")) return;

        try {
            await api.delete(`/collections/${id}`);
            fetchCollections();
        } catch (err) {
            console.error(err);
        }
    };

    const handleEdit = (id) => {
        navigate(`/collections?collectionId=${id}`);
    }

    if (loading) {
        return (
            <div className="py-20 text-center text-lg">
                Loading collections...
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-7xl px-6 py-10">

            <h1 className="mb-8 text-4xl font-bold">
                My Collections
            </h1>

            {/* Create Collection */}

            <div className="mb-10 rounded-xl bg-white p-6 shadow">

                <h2 className="mb-4 text-2xl font-semibold">
                    Create Collection
                </h2>

                <form
                    onSubmit={handleSubmit}
                    className="space-y-4"
                >

                    <input
                        type="text"
                        name="name"
                        placeholder="Collection Name"
                        value={formData.name}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3"
                        required
                    />

                    <textarea
                        name="description"
                        placeholder="Description"
                        value={formData.description}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3"
                        rows="3"
                    />

                    <button
                        className="cursor-pointer rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
                    >
                        {
                            collectionId ? "Update Collection" : "Create Collection"
                        }

                    </button>

                </form>

            </div>

            {/* Collections */}

            {collections.length === 0 ? (
                <div className="rounded-xl bg-white p-12 text-center shadow">

                    <h2 className="mb-2 text-2xl font-semibold">
                        No Collections Yet
                    </h2>

                    <p className="text-gray-600">
                        Create your first collection to organize your documents.
                    </p>

                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">

                    {collections.map((collection) => (
                        <div
                            key={collection.id}
                            className="rounded-xl bg-white p-6 shadow"
                        >

                            <Link to={`/collections/${collection.id}`} className="block mb-2 text-2xl font-bold hover:text-blue-600 hover:underline">
                                <h2 className="mb-2 text-xl font-bold">
                                    {collection.name}
                                </h2>
                            </Link>

                            <p className="mb-6 text-gray-600">
                                {collection.description || "No description"}
                            </p>

                            <div className="flex gap-3">

                                <button
                                    onClick={
                                        () => handleEdit(collection.id)
                                    }

                                    className="cursor-pointer rounded-lg bg-yellow-500 px-4 py-2 text-white hover:bg-yellow-600"
                                >
                                    Edit
                                </button>

                                <button
                                    onClick={() =>
                                        handleDelete(collection.id)
                                    }
                                    className="cursor-pointer rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700"
                                >
                                    Delete
                                </button>

                            </div>

                        </div>
                    ))}

                </div>
            )}

        </div>
    );
}

export default Collections;