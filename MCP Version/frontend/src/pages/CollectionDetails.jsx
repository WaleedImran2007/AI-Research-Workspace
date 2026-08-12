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
        <div className="mx-auto max-w-6xl px-6 py-10">

            <Link
                to="/collections"
                className="text-blue-600 hover:underline"
            >
                ← Back to Collections
            </Link>

            <h1 className="mt-6 mb-8 text-4xl font-bold">
                Documents
            </h1>

            {/* Upload */}

            <div className="mb-10 rounded-xl bg-white p-6 shadow">

                <input
                    type="file"
                    accept=".pdf,.csv,.xlsx,application/pdf,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                            setSelectedFile(file);
                        }
                    }}
                />

                <button
                    onClick={uploadDocument}
                    className="cursor-pointer ml-4 rounded bg-blue-600 px-6 py-2 text-white"
                >
                    Upload
                </button>

            </div>

            {/* Documents */}

            {
                loading ?

                    <p>Loading...</p>

                    :

                    documents.length === 0 ?

                        <div className="rounded-xl bg-white p-12 text-center shadow">

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
                                        className="flex items-center justify-between rounded-xl bg-white p-5 shadow"
                                    >

                                        <div>

                                            <h2 className="font-semibold">
                                                📄 {document.originalName}
                                            </h2>

                                            <p className="text-sm text-gray-500">
                                                {document.status}
                                            </p>

                                        </div>

                                        <button
                                            onClick={() =>
                                                deleteDocument(document.id)
                                            }
                                            className="cursor-pointer rounded bg-red-600 px-4 py-2 text-white"
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