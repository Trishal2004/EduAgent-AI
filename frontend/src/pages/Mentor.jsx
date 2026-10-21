import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiSend, FiCpu, FiTarget, FiClock, FiActivity, 
  FiZap, FiAward, FiCheckCircle, FiAlertCircle 
} from 'react-icons/fi';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import { mentorService } from '../services/mentorService';

const Mentor = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    loadDashboard();
    loadChat();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await mentorService.getDashboard();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadChat = async () => {
    try {
      const res = await mentorService.getChatHistory();
      setMessages(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await mentorService.generateInsights();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const msg = input.trim();
    setInput('');
    
    // Optimistic UI
    const tempUserMsg = { id: Date.now().toString(), role: 'user', content: msg };
    setMessages(prev => [...prev, tempUserMsg]);
    setIsTyping(true);

    try {
      const aiReply = await mentorService.sendChatMessage(msg);
      setMessages(prev => [...prev, aiReply]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  if (loading && !data) {
    return <div className="p-8 text-center text-gray-600">Loading Mentor Insights...</div>;
  }

  // Fallback context if generation hasn't run yet
  const todayGoal = data?.active_goals?.[0]?.goal_text || "Set up your goals";
  const weakTopics = data?.weak_topics || [];
  const strongTopics = []; // You could pull from topic mastery in kg in the future
  const examCountdown = data?.active_goals?.[0] ? Math.ceil((new Date(data.active_goals[0].target_date) - new Date()) / (1000 * 60 * 60 * 24)) : 0;
  
  return (
    <div className="h-[calc(100vh-6rem)] -mt-4 -mb-8 -mx-4 md:-mx-8 flex flex-col md:flex-row bg-[var(--color-bg-base)] overflow-hidden">
      
      {/* Left Panel: Mentor Insights & Context */}
      <div className="w-full md:w-96 border-r border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] overflow-y-auto hide-scrollbar p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <FiCpu className="text-blue-500" /> AI Mentor
            </h2>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">Your personalized learning coach.</p>
          </div>
          <button onClick={handleGenerate} className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs font-bold transition-colors">
            Generate Plan
          </button>
        </div>

        {/* Motivational Banner */}
        {examCountdown > 0 && (
          <div className="p-4 bg-gradient-to-br from-blue-900/40 to-indigo-900/40 rounded-xl border border-blue-500/20 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                <FiAward className="text-xl" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-blue-300">Next Deadline</p>
                <p className="text-lg font-bold text-gray-900">{examCountdown} Days Left</p>
              </div>
            </div>
          </div>
        )}

        {/* Active Goals */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-gray-600 uppercase tracking-widest">Active Goals</h3>
          
          <Card hover={false} className="border-l-4 border-l-emerald-500">
            <p className="text-xs text-gray-600 mb-1 flex items-center gap-1"><FiTarget /> Current Focus</p>
            <p className="font-bold text-gray-900 mb-2">{todayGoal}</p>
          </Card>
          
          {data?.today_plan && (
            <Card hover={false}>
              <p className="text-xs text-gray-600 mb-2 flex items-center gap-1"><FiClock /> Today's Plan</p>
              <ul className="text-sm space-y-1 list-disc pl-4 text-gray-700">
                {data.today_plan.content.tasks?.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </Card>
          )}
        </div>

        {/* Topic Analysis */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-gray-600 uppercase tracking-widest flex items-center gap-2">
            <FiActivity /> Topic Analysis
          </h3>
          
          <div className="space-y-3">
            <div>
              <p className="text-xs font-bold text-red-400 mb-2 flex items-center gap-1"><FiAlertCircle /> Needs Attention (Weak)</p>
              <div className="flex flex-wrap gap-2">
                {weakTopics.length > 0 
                  ? weakTopics.map(t => <Badge key={t.id} variant="danger">{t.topic_name} ({t.score_indicator}%)</Badge>)
                  : <span className="text-sm text-gray-600">No weak topics identified yet.</span>
                }
              </div>
            </div>
            
            {data?.recommendations?.length > 0 && (
              <div>
                <p className="text-xs font-bold text-emerald-400 mb-2 mt-4 flex items-center gap-1"><FiCheckCircle /> Recommendations</p>
                <div className="space-y-2">
                  {data.recommendations.map(r => (
                    <div key={r.id} className="p-2 bg-gray-50 rounded border border-gray-200 text-sm">
                      <span className="font-bold text-gray-700 uppercase text-xs mr-2">{r.action_type}:</span>
                      <span className="text-gray-600">{r.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Right Panel: Chat Interface */}
      <div className="flex-1 flex flex-col h-full bg-[var(--color-bg-base)]">
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 hide-scrollbar relative">
          {messages.length === 0 && (
            <div className="text-center text-gray-600 mt-10">Start a conversation with your mentor!</div>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`
                max-w-[85%] px-5 py-3 rounded-2xl shadow-md
                ${msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' 
                  : 'bg-gray-50 border border-gray-200 text-gray-800 rounded-tl-sm'
                }
              `}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-start">
              <div className="px-5 py-3 rounded-2xl rounded-tl-sm bg-gray-50 border border-gray-200 text-gray-600 flex items-center gap-2">
                <FiCpu className="animate-pulse text-blue-400" />
                <span className="text-sm">Analyzing progress and formulating strategy...</span>
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] shrink-0">
          
          <div className="flex gap-2 mb-3 overflow-x-auto hide-scrollbar pb-1">
            {['I have an exam in 5 days.', 'I am weak in Deadlocks.', 'What should I study today?', 'I scored 45% in DBMS quiz.'].map((suggestion, i) => (
              <button 
                key={i} 
                onClick={() => { setInput(suggestion); }}
                className="whitespace-nowrap px-4 py-1.5 rounded-full bg-gray-50 border border-gray-200 text-[11px] font-bold text-gray-700 hover:text-gray-900 hover:border-blue-500 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <form onSubmit={handleSend} className="relative flex items-center">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your mentor for guidance..."
              className="w-full pl-5 pr-12 py-4 rounded-xl bg-white border border-gray-200 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors shadow-inner"
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isTyping}
              className={`absolute right-2 p-2.5 rounded-lg transition-all ${
                input.trim() && !isTyping 
                  ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-sm' 
                  : 'bg-gray-50 text-gray-600'
              }`}
            >
              <FiSend />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Mentor;
