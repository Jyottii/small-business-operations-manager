import React, { useState, useEffect } from 'react';
import { 
  FileText, Image, File, UploadCloud, Download, Trash2, 
  Search, Loader2, Plus, CheckCircle2, AlertCircle 
} from 'lucide-react';
import { Card, CardBody } from '../../components/ui/Card';
import { apiClient } from '../../api/client';
import { useAuth } from '../../context/AuthContext';

export default function Documents() {
  const { role } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [docName, setDocName] = useState('');
  const [docType, setDocType] = useState('General');
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const canManage = ['Owner', 'Admin', 'Manager'].includes(role);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/documents?page_size=100');
      setDocuments(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setErrorMsg('Please select a file to upload.');
      return;
    }

    try {
      setUploading(true);
      setErrorMsg(null);
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('name', docName || uploadFile.name);
      formData.append('document_type', docType);

      await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setShowUploadModal(false);
      setUploadFile(null);
      setDocName('');
      setDocType('General');
      fetchDocuments();
    } catch (err) {
      setErrorMsg(err?.response?.data?.detail || err?.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (doc) => {
    try {
      const res = await apiClient.get(`/documents/${doc.id}/download`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: doc.mime_type || 'application/octet-stream' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.file_name);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download document: ' + (err?.message || 'Error'));
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to permanently delete this document?')) return;
    try {
      await apiClient.delete(`/documents/${docId}`);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (err) {
      alert('Failed to delete document: ' + (err?.message || 'Error'));
    }
  };

  const getIcon = (mimeType) => {
    if (mimeType?.includes('pdf')) return <FileText size={24} className="text-red-500" />;
    if (mimeType?.includes('image')) return <Image size={24} className="text-blue-500" />;
    if (mimeType?.includes('sheet') || mimeType?.includes('csv')) return <File size={24} className="text-green-600" />;
    return <File size={24} className="text-gray-500" />;
  };

  const filtered = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          doc.file_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = categoryFilter === 'ALL' || doc.document_type === categoryFilter;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Document Vault</h1>
          <p className="text-sm text-gray-500 mt-1">
            Secure multi-tenant file archive for invoices, receipts, tax documents, and contracts.
          </p>
        </div>
        <button
          onClick={() => { setErrorMsg(null); setShowUploadModal(true); }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow-sm text-sm font-semibold hover:bg-blue-700 flex items-center gap-2"
        >
          <UploadCloud size={18} /> Upload Document
        </button>
      </div>

      {/* Filter toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input 
            type="text" 
            placeholder="Search documents by title or filename..." 
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select 
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="border border-gray-300 rounded-lg py-2 px-3 text-sm focus:ring-blue-500 bg-white"
        >
          <option value="ALL">All Categories</option>
          <option value="Invoice">Invoices</option>
          <option value="Receipt">Receipts</option>
          <option value="Legal">Legal & Contracts</option>
          <option value="General">General</option>
        </select>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-20 text-gray-500">
          <Loader2 className="animate-spin mr-2" size={24} /> Loading document repository...
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
          <FileText className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No Documents Found</h3>
          <p className="mt-1 text-sm text-gray-500">Upload business documents or invoices to keep an audit trail.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(doc => (
            <Card key={doc.id} className="hover:border-blue-300 transition-colors border border-gray-200">
              <CardBody className="p-4 flex flex-col justify-between h-full">
                <div className="flex items-start space-x-3">
                  <div className="p-3 bg-gray-50 rounded-lg flex-shrink-0">
                    {getIcon(doc.mime_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">{doc.name}</p>
                    <p className="text-xs text-gray-500 truncate">{doc.file_name}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                        {doc.document_type || 'General'}
                      </span>
                      {doc.file_size && (
                        <span className="text-[10px] text-gray-400">
                          {(doc.file_size / 1024).toFixed(1)} KB
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs">
                  <span className="text-gray-400">
                    {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleDownload(doc)}
                      className="p-1.5 text-gray-500 hover:text-blue-600 rounded hover:bg-blue-50"
                      title="Download file"
                    >
                      <Download size={16} />
                    </button>
                    {canManage && (
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-red-50"
                        title="Delete file"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Upload Document</h2>
            {errorMsg && <p className="mb-4 text-xs text-red-600 bg-red-50 p-2 rounded">{errorMsg}</p>}
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Select File *</label>
                <input
                  type="file"
                  required
                  onChange={(e) => {
                    const f = e.target.files[0];
                    setUploadFile(f);
                    if (f && !docName) setDocName(f.name);
                  }}
                  className="mt-1 w-full text-xs text-gray-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Document Name</label>
                <input
                  type="text"
                  placeholder="e.g. Q1 Tax Receipt"
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Category</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
                >
                  <option value="Invoice">Invoice</option>
                  <option value="Receipt">Receipt</option>
                  <option value="Legal">Legal & Contracts</option>
                  <option value="General">General Business</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {uploading && <Loader2 size={16} className="animate-spin" />}
                  Upload Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
