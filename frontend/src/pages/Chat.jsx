import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiSend, FiPaperclip, FiMic, FiUser, FiInfo, FiExternalLink,
  FiSearch, FiBookOpen, FiCheckCircle, FiCpu, FiPlus, FiMessageSquare, FiTrash2, FiLoader, FiSquare,
  FiCopy, FiRefreshCw, FiMessageCircle, FiList, FiTrendingUp, FiFileText, FiLayers, FiHelpCircle, FiAlignLeft,
  FiVolume2, FiVolumeX, FiThumbsUp, FiThumbsDown, FiEdit2, FiCheck, FiX, FiEdit3
} from 'react-icons/fi';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { tutorService } from '../services/tutorService';
import { documentService } from '../services/documentService';
import { quizService } from '../services/quizService';
import { noteService } from '../services/noteService';
import { flashcardService } from '../services/flashcardService';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';

const AIThinkingProcess = () => {
  const [step, setStep] = useState(0);
  const steps = [
    { icon: <FiSearch />, text: 'Searching Knowledge Base...' },
    { icon: <FiBookOpen />, text: 'Reading Relevant Context...' },
    { icon: <FiCheckCircle />, text: 'Synthesizing Evidence...' },
    { icon: <FiCpu />, text: 'Generating Final Answer...' }
  ];

  useEffect(() => {
    if (step < steps.length) {
      const timer = setTimeout(() => setStep(s => s + 1), 800);
      return () => clearTimeout(timer);
    }
  }, [step]);

  return (
    <div className="space-y-2 mb-4">
      {steps.map((s, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: idx <= step ? (idx === step ? 1 : 0.5) : 0, height: idx <= step ? 'auto' : 0 }}
          className={`flex items-center gap-2 text-sm ${idx === step ? 'text-blue-400' : 'text-gray-600'}`}
        >
          {idx === step ? <FiCpu className="animate-pulse" /> : s.icon}
          <span>{s.text}</span>
        </motion.div>
      ))}
    </div>
  );
};

