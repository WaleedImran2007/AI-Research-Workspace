import { useParams, useSearchParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import api from "../../api/api.js";

import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

function normalizeText(text) {
  if (!text) return "";
  return text
    .replace(/\s+/g, " ") // collapse all whitespace
    .trim()
    .toLowerCase();
}

function PDFViewer() {
  const { documentId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  const currentPage = Number(searchParams.get("page")) || 1;
  const highlight = searchParams.get("highlight") || "";

  const [numPages, setNumPages] = useState(null);
  const [spans, setSpans] = useState([]);
  const [pageDimensions, setPageDimensions] = useState(null);
  const [loading, setLoading] = useState(true);

  // Scaling factor based on page dimensions (standard base width/height of 720x540)
  const scaleX = pageDimensions ? pageDimensions.width / 720 : 1;
  const scaleY = pageDimensions ? pageDimensions.height / 540 : 1;

  const normalizedHighlight = normalizeText(highlight);

  // Match bounding box spans with current highlighted text
  const matchedSpans = spans.filter((span) => {
    if (!normalizedHighlight) return false;
    const normSpanText = normalizeText(span.text);
    return normSpanText && normalizedHighlight.includes(normSpanText);
  });

  // Fetch page bounding box / layout meta on page or document change
  useEffect(() => {
    async function fetchLayout() {
      setLoading(true);
      try {
        const res = await api.get(`/documents/${documentId}/layout/${currentPage}`);
        setSpans(res.data.spans || []);
      } catch (err) {
        console.error("Error fetching page layout:", err);
        setSpans([]);
      } finally {
        setLoading(false);
      }
    }

    fetchLayout();
  }, [documentId, currentPage]);

  // Page switcher handler
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= (numPages || 1)) {
      setSearchParams({ page: newPage, highlight });
    }
  };

  const pdfUrl = `${import.meta.env.VITE_API_URL}/documents/${documentId}/view/pdf`;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6 space-y-4">
      {/* Navigation & Toolbar Header */}
      <div className="bg-white shadow px-4 py-2 rounded-lg flex items-center space-x-4">
        <button
          disabled={currentPage <= 1}
          onClick={() => handlePageChange(currentPage - 1)}
          className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-sm font-medium">
          Page {currentPage} of {numPages || "--"}
        </span>
        <button
          disabled={currentPage >= numPages}
          onClick={() => handlePageChange(currentPage + 1)}
          className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>

      {/* PDF Container */}
      <div className="relative shadow-lg border border-gray-300 rounded overflow-hidden bg-white">
        <Document
          file={pdfUrl}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          loading={<div className="p-10 text-gray-500">Loading document...</div>}
        >
          <Page
            pageNumber={currentPage}
            onLoadSuccess={(page) => {
              setPageDimensions({
                width: page.width,
                height: page.height,
              });
            }}
          />
        </Document>

        {/* Highlight Overlays */}
        {!loading &&
          matchedSpans.map((span, index) => {
            const [x0, y0, x1, y1] = span.bbox;

            return (
              <div
                key={index}
                className="absolute bg-yellow-300 opacity-40 pointer-events-none transition-all"
                style={{
                  left: `${x0 * scaleX}px`,
                  top: `${y0 * scaleY}px`,
                  width: `${(x1 - x0) * scaleX}px`,
                  height: `${(y1 - y0) * scaleY}px`,
                }}
              />
            );
          })}
      </div>
    </div>
  );
}

export default PDFViewer;