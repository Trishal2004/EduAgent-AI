import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    FiHome, FiCpu, FiBook, FiFolder, FiAward, FiSettings, FiLogOut 
} from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { logout } = useAuth();

    const navItems = [
        { path: '/dashboard', label: 'Dashboard', icon: <FiHome /> },
        { path: '/tutor', label: 'AI Tutor', icon: <FiCpu /> },
        { path: '/documents', label: 'My Documents', icon: <FiFolder /> },
        { path: '/flashcards', label: 'Flashcards', icon: <FiAward /> },
        { path: '/notes', label: 'Notes', icon: <FiBook /> },
    ];

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside className="w-64 h-screen bg-white border-r border-gray-200 flex flex-col fixed left-0 top-0 z-50">
            <div className="p-6">
                <Link to="/dashboard" className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-sm">
                        EA
                    </div>
                    <span className="text-xl font-bold text-blue-700">
                        EduAgent AI
                    </span>
                </Link>
            </div>

            <div className="flex-1 px-4 py-6 space-y-2 overflow-y-auto hide-scrollbar">
                <p className="px-4 text-xs font-bold text-gray-600 uppercase tracking-wider mb-4">Main Menu</p>
                {navItems.map((item) => {
                    const isActive = location.pathname.startsWith(item.path);
                    return (
                        <Link 
                            key={item.path} 
                            to={item.path}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all relative group ${
                                isActive ? 'text-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                            }`}
                        >
                            {isActive && (
                                <motion.div 
                                    layoutId="active-sidebar-bg"
                                    className="absolute inset-0 bg-blue-50 border border-blue-200 rounded-xl"
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                            <div className={`text-xl relative z-10 ${isActive ? 'text-blue-600' : 'group-hover:text-blue-600 transition-colors'}`}>
                                {item.icon}
                            </div>
                            <span className="font-medium relative z-10">{item.label}</span>
                        </Link>
                    );
                })}
            </div>

            <div className="p-4 border-t border-gray-200">
                <Link 
                    to="/settings"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all relative ${
                        location.pathname === '/settings' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                >
                    <FiSettings className="text-xl" />
                    <span className="font-medium">Settings</span>
                </Link>
                <button 
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 hover:text-red-400 hover:bg-red-900/10 transition-all mt-1"
                >
                    <FiLogOut className="text-xl" />
                    <span className="font-medium">Logout</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
