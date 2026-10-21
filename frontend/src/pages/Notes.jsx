import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiBookOpen, FiDownload, FiCheckCircle, FiFileText,
  FiFolder, FiStar, FiTag, FiSearch, FiPlus, FiTrash2, FiClock, FiEdit2, FiX
} from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { noteService } from '../services/noteService';
import { documentService } from '../services/documentService';
import { useNavigate } from 'react-router-dom';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import React from 'react';

const Notes = () => {
  const navigate = useNavigate();
  const [folders, setFolders] = useState([]);
  const [tags, setTags] = useState([]);
  const [notes, setNotes] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isDocumentsLoading, setIsDocumentsLoading] = useState(true);

  const [selectedFolder, setSelectedFolder] = useState(null);
  const [filterFavorite, setFilterFavorite] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterDocumentId, setFilterDocumentId] = useState('');

  const [isGenerating, setIsGenerating] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Delete Modal State
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [noteToDelete, setNoteToDelete] = useState(null);

  // Extract document ID from URL if present
  const searchParams = new URLSearchParams(window.location.search);
  const urlDocumentId = searchParams.get('doc');

  // Generator State
  const [topic, setTopic] = useState('');
  const [instructions, setInstructions] = useState('');
  const [documentId, setDocumentId] = useState(urlDocumentId || '');
  const [noteType, setNoteType] = useState('comprehensive');
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    loadSidebarData();
    loadDocuments();
    if (urlDocumentId) {
      loadDocumentNotes(urlDocumentId);
      setIsModalOpen(true); // Auto open modal if coming from document
    } else {
      loadNotes();
    }
  }, []);

  useEffect(() => {
    if (!urlDocumentId) loadNotes();
  }, [selectedFolder, filterFavorite, searchQuery]);

  const loadDocumentNotes = async (docId) => {
    try {
      const docNotes = await noteService.getDocumentNotes(docId);
      setNotes(docNotes);
    } catch (err) {
      console.error(err);
    }
  };

  const loadDocuments = async () => {
    try {
      setIsDocumentsLoading(true);
      const docs = await documentService.getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401 || err.response?.status === 403) {
        setErrorMsg("Your session has expired. Please log in again.");
      } else {
        setErrorMsg("Unable to load your documents. Please try again.");
      }
    } finally {
      setIsDocumentsLoading(false);
    }
  };

  const loadSidebarData = async () => {
    try {
      const [f, t] = await Promise.all([
        noteService.getFolders(),
        noteService.getTags()
      ]);
      setFolders(f);
      setTags(t);
    } catch (err) {
      console.error(err);
    }
  };

  const loadNotes = async () => {
    try {
      const n = await noteService.getNotes({
        folder_id: selectedFolder?.id,
        is_favorite: filterFavorite ? true : undefined,
        search: searchQuery || undefined
      });
      setNotes(n);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!documentId) {
      setErrorMsg("Please select a document.");
      return;
    }
    if (!topic.trim()) {
      setErrorMsg("Please enter a topic.");
      return;
    }
    
    setIsGenerating(true);
    setErrorMsg(null);

    try {
      const savedNote = await noteService.generateNote({
        topic: topic || "Document Synthesis",
        instructions: instructions || undefined,
        note_type: noteType,
        folder_id: selectedFolder?.id || null,
        document_id: documentId || null
      });
      setNotes(prev => [savedNote, ...prev]);
      setIsModalOpen(false);
      setTopic('');
      setInstructions('');
      navigate('/notes/' + savedNote.id);
    } catch (err) {
      console.error("Failed to generate note", err);
      if (err.response?.status === 401) {
        setErrorMsg("Your session has expired. Please log in again.");
      } else if (err.response?.status === 404) {
        setErrorMsg("Document not found. It may have been deleted.");
      } else if (err.response?.status === 429) {
        setErrorMsg("AI service rate limit exceeded. Please wait a moment and try again.");
      } else if (err.response?.data?.detail) {
        // Handle detail string or JSON structure
        const detail = err.response.data.detail;
        setErrorMsg(typeof detail === 'string' ? detail : (detail.message || "An error occurred."));
      } else {
        setErrorMsg("Failed to generate notes. The AI service may be temporarily unavailable.");
      }
    } finally {
      setIsGenerating(false);
    }
  };


  const toggleFavorite = async (note, e) => {
    e.stopPropagation();
    try {
      const updated = await noteService.toggleFavorite(note.id);
      setNotes(prev => prev.map(n => n.id === note.id ? updated : n));
    } catch (err) {
      console.error(err);
    }
  };

  const confirmDelete = (noteId, e) => {
    e.stopPropagation();
    setNoteToDelete(noteId);
    setIsDeleteModalOpen(true);
  };

  const executeDelete = async () => {
    if (!noteToDelete) return;
    try {
      await noteService.deleteNote(noteToDelete);
      setNotes(prev => prev.filter(n => n.id !== noteToDelete));
    } catch (err) {
      console.error(err);
      alert("Failed to delete note.");
    } finally {
      setIsDeleteModalOpen(false);
      setNoteToDelete(null);
    }
  };

  const cancelDelete = () => {
    setIsDeleteModalOpen(false);
    setNoteToDelete(null);
  };

  const filteredAndSortedNotes = [...(notes || [])]
    .filter(note => {
      if (filterDocumentId && note.document_id !== filterDocumentId) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'newest') return new Date(b.created_at) - new Date(a.created_at);
      if (sortBy === 'oldest') return new Date(a.created_at) - new Date(b.created_at);
      if (sortBy === 'a-z') return a.title.localeCompare(b.title);
      if (sortBy === 'edited') return new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at);
      return 0;
    });

  return (
    <div className="w-full max-w-7xl mx-auto h-[calc(100vh-120px)] flex gap-6 min-h-0">

      {/* LEFT SIDEBAR: Folders & Tags */}
      <div className="w-64 flex flex-col h-full bg-white border border-gray-200 rounded-2xl p-4 shrink-0 overflow-y-auto hidden md:flex shadow-md">
        <h2 className="text-sm font-bold text-gray-600 uppercase tracking-wider mb-4">Library</h2>

        <div className="space-y-1 mb-6">
          <button
            onClick={() => { setSelectedFolder(null); setFilterFavorite(false); }}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${!selectedFolder && !filterFavorite ? 'bg-blue-500/20 text-blue-400' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <FiFileText /> All Notes
          </button>
          <button
            onClick={() => { setSelectedFolder(null); setFilterFavorite(true); }}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${filterFavorite ? 'bg-yellow-500/20 text-yellow-400' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <FiStar /> Favorites
          </button>
        </div>

        <div className="flex justify-between items-center mb-2">
          <h2 className="text-sm font-bold text-gray-600 uppercase tracking-wider">Folders</h2>
          <button className="text-gray-600 hover:text-gray-900 transition-colors"><FiPlus /></button>
        </div>

        <div className="space-y-1 mb-6">
          {(folders || []).map(folder => (
            <button
              key={folder.id}
              onClick={() => { setSelectedFolder(folder); setFilterFavorite(false); }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${selectedFolder?.id === folder.id ? 'bg-blue-500/20 text-blue-400' : 'text-gray-700 hover:bg-gray-50'}`}
            >
              <FiFolder /> {folder.name}
            </button>
          ))}
          {(folders || []).length === 0 && <p className="text-xs text-gray-600 px-3 py-1">No folders yet</p>}
        </div>
      </div>

      {/* MIDDLE COLUMN: Note List */}
      <div className="flex-1 flex flex-col h-full bg-gray-100 border border-gray-200 rounded-2xl p-0 overflow-hidden min-w-0 shadow-md">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex-1 flex flex-col sm:flex-row gap-3 w-full">
            <div className="relative w-full md:max-w-md shrink-0">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600" />
              <input
                type="text"
                placeholder="Search notes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl py-2 pl-10 pr-4 text-sm text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>
            
            <div className="flex gap-2 w-full sm:w-auto">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-white border border-gray-200 text-gray-700 text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block p-2 transition-colors cursor-pointer w-full sm:w-auto"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="a-z">Title (A-Z)</option>
                <option value="edited">Recently Edited</option>
              </select>
              
              <select
                value={filterDocumentId}
                onChange={(e) => setFilterDocumentId(e.target.value)}
                className="bg-white border border-gray-200 text-gray-700 text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block p-2 transition-colors cursor-pointer w-full sm:w-auto"
                title="Filter by Document"
              >
                <option value="">All Documents</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>{doc.filename}</option>
                ))}
              </select>
            </div>
          </div>
          
          <button
            onClick={() => setIsModalOpen(true)}
            className="w-full md:w-auto shrink-0 flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold transition-colors shadow-sm shadow-blue-900/20 whitespace-nowrap"
          >
            <FiPlus /> Create New Notes
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6 items-start content-start bg-white/30">
          {filteredAndSortedNotes.map(note => (
            <div
              key={note.id}
              onClick={() => navigate('/notes/' + note.id)}
              className="p-5 flex flex-col h-auto min-h-[16rem] rounded-2xl border cursor-pointer transition-all text-left bg-white border-gray-200/60 hover:border-blue-300 hover:bg-gray-50/50 hover:-translate-y-1 hover:shadow-md shadow-sm group relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-500/0 group-hover:bg-blue-500 transition-all duration-300 opacity-0 group-hover:opacity-100" />
              <div className="flex justify-between items-start mb-2 gap-3">
                <h3 className="font-bold text-gray-900 text-base line-clamp-2 leading-snug flex-1">{note.title}</h3>
                <button 
                  onClick={(e) => { e.stopPropagation(); toggleFavorite(note, e); }} 
                  className="text-gray-400 hover:text-yellow-400 transition-colors shrink-0 p-1.5 bg-transparent rounded-full hover:bg-gray-100"
                >
                  <FiStar className={note.is_favorite ? "fill-yellow-400 text-yellow-400" : ""} size={16} />
                </button>
              </div>
              
              <div className="flex flex-wrap items-center gap-2 mb-3">
                 <span className="bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-md text-blue-600 text-xs font-bold tracking-wider">{note.note_type}</span>
                 {note.document_id && <span className="bg-gray-100 border border-gray-200 px-2 py-0.5 rounded-md text-gray-600 text-[10px] uppercase font-bold tracking-wider">Has Source</span>}
              </div>
              
              <div className="text-sm text-gray-600 line-clamp-3 mb-3 prose prose-sm flex-1 leading-relaxed" dangerouslySetInnerHTML={{ __html: note.content || "Empty note" }}></div>
              
              <div className="flex justify-between items-center text-[11px] font-medium text-gray-500 pt-3 border-t border-gray-100 mt-auto">
                <span className="flex items-center gap-1.5"><FiClock size={12} /> {new Date(note.created_at).toLocaleDateString()}</span>
                <button 
                  onClick={(e) => confirmDelete(note.id, e)} 
                  className="text-gray-400 hover:text-red-500 flex items-center gap-1.5 transition-colors px-2 py-1 hover:bg-red-50 rounded"
                >
                  <FiTrash2 size={14} /> <span>Delete</span>
                </button>
              </div>
            </div>
          ))}
          {filteredAndSortedNotes.length === 0 && (
            <div className="p-12 flex flex-col items-center justify-center text-center text-gray-600 col-span-full mt-10 bg-white rounded-2xl border border-gray-200 border-dashed min-h-[300px]">
              <div className="w-16 h-16 bg-blue-50 text-blue-400 rounded-full flex items-center justify-center text-2xl mb-4">
                <FiFileText />
              </div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">No notes found</h3>
              <p className="text-sm text-gray-500 max-w-sm">
                {notes.length === 0 
                  ? "You haven't created any study notes yet. Generate your first detailed study guide to get started."
                  : "We couldn't find any notes matching your current filters and search query."}
              </p>
              {notes.length === 0 && (
                <button onClick={() => setIsModalOpen(true)} className="mt-6 px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-500 transition-colors">
                  Create First Note
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* CREATE NOTES MODAL */}
      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="bg-white border border-gray-200 shadow-md rounded-2xl w-full max-w-lg overflow-hidden flex flex-col"
            >
              <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-100">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <FiBookOpen className="text-blue-400" /> Generate Notes
                </h3>
                <button onClick={() => !isGenerating && setIsModalOpen(false)} className="text-gray-600 hover:text-gray-900 transition-colors">
                  <FiX className="text-xl" />
                </button>
              </div>

              <div className="p-6">
                {errorMsg && (
                  <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3">
                    <div className="text-red-400 mt-0.5">⚠️</div>
                    <p className="text-sm text-red-200">{errorMsg}</p>
                  </div>
                )}

                <form onSubmit={handleGenerate} className="space-y-5">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Select Document</label>
                    <select
                      value={documentId}
                      onChange={(e) => setDocumentId(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
                      disabled={isDocumentsLoading || documents.length === 0}
                    >
                      {isDocumentsLoading ? (
                        <option value="">-- Loading documents... --</option>
                      ) : documents.length === 0 ? (
                        <option value="">-- No uploaded documents found. Upload a document from My Documents first. --</option>
                      ) : (
                        <>
                          <option value="">-- Please Select a Document --</option>
                          {(documents || []).map(doc => {
                            let label = doc.filename;
                            if (doc.upload_status === 'failed') label += " — Processing failed";
                            else if (doc.upload_status !== 'completed' && doc.upload_status !== 'processed') label += " — Processing...";
                            return <option key={doc.id} value={doc.id}>{label}</option>;
                          })}
                        </>
                      )}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Topic (Required)</label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g. Optical Fiber Communication"
                      required
                      className="w-full px-4 py-2.5 rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Optional Instructions</label>
                    <textarea
                      value={instructions}
                      onChange={(e) => setInstructions(e.target.value)}
                      placeholder="e.g. Focus specifically on the mathematical derivations."
                      rows="2"
                      className="w-full px-4 py-2.5 rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-3 text-gray-700">Detail Level</label>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { id: 'comprehensive', label: 'Comprehensive' },
                        { id: 'revision', label: 'Revision Summary' }
                      ].map(type => (
                        <label
                          key={type.id}
                          className={`flex items-center justify-center p-2.5 rounded-xl border cursor-pointer transition-all text-sm font-semibold ${noteType === type.id
                              ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                              : 'border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-700'
                            }`}
                        >
                          <input
                            type="radio"
                            name="noteType"
                            value={type.id}
                            checked={noteType === type.id}
                            onChange={() => setNoteType(type.id)}
                            className="hidden"
                          />
                          {type.label}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="pt-4 border-t border-gray-200 flex justify-end gap-3">
                    <Button variant="secondary" type="button" onClick={() => setIsModalOpen(false)} disabled={isGenerating}>Cancel</Button>
                    <Button
                      type="submit"
                      disabled={isGenerating || !topic.trim() || !documentId}
                      variant="primary"
                      className="px-6"
                      icon={isGenerating ? <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" /> : <FiBookOpen />}
                    >
                      {isGenerating ? 'Generating...' : 'Generate Notes'}
                    </Button>
                  </div>
                </form>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* DELETE CONFIRMATION MODAL */}
      <AnimatePresence>
        {isDeleteModalOpen && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={cancelDelete}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border border-gray-200 shadow-md rounded-2xl w-full max-w-sm overflow-hidden flex flex-col"
            >
              <div className="p-6 text-center">
                <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
                  <FiTrash2 />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Delete Note?</h3>
                <p className="text-sm text-gray-500 mb-6">
                  Are you sure you want to delete this note? This action cannot be undone.
                </p>
                <div className="flex gap-3 justify-center">
                  <Button variant="secondary" onClick={cancelDelete} className="flex-1">
                    Cancel
                  </Button>
                  <Button variant="danger" onClick={executeDelete} className="flex-1 bg-red-600 hover:bg-red-500 text-white">
                    Delete
                  </Button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default Notes;
