import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiFileText, FiMoreVertical, FiSearch, FiFilter, 
  FiMessageSquare, FiBookOpen, FiPlayCircle, FiExternalLink, FiLayers, FiTrash2, FiEdit2, FiDownload, FiCheckCircle
} from 'react-icons/fi';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { documentService } from '../services/documentService';
import Button from '../components/ui/Button';

const Documents = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMenuOpen, setActionMenuOpen] = useState(null); // stores doc id
  const [renamingDoc, setRenamingDoc] = useState(null); // stores doc id
  const [newName, setNewName] = useState('');
  
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, name_asc, name_desc, size
  const [previewDoc, setPreviewDoc] = useState(null); // stores doc object for preview

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await documentService.getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error("Failed to load documents", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await documentService.deleteDocument(id);
      setDocuments(documents.filter(d => d.id !== id));
      setActionMenuOpen(null);
    } catch (err) {
      console.error(err);
      alert("Failed to delete document.");
    }
  };

  const handleProcessDocument = async (id) => {
    try {
      // Optimistically update status to 'processing'
      setDocuments(documents.map(d => d.id === id ? { ...d, embedding_status: 'processing', upload_status: 'processing' } : d));
      await documentService.processDocument(id);
      // Processing successful, update state
      setDocuments(documents.map(d => d.id === id ? { ...d, embedding_status: 'completed', upload_status: 'completed' } : d));
    } catch (err) {
      console.error(err);
      alert("Failed to process document.");
      // Revert to failed state
      setDocuments(documents.map(d => d.id === id ? { ...d, embedding_status: 'failed', upload_status: 'failed' } : d));
    }
  };

  const startRename = (doc) => {
    setRenamingDoc(doc.id);
    setNewName(doc.filename);
    setActionMenuOpen(null);
  };

  const handleRename = async (id) => {
    try {
      if (newName.trim() === '') {
        setRenamingDoc(null);
        return;
      }
      const updatedDoc = await documentService.renameDocument(id, newName);
      setDocuments(documents.map(d => d.id === id ? { ...d, filename: updatedDoc.filename } : d));
    } catch (err) {
      console.error(err);
      alert("Failed to rename document.");
    } finally {
      setRenamingDoc(null);
    }
  };

  const handleDownload = (id) => {
    const url = documentService.getDownloadUrl(id);
    window.open(url, '_blank');
    setActionMenuOpen(null);
  };

  const handlePreview = (doc) => {
    setPreviewDoc(doc);
    setActionMenuOpen(null);
  };

  const filteredDocs = documents
    .filter(doc => doc.filename.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest': return new Date(b.created_at) - new Date(a.created_at);
        case 'oldest': return new Date(a.created_at) - new Date(b.created_at);
        case 'name_asc': return a.filename.localeCompare(b.filename);
        case 'name_desc': return b.filename.localeCompare(a.filename);
        case 'size': return b.file_size - a.file_size;
        default: return 0;
      }
    });

  return (
    <div className="space-y-8 max-w-7xl mx-auto relative pt-2">
      {/* Preview Modal */}
      <AnimatePresence>
        {previewDoc && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 lg:p-10"
          >
            <div className="bg-white border border-gray-200 w-full max-w-5xl h-[85vh] rounded-2xl overflow-hidden flex flex-col shadow-md">
              <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
                <h3 className="font-bold text-gray-900 truncate pr-4">{previewDoc.filename}</h3>
                <div className="flex gap-2">
                  <Button variant="secondary" onClick={() => handleDownload(previewDoc.id)}>Download</Button>
                  <Button variant="neutral" onClick={() => setPreviewDoc(null)}>Close</Button>
                </div>
              </div>
              <div className="flex-1 bg-gray-50">
                <iframe 
                  src={documentService.getDownloadUrl(previewDoc.id)} 
                  className="w-full h-full border-none"
                  title="Document Preview"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">My Documents</h1>
          <p className="text-[var(--color-text-muted)]">Manage your course materials and launch AI tools directly from your documents.</p>
        </div>
        <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto items-center">
          <div className="relative flex-1 w-full md:w-64">
            <FiSearch className="absolute left-3 top-3 text-gray-600" />
            <input 
              type="text" 
              placeholder="Search documents..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] focus:outline-none focus:border-blue-500 transition-colors shadow-inner"
            />
          </div>
          
          <div className="relative">
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="appearance-none pl-10 pr-8 py-2 rounded-xl bg-gray-50 border border-gray-200 text-gray-700 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="name_asc">Name (A-Z)</option>
              <option value="name_desc">Name (Z-A)</option>
              <option value="size">Largest File</option>
            </select>
            <FiFilter className="absolute left-3 top-3 text-gray-600" />
          </div>

          <Button variant="primary" onClick={() => window.location.href='/upload'}>
            Upload Document
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-gray-600 py-12">Loading documents...</div>
      ) : filteredDocs.length === 0 ? (
        <div className="text-center text-gray-600 py-12 bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] rounded-2xl">
          <FiFileText className="text-4xl mb-4 mx-auto opacity-50" />
          <p>No documents found.</p>
          <Button variant="primary" className="mt-4" onClick={() => window.location.href='/upload'}>Upload Document</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredDocs.map((doc, idx) => {
            const isIndexed = doc.embedding_status === 'completed' || doc.upload_status === 'completed';
            
            return (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="h-full"
              >
                <Card hover={false} className="h-full flex flex-col group overflow-visible relative">
                  {/* Thumbnail Area */}
                  <div className={`-mx-6 -mt-6 h-28 bg-gray-50 flex items-center justify-center border-b border-[var(--color-border-subtle)] relative`}>
                    <FiFileText className="text-5xl text-gray-300 group-hover:scale-110 transition-transform duration-500" />
                    <Badge 
                      variant={isIndexed ? 'success' : 'warning'} 
                      className={`absolute top-3 right-3 shadow-sm ${!isIndexed ? 'bg-amber-100 text-amber-700 border border-amber-200' : ''}`}
                    >
                      {isIndexed ? 'Ready for AI' : (doc.embedding_status === 'processing' ? 'Processing...' : 'Unprocessed')}
                    </Badge>
                  </div>

                  {/* Info */}
                  <div className="pt-5 flex-1 relative">
                    <div className="absolute top-2 right-0">
                      <button 
                        onClick={() => setActionMenuOpen(actionMenuOpen === doc.id ? null : doc.id)}
                        className="p-1 text-gray-600 hover:text-gray-900 transition-colors"
                      >
                        <FiMoreVertical />
                      </button>
                      
                      <AnimatePresence>
                        {actionMenuOpen === doc.id && (
                          <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="absolute right-0 top-6 w-40 bg-gray-50 border border-gray-200 shadow-md rounded-lg py-1 z-50"
                          >
                            <button onClick={() => handlePreview(doc)} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 flex items-center gap-2">
                              <FiExternalLink /> Preview
                            </button>
                            <button onClick={() => startRename(doc)} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 flex items-center gap-2">
                              <FiEdit2 /> Rename
                            </button>
                            <button onClick={() => handleDownload(doc.id)} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 flex items-center gap-2">
                              <FiDownload /> Download
                            </button>
                            <button onClick={() => handleDelete(doc.id)} className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/20 flex items-center gap-2">
                              <FiTrash2 /> Delete
                            </button>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {renamingDoc === doc.id ? (
                      <div className="mb-2 flex items-center gap-2 pr-6">
                        <input 
                          type="text" 
                          value={newName} 
                          onChange={(e) => setNewName(e.target.value)} 
                          className="w-full bg-white border border-gray-200 rounded px-2 py-1 text-sm text-gray-900 focus:outline-none focus:border-blue-500"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleRename(doc.id);
                            if (e.key === 'Escape') setRenamingDoc(null);
                          }}
                        />
                        <button onClick={() => handleRename(doc.id)} className="text-emerald-400 p-1 hover:bg-emerald-500/20 rounded"><FiCheckCircle/></button>
                      </div>
                    ) : (
                      <h3 className="text-lg font-bold text-gray-900 mb-2 truncate group-hover:text-blue-600 transition-colors pr-6">
                        {doc.filename}
                      </h3>
                    )}
                    
                    <div className="flex items-center gap-4 text-xs font-medium text-[var(--color-text-muted)]">
                      <span>{doc.content_type?.includes('pdf') ? 'PDF' : 'DOC'}</span>
                      <span>•</span>
                      <span>{Math.round(doc.file_size / 1024)} KB</span>
                      <span>•</span>
                      <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                    {isIndexed ? (
                      <div className="mt-4 pt-3 border-t border-[var(--color-border-subtle)]">
                        <p className="text-[10px] font-bold text-gray-500 mb-2 uppercase tracking-wider">AI Actions</p>
                        <div className="grid grid-cols-2 gap-2">
                          <button 
                            onClick={() => window.location.href = `/tutor?doc=${doc.id}`}
                            className="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium hover:bg-blue-100 hover:text-blue-700 transition-colors border border-blue-200"
                          >
                            <FiMessageSquare /> Ask AI
                          </button>
                          <button 
                            onClick={() => window.location.href = `/notes?doc=${doc.id}`}
                            className="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-indigo-50 text-indigo-600 rounded-lg text-xs font-medium hover:bg-indigo-100 hover:text-indigo-700 transition-colors border border-indigo-200"
                          >
                            <FiBookOpen /> Notes
                          </button>
                          <button 
                            onClick={() => window.location.href = `/quiz?doc=${doc.id}`}
                            className="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-emerald-50 text-emerald-600 rounded-lg text-xs font-medium hover:bg-emerald-100 hover:text-emerald-700 transition-colors border border-emerald-200"
                          >
                            <FiPlayCircle /> Quiz
                          </button>
                          <button 
                            onClick={() => window.location.href = `/flashcards?doc=${doc.id}`}
                            className="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-orange-50 text-orange-600 rounded-lg text-xs font-medium hover:bg-orange-100 hover:text-orange-700 transition-colors border border-orange-200"
                          >
                            <FiLayers /> Flashcards
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-4 pt-3 border-t border-[var(--color-border-subtle)]">
                        {doc.embedding_status === 'processing' || doc.upload_status === 'processing' ? (
                          <div className="py-4 text-center">
                            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                            <p className="text-xs text-gray-500">Processing document...</p>
                          </div>
                        ) : (
                          <Button 
                            variant={doc.embedding_status === 'failed' || doc.upload_status === 'failed' ? 'danger' : 'primary'}
                            className="w-full text-sm py-2"
                            onClick={() => handleProcessDocument(doc.id)}
                          >
                            {doc.embedding_status === 'failed' || doc.upload_status === 'failed' ? 'Retry Processing' : 'Process Document'}
                          </Button>
                        )}
                      </div>
                    )}
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Documents;
