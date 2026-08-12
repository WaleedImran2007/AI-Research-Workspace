import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../../api/api.js";

function CollectionDetails() {

    const { collectionId } = useParams();

    const [documents, setDocuments] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            const response = await api.get(`/documents/${collectionId}`);
            setDocuments(response.data);
        }

        catch (err) {
            console.error(err);
        }

        finally {
            setLoading(false);
        }
    };

    const uploadDocument = async () => {

        if (!selectedFile) {
            alert("Please select a PDF.");
            return;
        }

        const formData = new FormData();

        formData.append("file", selectedFile);

        try {

            await api.post(
                `/documents/${collectionId}`,
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                }
            );

            alert("Document uploaded successfully.");

            setSelectedFile(null);

            fetchDocuments();

        }

        catch (err) {
            console.error(err);
            alert("Failed to upload document.");
        }

    };

    const deleteDocument = async (id) => {

        if (!confirm("Delete this document?"))
            return;

        try {
            await api.delete(`/documents/document/${id}`);

            fetchDocuments();

        }

        catch (err) {
            console.error(err);
        }

    };

    return (
        <div className="mx-auto max-w-6xl px-6 py-10 text-zinc-900 dark:text-zinc-100">

            <Link
                to="/collections"
                className="text-blue-600 hover:underline dark:text-blue-400"
            >
                ← Back to Collections
            </Link>

            <h1 className="mt-6 mb-8 text-4xl font-bold">
                Documents
            </h1>

            {/* Upload */}

            <div className="mb-10 rounded-xl bg-white p-6 shadow dark:bg-zinc-900 dark:shadow-black/20">

                <input
                    type="file"
                    accept=".pdf,.csv,.xlsx,application/pdf,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                            setSelectedFile(file);
                        }
                    }}
                    className="text-sm text-zinc-700 file:mr-4 file:cursor-pointer file:rounded-lg file:border-0 file:bg-zinc-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-zinc-700 hover:file:bg-zinc-200 dark:text-zinc-300 dark:file:bg-zinc-800 dark:file:text-zinc-200 dark:hover:file:bg-zinc-700"
                />

                <button
                    onClick={uploadDocument}
                    className="ml-4 cursor-pointer rounded bg-blue-600 px-6 py-2 text-white transition-colors hover:bg-blue-700"
                >
                    Upload
                </button>

            </div>

            {/* Documents */}

            {
                loading ?

                    <p className="text-zinc-600 dark:text-zinc-400">
                        Loading...
                    </p>

                    :

                    documents.length === 0 ?

                        <div className="rounded-xl bg-white p-12 text-center shadow dark:bg-zinc-900 dark:shadow-black/20">

                            <h2 className="text-2xl font-semibold">
                                No Documents
                            </h2>

                        </div>

                        :

                        <div className="space-y-4">

                            {
                                documents.map(document => (

                                    <div
                                        key={document.id}
                                        className="flex items-center justify-between rounded-xl bg-white p-5 shadow dark:bg-zinc-900 dark:shadow-black/20"
                                    >

                                        <div>

                                            <h2 className="font-semibold text-zinc-900 dark:text-zinc-100">
                                                📄 {document.originalName}
                                            </h2>

                                            <p className="text-sm text-gray-500 dark:text-zinc-400">
                                                {document.status}
                                            </p>

                                        </div>

                                        <button
                                            onClick={() =>
                                                deleteDocument(document.id)
                                            }
                                            className="cursor-pointer rounded bg-red-600 px-4 py-2 text-white transition-colors hover:bg-red-700"
                                        >
                                            Delete
                                        </button>

                                    </div>

                                ))
                            }

                        </div>
            }

        </div>
    );
}

export default CollectionDetails;