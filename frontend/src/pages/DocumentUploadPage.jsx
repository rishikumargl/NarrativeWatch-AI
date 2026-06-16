import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, File, AlertCircle, CheckCircle, X, ArrowLeft, Home } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export default function DocumentUploadPage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const extractTextFromPDF = async (file) => {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let fullText = '';

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(' ');
        fullText += pageText + '\n';
      }

      return fullText;
    } catch (error) {
      console.error('Error extracting PDF text:', error);
      throw new Error(`Failed to extract text from PDF: ${error.message}`);
    }
  };

  const handleFiles = async (files) => {
    const newDocs = [];

    for (const file of files) {
      if (file.type === 'text/plain' || file.type === 'application/pdf') {
        try {
          let content = '';

          if (file.type === 'text/plain') {
            content = await file.text();
          } else if (file.type === 'application/pdf') {
            content = await extractTextFromPDF(file);
          }

          // Extract title from filename
          const title = file.name.replace(/\.[^/.]+$/, '');

          newDocs.push({
            id: Math.random().toString(36).substr(2, 9),
            title,
            content,
            fileName: file.name,
            fileSize: file.size,
            status: 'ready',
            error: null
          });
        } catch (error) {
          newDocs.push({
            id: Math.random().toString(36).substr(2, 9),
            title: file.name,
            content: '',
            fileName: file.name,
            fileSize: file.size,
            status: 'error',
            error: error.message
          });
        }
      } else {
        newDocs.push({
          id: Math.random().toString(36).substr(2, 9),
          title: file.name,
          content: '',
          fileName: file.name,
          fileSize: file.size,
          status: 'error',
          error: 'Only .txt and .pdf files are supported'
        });
      }
    }

    setDocuments([...documents, ...newDocs]);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    handleFiles(Array.from(files));
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    handleFiles(Array.from(files));
  };

  const removeDocument = (id) => {
    setDocuments(documents.filter(doc => doc.id !== id));
  };

  const editDocument = (id, field, value) => {
    setDocuments(documents.map(doc =>
      doc.id === id ? { ...doc, [field]: value } : doc
    ));
  };

  const uploadDocuments = async () => {
    const validDocs = documents.filter(doc => doc.status !== 'error' && doc.content);

    if (validDocs.length === 0) {
      setUploadStatus({
        type: 'error',
        message: 'No valid documents to upload. Please add text or PDF files.'
      });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

      // Prepare documents for batch upload
      const uploadPayload = {
        documents: validDocs.map(doc => ({
          title: doc.title || 'Untitled',
          content: doc.content,
          source_url: `uploaded://${doc.fileName}`,
          source_domain: 'user-uploaded',
          author: 'Unknown',
          category: 'general',
          tags: ['user-uploaded']
        }))
      };

      console.log(`Uploading ${uploadPayload.documents.length} documents...`);

      const response = await fetch(`${apiUrl}/api/v1/documents/upload-batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(uploadPayload)
      });

      const result = await response.json();

      if (result.success || result.ingested_count > 0) {
        setUploadStatus({
          type: 'success',
          message: `Successfully uploaded ${result.ingested_count} document(s)!`,
          details: result
        });

        // Clear documents after successful upload
        setTimeout(() => {
          setDocuments([]);
          setUploadStatus(null);
        }, 2000);
      } else {
        setUploadStatus({
          type: 'error',
          message: `Failed to upload documents: ${result.message || 'Unknown error'}`,
          details: result
        });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        type: 'error',
        message: `Upload failed: ${error.message}`
      });
    } finally {
      setUploading(false);
    }
  };

  const getDocumentStats = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/v1/documents/stats`);
      const stats = await response.json();

      console.log('Document statistics:', stats);
      alert(`
Documents in RAG System:
- Total: ${stats.total_documents}
- Sources: ${stats.unique_sources}
- Categories: ${stats.unique_categories}
- With embeddings: ${stats.with_embeddings}
      `);
    } catch (error) {
      console.error('Error fetching stats:', error);
      alert('Failed to fetch document statistics');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Background animations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Header */}
      <nav className="relative z-10 border-b border-gray-800/30 bg-gray-900/20 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/projects')}
              className="p-2 hover:bg-gray-800/50 rounded-lg transition-colors"
              title="Back to projects"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400 hover:text-white transition-colors" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">📄 Document Upload</h1>
              <p className="text-gray-400 text-sm mt-1">Upload documents for RAG system enrichment</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all duration-300 hover:border-blue-500/50 group"
          >
            <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
            Home
          </button>
        </div>
      </nav>

      {/* Main content */}
      <div className="relative z-10 container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Upload area */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
              dragActive
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-700 bg-gray-900/40 hover:border-gray-600'
            }`}
          >
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">
              Drag files here or click to upload
            </h2>
            <p className="text-gray-400 mb-6">
              Supported formats: .txt (text) and .pdf files
            </p>
            <label className="inline-block">
              <input
                type="file"
                multiple
                accept=".txt,.pdf"
                onChange={handleFileInput}
                className="hidden"
              />
              <span className="inline-block px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 cursor-pointer transition-all">
                Select Files
              </span>
            </label>
          </div>

          {/* Status messages */}
          {uploadStatus && (
            <div className={`mt-6 p-4 rounded-lg border ${
              uploadStatus.type === 'success'
                ? 'border-green-500/50 bg-green-500/10'
                : 'border-red-500/50 bg-red-500/10'
            }`}>
              <div className="flex items-start gap-3">
                {uploadStatus.type === 'success' ? (
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <p className={uploadStatus.type === 'success' ? 'text-green-300' : 'text-red-300'}>
                    {uploadStatus.message}
                  </p>
                  {uploadStatus.details && (
                    <p className="text-sm text-gray-400 mt-2">
                      Ingested: {uploadStatus.details.ingested_count} |
                      Skipped: {uploadStatus.details.skipped_count} |
                      Failed: {uploadStatus.details.failed_count}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Documents list */}
          {documents.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-white mb-4">
                Documents ({documents.length})
              </h3>

              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={`p-4 rounded-lg border ${
                      doc.status === 'error'
                        ? 'border-red-500/30 bg-red-500/5'
                        : 'border-gray-700 bg-gray-800/50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <File className={`w-5 h-5 flex-shrink-0 mt-1 ${
                          doc.status === 'error' ? 'text-red-400' : 'text-blue-400'
                        }`} />
                        <div className="flex-1">
                          <input
                            type="text"
                            value={doc.title}
                            onChange={(e) => editDocument(doc.id, 'title', e.target.value)}
                            className="text-white font-semibold bg-transparent border-b border-gray-700 focus:border-blue-500 outline-none w-full mb-1"
                            placeholder="Document title"
                          />
                          <p className="text-gray-400 text-sm">
                            {doc.fileName} ({(doc.fileSize / 1024).toFixed(2)} KB)
                          </p>
                          {doc.status === 'error' && (
                            <p className="text-red-400 text-sm mt-1">{doc.error}</p>
                          )}
                          {doc.content && (
                            <p className="text-gray-500 text-xs mt-1">
                              {doc.content.length} characters extracted
                            </p>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => removeDocument(doc.id)}
                        className="p-2 hover:bg-gray-700 rounded transition-colors"
                      >
                        <X className="w-5 h-5 text-gray-400" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action buttons */}
              <div className="mt-6 flex gap-4">
                <button
                  onClick={uploadDocuments}
                  disabled={uploading || documents.filter(d => d.status !== 'error').length === 0}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Uploading...' : 'Upload Documents'}
                </button>
                <button
                  onClick={() => setDocuments([])}
                  className="px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all"
                >
                  Clear All
                </button>
                <button
                  onClick={getDocumentStats}
                  className="px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all"
                >
                  📊 Stats
                </button>
              </div>
            </div>
          )}

          {/* Info box */}
          <div className="mt-12 bg-gray-900/40 border border-gray-800/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">About Document Upload</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">→</span>
                <span>Upload <strong>text files (.txt)</strong> or <strong>PDF files (.pdf)</strong></span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">→</span>
                <span>Documents are indexed and stored in the <strong>RAG system</strong></span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">→</span>
                <span>Embeddings are generated for <strong>semantic similarity search</strong></span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">→</span>
                <span>Historical context enriches <strong>future article analysis</strong></span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">→</span>
                <span>Edit titles before upload to improve searchability</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