const Chat = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Search & Rename
  const [searchQuery, setSearchQuery] = useState('');
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editSessionTitle, setEditSessionTitle] = useState('');

  // User Message Edit
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editMessageText, setEditMessageText] = useState('');

  // AI Feedback
  const [feedbackGiven, setFeedbackGiven] = useState({}); // { msgId: 'up' | 'down' }

  // Document Context
  const searchParams = new URLSearchParams(window.location.search);
  const [activeDocumentId, setActiveDocumentId] = useState(searchParams.get('doc'));
  const [uploadState, setUploadState] = useState('idle'); // idle, uploading, processing, success, error
  const [attachedImage, setAttachedImage] = useState(null);

  const endOfMessagesRef = useRef(null);
  const abortControllerRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Voice States
  const [isRecording, setIsRecording] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Load History
  const loadHistory = async () => {
    try {
      const hist = await tutorService.getHistory();
      setSessions(hist);
    } catch (err) {
      console.error('Failed to load history', err);
    }
  };

  useEffect(() => {
    loadHistory().finally(() => setLoading(false));
    documentService.getDocuments().then(docs => setDocuments(docs.filter(d => d.embedding_status === 'completed')));
  }, []);

  // Load Session Messages
  useEffect(() => {
    if (currentSessionId) {
      tutorService.getSession(currentSessionId).then(data => {
        setMessages(data.messages || []);
        if (data.document_id) {
          setActiveDocumentId(data.document_id);
        } else {
          setActiveDocumentId(null);
        }
      });
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    // Cleanup speech synthesis on unmount
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      import('react-hot-toast').then(mod => mod.toast.error("Speech recognition is not supported in this browser."));
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        import('react-hot-toast').then(mod => mod.toast.success("Listening..."));
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setInput(prev => prev ? prev + ' ' + finalTranscript : finalTranscript);
        }
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        if (event.error === 'not-allowed') {
          import('react-hot-toast').then(mod => mod.toast.error("Microphone access denied."));
        } else {
          import('react-hot-toast').then(mod => mod.toast.error(`Speech recognition error: ${event.error}`));
        }
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.start();
      recognitionRef.current = recognition;
    } catch (err) {
      console.error(err);
      import('react-hot-toast').then(mod => mod.toast.error("Failed to start speech recognition."));
    }
  };

  const toggleSpeech = (msg) => {
    if (!window.speechSynthesis) {
      import('react-hot-toast').then(mod => mod.toast.error("Text-to-speech is not supported in this browser."));
      return;
    }

    if (speakingMessageId === msg.id) {
      // Stop speaking
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
      return;
    }

    // Stop current speech before starting new one
    window.speechSynthesis.cancel();

    // Extract text from markdown (basic strip for TTS)
    let textToSpeak = msg.content || '';
    textToSpeak = textToSpeak.replace(/[#*`_]/g, ''); // strip basic markdown

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    setSpeakingMessageId(msg.id);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async (e, overrideQuestion = null) => {
    e?.preventDefault();
    const question = overrideQuestion || input.trim();
    if (!question || isTyping) return;

    const payloadImage = attachedImage;
    if (!overrideQuestion) {
      setInput('');
      setAttachedImage(null);
    }

    // Optimistic UI for user message
    const tempId = Date.now();
    const tempAiMessageId = tempId + 1;

    setMessages(prev => [
      ...prev,
      { id: tempId, role: 'user', content: question, created_at: new Date().toISOString() },
      { id: tempAiMessageId, role: 'ai', content: '', isStreaming: true }
    ]);
    setIsTyping(true);

    // Initialize AbortController
    abortControllerRef.current = new AbortController();

    let fullText = "";
    const onChunk = (chunk) => {
      fullText += chunk;
      setMessages(prev => prev.map(m => m.id === tempAiMessageId ? { ...m, content: fullText } : m));
    };

    try {
      const response = await tutorService.chat(currentSessionId, question, activeDocumentId, payloadImage, abortControllerRef.current.signal, onChunk);

      if (!currentSessionId && response.session_id) {
        setCurrentSessionId(response.session_id);
        await loadHistory();
      }

      // Always replace temp user message and add final AI message immediately
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== tempId && m.id !== tempAiMessageId);
        return [...filtered, response.user_message, response.ai_message];
      });
    } catch (err) {
      if (err.name === 'CanceledError' || err.message === 'canceled') {
        console.log('Generation stopped by user.');
        // Keep partial response on stop
        setMessages(prev => prev.map(m => m.id === tempAiMessageId ? { ...m, isStreaming: false } : m));
        return;
      }
      console.error('Chat error:', err);
      // Clean up the temp messages on error so they can retry
      setMessages(prev => prev.filter(m => m.id !== tempId && m.id !== tempAiMessageId));

      const errorMsg = err.response?.data?.detail || err.message || 'Failed to communicate with AI Tutor';
      import('react-hot-toast').then(mod => {
        mod.toast.error(errorMsg);
      });
    } finally {
      setIsTyping(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleNewChat = async () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  const handleActionClick = (action, msg) => {
    if (action.action === 'copy') {
      let textToCopy = msg.content || '';
      navigator.clipboard.writeText(textToCopy);
      import('react-hot-toast').then(mod => mod.toast.success('Copied to clipboard'));
    } else if (action.action === 'export_md' || action.action === 'export_pdf') {
      let md = `# EDUAGENT AI\n## Study Guide\n\n`;
      if (msg.content) md += `${msg.content}\n\n`;

      if (action.action === 'export_md') {
        const blob = new Blob([md], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Study_Guide_Export.md`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        // Export PDF
        const element = document.createElement('div');
        element.style.padding = '20px';
        element.style.fontFamily = 'Arial, sans-serif';
        element.style.color = '#000';
        element.style.background = '#fff';
        // Basic HTML render
        element.innerHTML = `
          <h1 style="color: #2563eb;">EDUAGENT AI - Study Guide</h1>
          ${msg.content ? `<div style="white-space: pre-wrap;">${msg.content}</div>` : ''}
        `;

        import('html2pdf.js').then(html2pdf => {
          html2pdf.default().from(element).set({
            margin: 10,
            filename: `Study_Guide_Export.pdf`,
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
          }).save();
        });
      }
    } else if (action.action === 'regenerate') {
      handleSend(null, "Please regenerate your previous response.");
    } else if (action.action === 'generate_notes') {
      const topic = "AI Conversation Topic";
      const content = msg.content || "";
      const toastPromise = noteService.generateNote({
        topic: topic,
        note_type: 'general',
        document_id: activeDocumentId || null
      });
      import('react-hot-toast').then(mod => {
        mod.toast.promise(toastPromise, {
          loading: 'Generating Notes...',
          success: 'Notes generated and saved successfully!',
          error: 'Failed to generate notes'
        });
      });
    } else if (action.action === 'generate_flashcards') {
      const topic = "AI Conversation Topic";
      const content = msg.content || "";
      const toastPromise = flashcardService.generateFlashcardsFromTopic(activeDocumentId || null, topic, content, 10);
      import('react-hot-toast').then(mod => {
        mod.toast.promise(toastPromise, {
          loading: 'Generating Flashcards...',
          success: 'Flashcards generated and saved successfully!',
          error: 'Failed to generate flashcards'
        });
      });
    } else if (action.action === 'generate_quiz') {
      const topic = "AI Conversation Topic";
      const content = msg.content || "";
      const toastPromise = quizService.generateQuiz(activeDocumentId || null, 'medium', 5, topic, content);
      import('react-hot-toast').then(mod => {
        mod.toast.promise(toastPromise, {
          loading: 'Generating Quiz...',
          success: 'Quiz generated and saved successfully!',
          error: 'Failed to generate quiz'
        });
      });
    } else if (action.prompt) {
      handleSend(null, action.prompt);
    }
  };

  const aiActions = [
    { label: 'Copy', icon: <FiCopy />, action: 'copy' },
    { label: 'Regenerate', icon: <FiRefreshCw />, action: 'regenerate' },
    { label: 'Explain simpler', icon: <FiInfo />, prompt: 'Explain the previous answer at a beginner level.' },
    { label: 'Give example', icon: <FiList />, prompt: 'Give me a practical example of the previous concept.' },
    { label: 'Go deeper', icon: <FiTrendingUp />, prompt: 'Give me a more detailed technical explanation.' },
    { label: 'Generate Notes', icon: <FiFileText />, action: 'generate_notes' },
    { label: 'Generate Flashcards', icon: <FiLayers />, action: 'generate_flashcards' },
    { label: 'Generate Quiz', icon: <FiHelpCircle />, action: 'generate_quiz' },
    { label: 'Summarize', icon: <FiAlignLeft />, prompt: 'Summarize the key points.' },
    { label: 'Export PDF', icon: <FiBookOpen />, action: 'export_pdf' },
    { label: 'Export MD', icon: <FiFileText />, action: 'export_md' },
  ];



  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const handleDeleteSession = async (id, e) => {
    e.stopPropagation();
    try {
      await tutorService.deleteSession(id);
      if (currentSessionId === id) {
        setCurrentSessionId(null);
        setMessages([]);
      }
      loadHistory();
      import('react-hot-toast').then(mod => mod.toast.success('Chat deleted'));
    } catch (err) {
      console.error('Failed to delete session', err);
    }
  };

  const handleRenameSession = async (id, e) => {
    e.stopPropagation();
    if (!editSessionTitle.trim()) {
      setEditingSessionId(null);
      return;
    }
    try {
      await tutorService.renameSession(id, editSessionTitle);
      setEditingSessionId(null);
      loadHistory();
    } catch (err) {
      console.error('Failed to rename session', err);
      import('react-hot-toast').then(mod => mod.toast.error('Failed to rename chat'));
    }
  };

  const startRename = (session, e) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditSessionTitle(session.title);
  };

  const handleEditMessageSubmit = (msgId) => {
    if (!editMessageText.trim()) {
      setEditingMessageId(null);
      return;
    }
    
    // In a real app we might truncate history, but for simple UX we just resend
    // and let backend handle context (or we can just fire a new message).
    handleSend(null, editMessageText);
    setEditingMessageId(null);
  };

  const filteredSessions = sessions.filter(s => s.title.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type.startsWith('image/')) {
      const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        import('react-hot-toast').then(mod => mod.toast.error("Only JPG, PNG, and WebP images are supported."));
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        import('react-hot-toast').then(mod => mod.toast.error("Image size must be less than 5MB."));
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachedImage(reader.result);
      };
      reader.readAsDataURL(file);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setUploadState('uploading');
    try {
      // 1. Upload document
      const uploadRes = await documentService.uploadDocument(file);

      // 2. Process document (generate embeddings, etc)
      setUploadState('processing');
      await documentService.processDocument(uploadRes.id);

      setUploadState('success');
      setActiveDocumentId(uploadRes.id);
      import('react-hot-toast').then(mod => mod.toast.success('Document ready for questions!'));

      setTimeout(() => setUploadState('idle'), 3000);
    } catch (err) {
      console.error(err);
      setUploadState('error');
      import('react-hot-toast').then(mod => {
        mod.toast.error(err.response?.data?.detail || err.message || 'Failed to process document');
      });
      setTimeout(() => setUploadState('idle'), 3000);
    }

    // Clear input so same file can be selected again
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-6 max-w-7xl mx-auto">

      {/* Sidebar for History */}
      <div className="w-64 flex-shrink-0 flex flex-col p-4 bg-white border border-gray-200 rounded-2xl hidden md:flex shadow-md">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-lg font-medium transition-colors mb-6 shadow-sm"
        >
          <FiPlus /> New Chat
        </button>

        <div className="flex-1 overflow-y-auto space-y-2 hide-scrollbar mt-2">
          {/* Search bar */}
          <div className="relative mb-4">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" size={14} />
            <input 
              type="text" 
              placeholder="Search chats..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-gray-100 border border-gray-200 text-sm text-gray-800 rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>

          <h3 className="text-xs font-bold text-gray-600 uppercase tracking-wider mb-3">Recent Chats</h3>
          {loading ? (
            <div className="flex justify-center p-4"><FiLoader className="animate-spin text-blue-500" /></div>
          ) : filteredSessions.length === 0 ? (
            <p className="text-sm text-gray-600 text-center">No history found.</p>
          ) : (
            filteredSessions.map(session => (
              <div
                key={session.id}
                onClick={() => {
                  if (editingSessionId !== session.id) setCurrentSessionId(session.id);
                }}
                className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${currentSessionId === session.id ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'hover:bg-gray-50 text-gray-700'}`}
              >
                <div className="flex items-center gap-2 truncate flex-1">
                  <FiMessageSquare className="shrink-0" />
                  {editingSessionId === session.id ? (
                    <input
                      type="text"
                      autoFocus
                      value={editSessionTitle}
                      onChange={(e) => setEditSessionTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRenameSession(session.id, e);
                        if (e.key === 'Escape') setEditingSessionId(null);
                      }}
                      onClick={(e) => e.stopPropagation()}
                      onBlur={(e) => handleRenameSession(session.id, e)}
                      className="w-full bg-gray-100 border-none rounded text-sm text-gray-900 px-1 py-0.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  ) : (
                    <span className="text-sm truncate">{session.title}</span>
                  )}
                </div>
                
                {editingSessionId !== session.id && (
                  <div className="opacity-0 group-hover:opacity-100 flex items-center shrink-0">
                    <button
                      onClick={(e) => startRename(session, e)}
                      className="text-gray-600 hover:text-blue-400 transition-all p-1.5"
                      title="Rename"
                    >
                      <FiEdit3 size={14} />
                    </button>
                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      className="text-gray-600 hover:text-red-400 transition-all p-1.5"
                      title="Delete"
                    >
                      <FiTrash2 size={14} />
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="mb-4 flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">AI Tutor</h1>
            {activeDocumentId && <Badge variant="primary" className="bg-blue-500/20 text-blue-400">Document Context Active</Badge>}
          </div>
          <p className="text-[var(--color-text-muted)] text-sm">Ask complex questions. The AI will read your documents and synthesize a complete learning guide.</p>
        </div>

        <Card className="flex-1 flex flex-col p-0 overflow-hidden relative shadow-md" hover={false}>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-8 hide-scrollbar bg-gray-50">
            {messages.length === 0 && !isTyping && (
              <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-6 text-center px-4 max-w-2xl mx-auto">
                <div className="w-16 h-16 bg-blue-500/10 text-blue-500 rounded-full flex items-center justify-center text-3xl">
                  <FiCpu />
                </div>
                <div>
                  <h2 className="font-bold text-xl text-gray-800 mb-2">Hi! I'm your AI Tutor.</h2>
                  <p className="text-gray-500">Ask me anything about your uploaded study materials.</p>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-4">
                  {[
                    "Explain this topic",
                    "Summarize this document",
                    "Give me important exam questions",
                    "Explain this in simple terms"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(null, q)}
                      className="p-3 bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50 rounded-xl text-sm text-gray-700 font-medium transition-all text-left flex items-center gap-2 group"
                    >
                      <span className="text-blue-500 group-hover:scale-110 transition-transform">✨</span>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, index) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-4 max-w-[95%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                  {/* Avatar */}
                  <div className={`w-10 h-10 shrink-0 rounded-xl flex items-center justify-center font-bold text-lg shadow-sm
                    ${msg.role === 'user' ? 'bg-gray-100 text-white' : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'}`}>
                    {msg.role === 'user' ? 'U' : 'E'}
                  </div>

                  {/* Content */}
                  <div className={`flex flex-col gap-2 ${msg.role === 'user' ? 'items-end' : 'items-start'} w-full`}>
                    {msg.role === 'user' ? (
                      <div className="group relative max-w-full">
                        {editingMessageId === msg.id ? (
                          <div className="w-full min-w-[300px] bg-gray-50 border border-gray-300 rounded-xl p-3 shadow-sm">
                            <textarea
                              autoFocus
                              value={editMessageText}
                              onChange={(e) => setEditMessageText(e.target.value)}
                              className="w-full bg-transparent text-gray-900 focus:outline-none resize-none min-h-[60px]"
                            />
                            <div className="flex justify-end gap-2 mt-2">
                              <button onClick={() => setEditingMessageId(null)} className="px-3 py-1.5 text-xs text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
                              <button onClick={() => handleEditMessageSubmit(msg.id)} className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors flex items-center gap-1"><FiSend size={12}/> Resend</button>
                            </div>
                          </div>
                        ) : (
                          <div className="px-5 py-3 rounded-2xl rounded-tr-sm bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.2)] group-hover:pr-12 transition-all relative">
                            {msg.structured_data?.image && (
                              <img src={msg.structured_data.image} alt="User Upload" className="max-w-[250px] max-h-[250px] rounded-lg mb-3 object-contain bg-black/20" />
                            )}
                            <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                            
                            {/* Edit Button overlay */}
                            <button
                              onClick={() => {
                                setEditingMessageId(msg.id);
                                setEditMessageText(msg.content);
                              }}
                              className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 bg-gray-100/80 text-gray-700 hover:text-gray-900 rounded-md opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm"
                              title="Edit message"
                            >
                              <FiEdit2 size={14} />
                            </button>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="w-full">
                        {msg.isStreaming && !msg.content ? (
                          <div className="bg-gray-50 border border-gray-200 p-5 rounded-2xl rounded-tl-sm min-w-[250px] shadow-sm">
                            <AIThinkingProcess />
                            <div className="flex gap-1 mt-4">
                              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
                              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                            </div>
                          </div>
                        ) : (
                          msg.content && (
                            <div className="px-5 py-4 rounded-2xl rounded-tl-sm bg-gray-50 border border-gray-200 text-gray-800 shadow-md prose prose-invert max-w-none prose-pre:p-0 prose-pre:bg-transparent">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                                components={{
                                  code({ node, inline, className, children, ...props }) {
                                    const match = /language-(\w+)/.exec(className || '');
                                    return !inline && match ? (
                                      <div className="relative group overflow-hidden rounded-xl border border-gray-200/50 my-4">
                                        <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200/50">
                                          <span className="text-xs font-mono text-gray-600">{match[1]}</span>
                                          <button
                                            onClick={() => {
                                              navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
                                              import('react-hot-toast').then(mod => mod.toast.success('Code copied!'));
                                            }}
                                            className="text-gray-600 hover:text-gray-900 flex items-center gap-1.5 text-xs transition-colors"
                                          >
                                            <FiCopy size={12} /> Copy
                                          </button>
                                        </div>
                                        <SyntaxHighlighter
                                          {...props}
                                          children={String(children).replace(/\n$/, '')}
                                          style={oneDark}
                                          language={match[1]}
                                          PreTag="div"
                                          customStyle={{ margin: 0, padding: '1rem', background: '#0f172a' }}
                                        />
                                      </div>
                                    ) : (
                                      <code {...props} className={`${className} bg-white px-1.5 py-0.5 rounded text-sm text-blue-300 font-mono before:content-[''] after:content-['']`}>
                                        {children}
                                      </code>
                                    );
                                  }
                                }}
                              >
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          )
                        )}

                        {msg.structured_data?.citations?.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-200 w-full">
                            <h4 className="text-sm font-bold text-gray-600 mb-3 uppercase tracking-wider">Sources & Evidence</h4>
                            <div className="flex flex-col gap-2">
                              {msg.structured_data.citations.map((cite, i) => (
                                <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 border border-gray-200/50 hover:border-blue-500/50 transition-colors cursor-pointer group">
                                  <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg group-hover:bg-blue-500/20"><FiExternalLink /></div>
                                  <div>
                                    <p className="font-medium text-gray-800 text-sm flex flex-wrap items-center gap-2">
                                      📄 {cite.document_name || 'Document'} 
                                      <span className="text-gray-600">— Page {cite.page_number || cite.page || 'N/A'}</span>
                                      {cite.relevance_score && (
                                        <span className="text-xs bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded ml-2">
                                          {Math.round(cite.relevance_score * 100)}% Match
                                        </span>
                                      )}
                                    </p>
                                    <p className="text-xs text-gray-600 mt-1">{cite.section_title || cite.section || 'Unknown Section'}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}



                        {/* Quick AI Actions - Only show on the very last AI message */}
                        {index === messages.length - 1 && (
                          <div className="mt-4 pt-4 border-t border-gray-200/50 flex flex-wrap gap-2 items-center">
                            <div className="flex gap-1 mr-1">
                              <button 
                                onClick={() => {
                                  setFeedbackGiven(prev => ({...prev, [msg.id]: 'up'}));
                                  import('react-hot-toast').then(mod => mod.toast.success('Thanks for the feedback!'));
                                }}
                                className={`p-1.5 rounded-lg border transition-colors ${feedbackGiven[msg.id] === 'up' ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' : 'bg-gray-50 border-gray-200 text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}
                                title="Good Response"
                              >
                                <FiThumbsUp size={14} />
                              </button>
                              <button 
                                onClick={() => {
                                  setFeedbackGiven(prev => ({...prev, [msg.id]: 'down'}));
                                  import('react-hot-toast').then(mod => mod.toast.success('Thanks for the feedback!'));
                                }}
                                className={`p-1.5 rounded-lg border transition-colors ${feedbackGiven[msg.id] === 'down' ? 'bg-red-500/20 border-red-500 text-red-400' : 'bg-gray-50 border-gray-200 text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}
                                title="Bad Response"
                              >
                                <FiThumbsDown size={14} />
                              </button>
                            </div>
                            
                            <button
                              onClick={() => toggleSpeech(msg)}
                              className={`flex items-center gap-1.5 px-3 py-1.5 border rounded-lg text-xs font-medium transition-colors ${speakingMessageId === msg.id ? 'bg-blue-600 border-blue-500 text-white' : 'bg-gray-50 hover:bg-gray-100 border-gray-200 hover:border-gray-300 text-gray-700'}`}
                            >
                              {speakingMessageId === msg.id ? <FiVolumeX /> : <FiVolume2 />}
                              <span>{speakingMessageId === msg.id ? 'Stop' : 'Read'}</span>
                            </button>
                            <div className="h-4 w-px bg-gray-100 mx-1"></div>
                            {aiActions.map((action, i) => (
                              <button
                                key={i}
                                onClick={() => handleActionClick(action, msg)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 rounded-lg text-xs font-medium text-gray-700 transition-colors"
                              >
                                {action.icon}
                                <span>{action.label}</span>
                              </button>
                            ))}
                          </div>
                        )}

                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Remove Old Typing Indicator logic entirely since it's now an inline temp message */}
            <div ref={endOfMessagesRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-gray-200 bg-white relative">

            {attachedImage && (
              <div className="absolute left-4 -top-16 bg-gray-50 p-2 rounded-xl border border-gray-200 shadow-md z-10">
                <img src={attachedImage} alt="Attached" className="h-12 w-12 object-cover rounded-lg" />
                <button onClick={() => setAttachedImage(null)} className="absolute -top-2 -right-2 bg-red-500 rounded-full w-5 h-5 flex items-center justify-center text-white text-xs font-bold hover:bg-red-400">×</button>
              </div>
            )}

            {/* Upload State Indicator */}
            {uploadState !== 'idle' && (
              <div className="flex items-center gap-2 mb-3 px-2 text-sm">
                {uploadState === 'uploading' && <><FiLoader className="animate-spin text-blue-400" /> <span className="text-blue-400">Uploading document...</span></>}
                {uploadState === 'processing' && <><FiCpu className="animate-pulse text-indigo-400" /> <span className="text-indigo-400">Creating embeddings & processing...</span></>}
                {uploadState === 'success' && <><FiCheckCircle className="text-emerald-400" /> <span className="text-emerald-400">Ready!</span></>}
                {uploadState === 'error' && <><FiInfo className="text-red-400" /> <span className="text-red-400">Failed to process document</span></>}
              </div>
            )}
            
            {/* Document Selector */}
            <div className="mb-3 px-2">
              <select
                value={activeDocumentId || ''}
                onChange={(e) => setActiveDocumentId(e.target.value || null)}
                className="w-full sm:w-auto bg-gray-50 border border-gray-200 text-gray-700 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2 transition-colors"
              >
                <option value="">All Documents</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>{doc.filename}</option>
                ))}
              </select>
            </div>
            <form onSubmit={handleSend} className="relative flex items-center group">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                className="hidden"
                accept=".pdf,.txt,.docx,.md,.jpg,.jpeg,.png,.webp"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadState === 'uploading' || uploadState === 'processing'}
                title="Attach Document"
                className={`absolute left-4 p-2 transition-colors ${uploadState !== 'idle' ? 'text-slate-600' : 'text-gray-600 hover:text-blue-400'}`}
              >
                <FiPaperclip className="text-xl" />
              </button>

              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything... EduAgent will analyze your documents."
                rows={1}
                className="w-full pl-14 pr-24 py-4 rounded-xl bg-gray-50 border border-gray-200 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all shadow-inner resize-none overflow-hidden"
                style={{ minHeight: '56px', maxHeight: '150px' }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
                }}
              />

              <div className="absolute right-3 flex items-center gap-2">
                <button
                  type="button"
                  onClick={toggleRecording}
                  title={isRecording ? "Stop Recording" : "Start Voice Typing"}
                  className={`p-2 transition-colors hidden sm:flex items-center justify-center rounded-full ${isRecording ? 'text-red-500 bg-red-500/10 animate-pulse' : 'text-gray-600 hover:text-gray-900'}`}
                >
                  <FiMic className="text-xl" />
                </button>
                {isTyping ? (
                  <button
                    type="button"
                    onClick={handleStop}
                    title="Stop Generation"
                    className="p-2 rounded-lg transition-all bg-red-600/20 text-red-500 border border-red-500/30 hover:bg-red-600 hover:text-gray-900 hover:border-red-600 shadow-[0_0_10px_rgba(239,68,68,0.2)]"
                  >
                    <FiSquare className="text-xl fill-current" />
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={!input.trim()}
                    title="Send Message"
                    className={`p-2 rounded-lg transition-all ${input.trim()
                        ? 'bg-blue-600 text-white hover:bg-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.4)]'
                        : 'bg-gray-50 text-slate-600 border border-gray-200'
                      }`}
                  >
                    <FiSend className="text-xl" />
                  </button>
                )}
              </div>
            </form>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Chat;
