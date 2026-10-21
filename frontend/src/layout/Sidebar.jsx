import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FiHome, FiMessageSquare, FiBookOpen, FiFileText,
  FiUpload, FiFolder, FiBookmark, FiPlayCircle,
  FiSettings, FiHelpCircle, FiLogOut, FiTrendingUp, FiMonitor, FiCalendar, FiShare2, FiActivity
} from 'react-icons/fi';

const sidebarGroups = [
  {
    title: 'Learning',
    items: [
      { name: 'Dashboard', icon: <FiHome />, path: '/dashboard' },
      { name: 'AI Chat', icon: <FiMessageSquare />, path: '/chat' },
      { name: 'Knowledge Graph', icon: <FiShare2 />, path: '/graph' },
      { name: 'Study Notes', icon: <FiBookOpen />, path: '/notes' },
      { name: 'Flashcards', icon: <FiFileText />, path: '/flashcards' },
    ]
  },
  {
    title: 'Documents',
    items: [
      { name: 'Upload', icon: <FiUpload />, path: '/upload' },
      { name: 'My Documents', icon: <FiFolder />, path: '/documents' },
      { name: 'Workspace', icon: <FiMonitor />, path: '/workspace/1' },
    ]
  },
  {
    title: 'Practice',
    items: [
      { name: 'Quiz', icon: <FiPlayCircle />, path: '/quiz' },
      { name: 'Question Papers', icon: <FiFileText />, path: '/question-paper' },
    ]
  },
  {
    title: 'Analytics & Planning',
    items: [
      { name: 'Learning Analytics', icon: <FiActivity />, path: '/analytics' },
      { name: 'Academic Mentor', icon: <FiTrendingUp />, path: '/mentor' },
      { name: 'Study Planner', icon: <FiCalendar />, path: '/planner' },
    ]
  }
];

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-[var(--color-bg-base)]/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar container */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-72 bg-[var(--color-bg-card)] border-r border-[var(--color-border-subtle)]
        transform transition-transform duration-300 ease-in-out flex flex-col hide-scrollbar
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="h-20 flex items-center px-8 shrink-0">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-bold text-xl shadow-[0_0_15px_rgba(37,99,235,0.4)] group-hover:scale-110 transition-transform">
              E
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              EduAgent<span className="text-blue-500">.ai</span>
            </span>
          </Link>
        </div>

        {/* Navigation Groups */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-8 hide-scrollbar">
          {sidebarGroups.map((group, idx) => (
            <div key={idx}>
              <h4 className="px-4 text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-widest mb-3">
                {group.title}
              </h4>
              <div className="space-y-1">
                {group.items.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      className={`relative flex items-center space-x-3 px-4 py-2.5 rounded-xl transition-all duration-300 group ${
                        isActive 
                          ? 'text-white bg-blue-500/10' 
                          : 'text-[var(--color-text-muted)] hover:text-white hover:bg-slate-800/50'
                      }`}
                    >
                      {isActive && (
                        <motion.div 
                          layoutId="sidebar-active"
                          className="absolute inset-0 bg-[var(--color-primary)]/10 rounded-xl border border-[var(--color-primary)]/30 shadow-[0_0_15px_rgba(37,99,235,0.15)]"
                        />
                      )}
                      
                      <span className={`relative z-10 text-lg transition-colors ${isActive ? 'text-blue-400' : 'group-hover:text-blue-400'}`}>
                        {item.icon}
                      </span>
                      <span className="relative z-10 font-medium">
                        {item.name}
                      </span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* System Settings */}
        <div className="p-4 border-t border-[var(--color-border-subtle)] space-y-1">
          <Link to="/settings" className="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-[var(--color-text-muted)] hover:text-white hover:bg-slate-800/50 transition-all">
            <FiSettings className="text-lg" />
            <span className="font-medium">Settings</span>
          </Link>
          <button className="w-full flex items-center space-x-3 px-4 py-2.5 rounded-xl text-[var(--color-text-muted)] hover:text-red-400 hover:bg-red-500/10 transition-all">
            <FiLogOut className="text-lg" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
