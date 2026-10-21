import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiFolder, FiStar, FiTrash2, FiDownload, FiEdit2, FiCheckCircle, FiFileText, FiSearch } from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { noteService } from '../services/noteService';
import { documentService } from '../services/documentService';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

const NoteDetail = () => {
  const { noteId } = useParams();
  const navigate = useNavigate();
  
  const [note, setNote] = useState(null);
  const [documentName, setDocumentName] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  
  const [headings, setHeadings] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const contentRef = React.useRef(null);

  useEffect(() => {
    const fetchNoteAndDoc = async () => {
      try {
        setLoading(true);
        const data = await noteService.getNote(noteId);
        setNote(data);
        
        if (data.document_id) {
            try {
                const docs = await documentService.getDocuments();
                const matchedDoc = docs.find(d => d.id === data.document_id);
                if (matchedDoc) {
                    setDocumentName(matchedDoc.filename);
                }
            } catch (docErr) {
                console.error("Failed to fetch document filename:", docErr);
            }
        }
      } catch (err) {
        console.error(err);
        setError("Unable to load this note. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchNoteAndDoc();
  }, [noteId]);

  useEffect(() => {
    if (!loading && !isEditing && note?.content && contentRef.current) {
      const h2s = Array.from(contentRef.current.querySelectorAll('h2'));
      setHeadings(h2s.map((h, i) => {
        if (!h.id) h.id = `heading-${i}`;
        return { id: h.id, text: h.innerText };
      }));
    }
  }, [loading, isEditing, note]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery) {
      window.find(searchQuery);
    }
  };

  const handleSaveEdit = async () => {
    try {
      const updated = await noteService.updateNote(note.id, { content: editContent });
      setNote(updated);
      setIsEditing(false);
    } catch (err) {
      console.error(err);
      alert("Failed to save changes.");
    }
  };

  const toggleFavorite = async () => {
    try {
      const updated = await noteService.toggleFavorite(note.id);
      setNote(updated);
    } catch (err) {
      console.error(err);
    }
  };

  const deleteNote = async () => {
    if (!window.confirm("Delete this note? This action cannot be undone.")) return;
    try {
      await noteService.deleteNote(note.id);
      navigate('/notes');
    } catch (err) {
      console.error(err);
      alert("Failed to delete note.");
    }
  };

  const handleDownloadPDF = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto h-64 flex items-center justify-center">
        <div className="text-gray-600 font-medium flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          Loading note...
        </div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="max-w-4xl mx-auto h-64 flex flex-col items-center justify-center text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{error || "Note not found."}</h2>
        <Button variant="primary" onClick={() => navigate('/notes')} className="mt-4" icon={<FiArrowLeft />}>
          Back to Notes
        </Button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto flex gap-6 relative">
      
      {/* Table of Contents Sidebar */}
      {headings.length > 0 && !isEditing && (
        <div className="hidden lg:block w-64 shrink-0">
          <div className="sticky top-6 bg-white border border-gray-200 rounded-2xl p-5 shadow-md">
            <h3 className="font-bold text-gray-900 mb-4 uppercase tracking-wider text-xs">Table of Contents</h3>
            <ul className="space-y-2 text-sm text-gray-600 max-h-[calc(100vh-150px)] overflow-y-auto hide-scrollbar">
              {headings.map((h, i) => (
                <li key={i}>
                  <a href={`#${h.id}`} className="hover:text-blue-600 transition-colors block truncate" title={h.text}>
                    {h.text}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col gap-6 min-w-0">
        <button 
          onClick={() => navigate('/notes')}
          className="self-start flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
        >
          <FiArrowLeft /> Back to Notes
        </button>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-md overflow-hidden relative">
        <div className="p-6 md:p-8 border-b border-gray-200 bg-gray-50/30 flex flex-col md:flex-row md:justify-between md:items-start gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-md text-xs font-bold uppercase tracking-wider border border-blue-500/20">
                {note.note_type}
              </span>
              {note.folder && (
                <span className="text-xs font-medium text-gray-600 flex items-center gap-1.5 bg-gray-50 px-3 py-1 rounded-md border border-gray-200/50">
                  <FiFolder size={14} /> {note.folder.name}
                </span>
              )}
              <span className="text-xs font-medium text-gray-600 flex items-center gap-1.5 bg-gray-50 px-3 py-1 rounded-md border border-gray-200/50">
                <FiClock size={14} /> {new Date(note.created_at).toLocaleDateString()}
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3 leading-tight">{note.title}</h1>
            {note.document_id && (
              <p className="text-sm text-gray-600 flex items-center gap-2">
                <FiFileText size={16} className="text-gray-600" />
                {documentName ? documentName : `Document: ${note.document_id}`}
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2 shrink-0 items-center">
            {!isEditing && (
              <form onSubmit={handleSearch} className="flex items-center bg-white border border-gray-200 rounded-lg px-2 mr-2">
                <FiSearch className="text-gray-400" />
                <input 
                  type="text" 
                  placeholder="Find..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-24 md:w-32 text-sm bg-transparent border-none focus:outline-none focus:ring-0 p-1.5"
                />
              </form>
            )}
            <Button 
              variant="secondary" 
              onClick={toggleFavorite} 
              icon={<FiStar className={note.is_favorite ? "fill-yellow-400 text-yellow-400" : ""} />}
            >
              Favorite
            </Button>
            {isEditing ? (
              <>
                <Button variant="primary" onClick={handleSaveEdit} icon={<FiCheckCircle />}>Save Changes</Button>
                <Button variant="secondary" onClick={() => setIsEditing(false)}>Cancel</Button>
              </>
            ) : (
              <>
                <Button variant="secondary" onClick={() => { setEditContent(note.content); setIsEditing(true); }} icon={<FiEdit2 />}>Edit</Button>
                <Button variant="secondary" onClick={handleDownloadPDF} icon={<FiDownload />}>Export</Button>
                <Button variant="danger" onClick={deleteNote} icon={<FiTrash2 />}>Delete</Button>
              </>
            )}
          </div>
        </div>

        <div className="p-6 md:p-10 lg:p-12 print:p-0">
          {isEditing ? (
            <div className="min-h-[500px] bg-white rounded-lg text-black overflow-hidden">
              <ReactQuill
                theme="snow"
                value={editContent}
                onChange={setEditContent}
                className="h-[500px] pb-10"
                modules={{
                  toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['link', 'clean']
                  ]
                }}
              />
            </div>
          ) : (
            <div
              ref={contentRef}
              className="prose prose-lg max-w-[1000px] mx-auto text-gray-900 prose-headings:text-blue-600 prose-p:leading-[1.8] prose-headings:mt-10 prose-headings:mb-4 prose-a:text-blue-500 prose-table:border-collapse prose-td:border prose-td:border-gray-200 prose-th:border prose-th:border-gray-200 prose-th:bg-gray-50 prose-li:my-1"
              dangerouslySetInnerHTML={{ __html: note.content }}
            />
          )}
        </div>
      </div>
    </div>
    </div>
  );
};

export default NoteDetail;
