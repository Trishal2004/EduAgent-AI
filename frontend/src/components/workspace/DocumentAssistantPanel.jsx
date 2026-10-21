import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiSend, FiCpu, FiBookOpen, FiSearch, FiCheckCircle, 
  FiZap, FiLayers, FiFileText, FiTarget, FiStar
} from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import Card from '../ui/Card';

const AIThinkingProcess = () => {
  const [step, setStep] = useState(0);
  const steps = [
    { icon: <FiSearch />, text: 'Understanding Question...' },
    { icon: <FiBookOpen />, text: 'Searching Documents...' },
    { icon: <FiLayers />, text: 'Retrieving Context...' },
    { icon: <FiCheckCircle />, text: 'Checking Evidence...' },
    { icon: <FiCpu />, text: 'Generating Answer...' }
  ];

  useEffect(() => {
    if (step < steps.length) {
      const timer = setTimeout(() => setStep(s => s + 1), 700);
      return () => clearTimeout(timer);
    }
  }, [step]);

  return (
    <div className="space-y-3 mb-4 p-4 rounded-xl bg-gray-100 border border-gray-200">
      {steps.map((s, idx) => (
        <motion.div 
          key={idx}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: idx <= step ? (idx === step ? 1 : 0.5) : 0, height: idx <= step ? 'auto' : 0 }}
          className={`flex items-center gap-3 text-sm font-medium ${idx === step ? 'text-blue-400' : 'text-gray-600'}`}
        >
          {idx === step ? <FiCpu className="animate-pulse text-lg" /> : <span className="text-lg">{s.icon}</span>}
          <span>{s.text}</span>
        </motion.div>
      ))}
    </div>
  );
};

