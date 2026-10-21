import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiZoomIn, FiZoomOut, FiSearch, FiBookmark, FiEdit3, FiMaximize, FiList, FiFileText, FiMessageSquare, FiActivity, FiArrowLeft } from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import DocumentAssistantPanel from '../components/workspace/DocumentAssistantPanel';
import { workspaceService } from '../services/workspaceService';

const Workspace = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewState, setViewState] = useState('hub'); // 'hub' or 'viewer'
  const [selectedDoc, setSelectedDoc] = useState(null);

  // Viewer states
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    loadWorkspace();
  }, []);

  const loadWorkspace = async () => {
    try {
      setLoading(true);
      const res = await workspaceService.getWorkspaceDashboard();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openDocument = (doc) => {
    setSelectedDoc(doc);
    setViewState('viewer');
  };

  const closeViewer = () => {
    setViewState('hub');
    setSelectedDoc(null);
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-600">Loading Workspace...</div>;
  }

  if (viewState === 'viewer' && selectedDoc) {
    return (
      <div className="h-[calc(100vh-6rem)] -mt-4 -mb-8 -mx-4 md:-mx-8 flex flex-col overflow-hidden bg-[var(--color-bg-base)]">
        {/* Top Toolbar */}
        <div className="h-14 border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] flex items-center justify-between px-4 shrink-0 z-10">
          <div className="flex items-center gap-4">
            <Button variant="ghost" className="p-2 text-gray-600 hover:text-gray-900" onClick={closeViewer}>
              <FiArrowLeft />
            </Button>
            <h2 className="font-semibold text-gray-900 tracking-tight truncate max-w-xs">{selectedDoc.filename}</h2>
            <Badge variant="neutral">Page {pageNumber} of {numPages || '?'}</Badge>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-gray-50 rounded-lg p-1 border border-gray-200 mr-2">
              <button onClick={() => setScale(s => Math.max(0.5, s - 0.1))} className="p-1.5 text-gray-600 hover:text-gray-900 transition-colors rounded hover:bg-gray-100">
                <FiZoomOut />
              </button>
              <span className="text-xs font-medium w-12 text-center text-gray-700">{Math.round(scale * 100)}%</span>
              <button onClick={() => setScale(s => Math.min(2.5, s + 0.1))} className="p-1.5 text-gray-600 hover:text-gray-900 transition-colors rounded hover:bg-gray-100">
                <FiZoomIn />
              </button>
            </div>
          </div>
        </div>

        {/* Main Split Content */}
        <div className="flex-1 flex overflow-hidden relative">
          <div className="flex-1 overflow-y-auto bg-gray-50 flex justify-center p-4 hide-scrollbar">
            <div className="bg-white rounded shadow-md relative transition-transform origin-top" style={{ width: '800px', height: '1100px', transform: `scale(${scale})` }}>
              <div className="absolute inset-0 flex items-center justify-center flex-col text-gray-600">
                <p className="text-lg font-bold text-gray-700 mb-2">PDF Viewer rendered here</p>
                <p className="text-sm">{selectedDoc.filename}</p>
              </div>
            </div>
          </div>

          <div className="w-[450px] border-l border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] flex flex-col shrink-0">
            <DocumentAssistantPanel documentContext={{ page: pageNumber, selectedText: "" }} />
          </div>
        </div>
      </div>
    );
  }

  // Hub View
  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Workspace Hub</h1>
        <p className="text-[var(--color-text-muted)]">Your central command for all active study materials and AI sessions.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Recent & Pinned Docs */}
        <div className="lg:col-span-2 space-y-8">
          
          <section>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><FiBookmark className="text-emerald-500" /> Pinned Documents</h3>
            {data?.pinned_files?.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.pinned_files.map(doc => (
                  <Card hover={true} key={doc.id} onClick={() => openDocument(doc)} className="cursor-pointer border-emerald-500/20 bg-emerald-900/10 hover:bg-emerald-900/20">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                        <FiFileText />
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-bold text-gray-900 truncate text-sm">{doc.filename}</h4>
                        <p className="text-xs text-gray-600 truncate">Pinned {new Date(doc.pinned_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-gray-100 rounded-xl border border-gray-200 text-center text-gray-600 text-sm">
                No pinned documents yet.
              </div>
            )}
          </section>

          <section>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><FiFileText className="text-blue-500" /> Recent Uploads</h3>
            {data?.recent_uploads?.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.recent_uploads.map(doc => (
                  <Card hover={true} key={doc.id} onClick={() => openDocument(doc)} className="cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gray-50 flex items-center justify-center text-blue-400 shrink-0">
                        <FiFileText />
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-bold text-gray-900 truncate text-sm">{doc.filename}</h4>
                        <p className="text-xs text-gray-600 truncate">{Math.round(doc.file_size/1024)} KB • {new Date(doc.last_opened_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-gray-100 rounded-xl border border-gray-200 text-center text-gray-600 text-sm">
                No recent uploads.
              </div>
            )}
          </section>

        </div>

        {/* Right Column: Chats & Activity */}
        <div className="space-y-8">
          
          <section>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><FiMessageSquare className="text-purple-500" /> Recent AI Chats</h3>
            {data?.recent_chats?.length > 0 ? (
              <div className="space-y-3">
                {data.recent_chats.map(chat => (
                  <Card hover={true} key={chat.id} onClick={() => window.location.href='/tutor'} className="cursor-pointer p-4">
                    <h4 className="font-bold text-sm text-gray-900 mb-1 truncate">{chat.title || "Untitled Session"}</h4>
                    <p className="text-xs text-gray-600 truncate">{new Date(chat.updated_at).toLocaleString()}</p>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-gray-100 rounded-xl border border-gray-200 text-center text-gray-600 text-sm">
                No recent chats.
              </div>
            )}
          </section>

          <section>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><FiActivity className="text-orange-500" /> Activity Feed</h3>
            {data?.activities?.length > 0 ? (
              <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
                {data.activities.map((act, i) => (
                  <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-gray-50 text-gray-600 group-[.is-active]:text-emerald-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                      <FiActivity className="text-sm" />
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-gray-50 p-4 rounded border border-gray-200">
                      <p className="text-sm text-gray-900 font-medium">{act.description}</p>
                      <time className="text-xs text-gray-600 mt-1 block">{new Date(act.created_at).toLocaleString()}</time>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-gray-100 rounded-xl border border-gray-200 text-center text-gray-600 text-sm">
                No recent activity.
              </div>
            )}
          </section>

        </div>
      </div>
    </div>
  );
};

export default Workspace;
