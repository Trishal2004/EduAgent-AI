import { FiMenu, FiSearch, FiBell } from 'react-icons/fi';
import { motion } from 'framer-motion';

const Navbar = ({ toggleSidebar }) => {
  return (
    <header className="h-20 bg-[var(--color-bg-base)]/80 backdrop-blur-xl border-b border-[var(--color-border-subtle)] flex items-center justify-between px-6 z-30 sticky top-0">
      
      <div className="flex items-center gap-4 flex-1">
        <button 
          onClick={toggleSidebar}
          className="lg:hidden p-2 text-[var(--color-text-muted)] hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
        >
          <FiMenu className="text-2xl" />
        </button>

        {/* Global Search */}
        <div className="hidden md:flex items-center relative w-full max-w-xl group">
          <FiSearch className="absolute left-4 text-[var(--color-text-muted)] group-focus-within:text-blue-400 transition-colors" />
          <input 
            type="text" 
            placeholder="Search learning materials, notes, or ask AI..." 
            className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] text-sm text-[var(--color-text-main)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-blue-500/50 focus:bg-slate-800/80 transition-all shadow-inner"
          />
          <div className="absolute right-3 px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">
            ⌘ K
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Notifications */}
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative p-2.5 text-[var(--color-text-muted)] hover:text-white bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] hover:border-slate-600 rounded-full transition-colors shadow-sm"
        >
          <FiBell className="text-lg" />
          <span className="absolute top-2 right-2.5 w-2 h-2 bg-[var(--color-danger)] rounded-full shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
        </motion.button>

        {/* Profile Avatar */}
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center gap-2 p-1 pr-3 rounded-full bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] hover:border-slate-600 transition-colors shadow-sm"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-inner">
            JD
          </div>
          <span className="text-sm font-medium hidden sm:block text-[var(--color-text-main)]">John Doe</span>
        </motion.button>
      </div>
      
    </header>
  );
};

export default Navbar;