const DocumentAssistantPanel = ({ documentContext }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'ai',
      content: 'I am reading "Operating Systems - Chapter 5". What would you like to know about this document?',
      structured: null
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endOfMessagesRef = useRef(null);
  const navigate = useNavigate();
  
  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleQuickAction = (action) => {
    setInput(action);
    // Auto-send could be placed here if desired
  };

  const handleSend = (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate Agentic AI process
    setTimeout(() => {
      const aiMessage = {
        id: Date.now() + 1,
        role: 'ai',
        content: null,
        structured: {
          topic: 'Deadlock Context Analysis',
          definition: documentContext.selectedText,
          easy: 'A deadlock is like a traffic jam where every car is blocking another car, so nobody can move.',
          example: 'Transaction A waits for Table 2, while Transaction B waits for Table 1.',
          diagram: '[Diagram: Circular Wait Concept]',
          advantages: 'N/A',
          disadvantages: 'System halts, requiring manual intervention or process termination.',
          applications: 'Database transactions, Multithreading, OS Resource Allocation.',
          examTips: 'Always mention the 4 necessary conditions (Coffman conditions).',
          interview: 'How do you prevent a deadlock in a multithreaded application?',
          related: ['Starvation', 'Banker\'s Algorithm', 'Semaphores'],
          source: 'Operating Systems Chapter 5.pdf',
          page: documentContext.page,
          confidence: '99%'
        }
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 4000); 
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[var(--color-bg-card)]">
      {/* Panel Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-100/80 flex items-center gap-3 shrink-0">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold shadow-sm">E</div>
        <div>
          <h3 className="font-bold text-gray-900 text-sm leading-tight">AI Workspace Assistant</h3>
          <p className="text-xs text-blue-400">Context: Page {documentContext.page}</p>
        </div>
      </div>

      {/* Context Actions if text selected */}
      {documentContext?.selectedText && (
        <div className="px-4 pt-4 pb-2 border-b border-gray-200/50 bg-blue-900/10 shrink-0">
          <p className="text-xs font-bold text-blue-400 mb-2 flex items-center gap-1"><FiTarget /> Selected Text Actions</p>
          <div className="flex flex-wrap gap-2">
            {['Explain highlighted text', 'Summarize selected text', 'Explain in Beginner Mode'].map((action, i) => (
              <button 
                key={i} 
                onClick={() => handleQuickAction(action)}
                className="px-3 py-1.5 rounded bg-gray-50 border border-gray-200 text-xs text-gray-700 hover:text-gray-900 hover:border-blue-500 hover:bg-gray-100 transition-colors"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 hide-scrollbar relative">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            
            {msg.role === 'user' ? (
              <div className="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-blue-600 text-white shadow-md max-w-[85%]">
                <p className="text-sm leading-relaxed">{msg.content}</p>
              </div>
            ) : (
              <div className="w-full">
                {msg.content && (
                  <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-gray-50 border border-gray-200 text-gray-800 max-w-[85%]">
                    <p className="text-sm">{msg.content}</p>
                  </div>
                )}
                
                {msg.structured && (
                  <div className="space-y-4 bg-gray-50/40 border border-gray-200 p-5 rounded-2xl rounded-tl-sm w-full">
                    {/* Header */}
                    <div>
                      <h4 className="text-lg font-bold text-gray-900 mb-1">{msg.structured.topic}</h4>
                      <Badge variant="success" className="text-xs">Confidence: {msg.structured.confidence}</Badge>
                    </div>

                    {/* Content Blocks */}
                    <div className="space-y-3">
                      <div className="bg-gray-50 p-3 rounded-lg border border-gray-200/50">
                        <p className="text-xs font-bold text-gray-600 mb-1 uppercase tracking-wider">Definition</p>
                        <p className="text-sm text-gray-800 italic">"{msg.structured.definition}"</p>
                      </div>
                      
                      <div className="bg-blue-900/20 p-3 rounded-lg border border-blue-500/20">
                        <p className="text-xs font-bold text-blue-400 mb-1 flex items-center gap-1"><FiStar /> Easy Explanation</p>
                        <p className="text-sm text-gray-700">{msg.structured.easy}</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-emerald-900/20 p-3 rounded-lg border border-emerald-500/20">
                          <p className="text-xs font-bold text-emerald-400 mb-1">Exam Tips</p>
                          <p className="text-xs text-gray-700">{msg.structured.examTips}</p>
                        </div>
                        <div className="bg-orange-900/20 p-3 rounded-lg border border-orange-500/20">
                          <p className="text-xs font-bold text-orange-400 mb-1">Interview Prep</p>
                          <p className="text-xs text-gray-700">{msg.structured.interview}</p>
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 p-3 rounded-lg border border-gray-200/50 flex justify-between items-center">
                        <div>
                          <p className="text-xs text-gray-600">Source: <span className="text-gray-800">{msg.structured.source}</span></p>
                        </div>
                        <Badge variant="neutral">Page {msg.structured.page}</Badge>
                      </div>
                    </div>

                    {/* Generation Actions */}
                    <div className="pt-3 border-t border-gray-200/50">
                      <p className="text-xs font-bold text-gray-600 mb-2">Generate from this context:</p>
                      <div className="grid grid-cols-2 gap-2">
                        {['Generate Notes', 'Generate Flashcards', 'Generate Quiz', 'Mind Map'].map((btn, i) => (
                          <button 
                            key={i} 
                            onClick={() => {
                              if (btn === 'Generate Flashcards') {
                                navigate(`/app/flashcards?doc=${documentContext?.id || ''}`);
                              }
                            }}
                            className="py-1.5 px-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded text-xs text-gray-700 font-medium transition-colors flex items-center justify-center gap-1"
                          >
                            <FiZap className="text-yellow-400" /> {btn}
                          </button>
                        ))}
                      </div>
                    </div>

                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Typing / Thinking Indicator */}
        {isTyping && (
          <div className="w-full">
            <AIThinkingProcess />
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-gray-200 bg-white shrink-0">
        {/* Helper Modes */}
        <div className="flex gap-2 mb-3 overflow-x-auto hide-scrollbar pb-1">
          {['Explain in Exam Mode', 'Explain in Research Mode'].map((mode, i) => (
            <button 
              key={i} 
              onClick={() => handleQuickAction(mode)}
              className="whitespace-nowrap px-3 py-1 rounded-full bg-gray-50 border border-gray-200 text-[10px] uppercase tracking-wider font-bold text-gray-600 hover:text-gray-900 transition-colors"
            >
              {mode}
            </button>
          ))}
        </div>
        
        <form onSubmit={handleSend} className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this page..."
            className="w-full pl-4 pr-12 py-3 rounded-xl bg-gray-50 border border-gray-200 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isTyping}
            className={`absolute right-2 p-2 rounded-lg transition-all ${
              input.trim() && !isTyping 
                ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-md' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            <FiSend />
          </button>
        </form>
      </div>
    </div>
  );
};

export default DocumentAssistantPanel;
