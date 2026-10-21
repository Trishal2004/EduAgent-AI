import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiBell, FiSearch, FiMenu, FiCheckCircle, FiLoader } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import Sidebar from './Sidebar';
import { notificationService } from '../../services/notificationService';
import { searchService } from '../../services/searchService';

const MainLayout = ({ children }) => {
    const { user } = useAuth();
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    // Get page title based on route
    const getPageTitle = () => {
        const path = location.pathname;
        if (path.startsWith('/dashboard')) return 'Dashboard';
        if (path.startsWith('/tutor')) return 'AI Tutor';
        if (path.startsWith('/documents')) return 'My Documents';
        if (path.startsWith('/flashcards')) return 'Flashcards';
        if (path.startsWith('/notes')) return 'Notes';
        if (path.startsWith('/profile')) return 'Settings';
        return 'EduAgent AI';
    };

    // Notifications State
    const [notifications, setNotifications] = useState([]);
    const [showNotifications, setShowNotifications] = useState(false);
    const unreadCount = notifications.filter(n => !n.is_read).length;

    useEffect(() => {
        if (user) {
            notificationService.getNotifications().then(setNotifications).catch(console.error);
        }
    }, [user]);

    const handleMarkAsRead = async (id) => {
        try {
            await notificationService.markAsRead(id);
            setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
        } catch (err) {
            console.error(err);
        }
    };

    const handleMarkAllAsRead = async () => {
        try {
            await notificationService.markAllAsRead();
            setNotifications(notifications.map(n => ({ ...n, is_read: true })));
        } catch (err) {
            console.error(err);
        }
    };

    // Search State
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showSearchDropdown, setShowSearchDropdown] = useState(false);

    useEffect(() => {
        if (!searchQuery.trim()) {
            setSearchResults([]);
            setShowSearchDropdown(false);
            return;
        }
        
        const delaySearch = setTimeout(async () => {
            setIsSearching(true);
            try {
                const res = await searchService.search(searchQuery);
                setSearchResults(res.results || []);
                setShowSearchDropdown(true);
            } catch (err) {
                console.error(err);
            } finally {
                setIsSearching(false);
            }
        }, 300);

        return () => clearTimeout(delaySearch);
    }, [searchQuery]);

    // Group results by type
    const groupedResults = searchResults.reduce((acc, curr) => {
        if (!acc[curr.type]) acc[curr.type] = [];
        acc[curr.type].push(curr);
        return acc;
    }, {});

    return (
        <div className="min-h-screen bg-[var(--color-bg-base)] text-[var(--color-text-main)] flex">
            {/* Desktop Sidebar */}
            <div className="hidden lg:block w-64 shrink-0">
                <Sidebar />
            </div>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div 
                    className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-sm"
                    onClick={() => setSidebarOpen(false)}
                />
            )}
            
            {/* Mobile Sidebar */}
            <div className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 lg:hidden ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                <Sidebar />
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Topbar */}
                <header className="h-20 bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-30 flex items-center justify-between px-6 lg:px-10">
                    <div className="flex items-center gap-4">
                        <button 
                            className="lg:hidden p-2 -ml-2 text-gray-600 hover:text-gray-900"
                            onClick={() => setSidebarOpen(true)}
                        >
                            <FiMenu size={24} />
                        </button>
                        <h1 className="text-xl font-bold tracking-tight">{getPageTitle()}</h1>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden md:flex relative group">
                            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 group-focus-within:text-blue-400 transition-colors" />
                            <input 
                                type="text" 
                                placeholder="Search everything..." 
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-10 pr-4 py-2 w-64 bg-white border border-gray-200 rounded-full text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-gray-900 placeholder-gray-400"
                            />
                            {isSearching && (
                                <FiLoader className="absolute right-3 top-1/2 -translate-y-1/2 text-blue-500 animate-spin" />
                            )}
                            {showSearchDropdown && (
                                <div className="absolute top-12 left-0 w-80 bg-white border border-gray-200 shadow-md rounded-2xl overflow-hidden z-50 flex flex-col max-h-96">
                                    <div className="p-3 border-b border-gray-200 bg-white/80">
                                        <span className="text-xs font-bold text-gray-600 uppercase tracking-wider">Search Results</span>
                                    </div>
                                    <div className="flex-1 overflow-y-auto">
                                        {searchResults.length === 0 ? (
                                            <div className="p-4 text-center text-gray-600 text-sm">No results found.</div>
                                        ) : (
                                            Object.keys(groupedResults).map(type => (
                                                <div key={type} className="border-b border-gray-200 last:border-0">
                                                    <div className="px-4 py-1.5 bg-gray-100 text-[10px] font-bold text-blue-400 uppercase tracking-wider">
                                                        {type}
                                                    </div>
                                                    {groupedResults[type].map(item => (
                                                        <a 
                                                            key={item.id} 
                                                            href={item.url || '#'} 
                                                            className="block px-4 py-2 hover:bg-gray-50 transition-colors"
                                                            onClick={() => { setShowSearchDropdown(false); setSearchQuery(''); }}
                                                        >
                                                            <div className="text-sm font-bold text-gray-800 truncate">{item.title}</div>
                                                            {item.snippet && <div className="text-xs text-gray-600 truncate mt-0.5">{item.snippet}</div>}
                                                        </a>
                                                    ))}
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="relative">
                            <button 
                                onClick={() => setShowNotifications(!showNotifications)}
                                className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors"
                            >
                                <FiBell size={20} />
                                {unreadCount > 0 && (
                                    <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold border-2 border-slate-900 rounded-full flex items-center justify-center">
                                        {unreadCount > 9 ? '9+' : unreadCount}
                                    </span>
                                )}
                            </button>

                            {showNotifications && (
                                <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 shadow-md rounded-2xl overflow-hidden z-50 flex flex-col max-h-96">
                                    <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-white/80">
                                        <h3 className="font-bold text-gray-900">Notifications</h3>
                                        {unreadCount > 0 && (
                                            <button onClick={handleMarkAllAsRead} className="text-xs text-blue-400 hover:text-blue-300 transition-colors">Mark all read</button>
                                        )}
                                    </div>
                                    <div className="flex-1 overflow-y-auto">
                                        {notifications.length === 0 ? (
                                            <div className="p-8 text-center text-gray-600 text-sm">No notifications yet.</div>
                                        ) : (
                                            notifications.map(notif => (
                                                <div key={notif.id} onClick={() => !notif.is_read && handleMarkAsRead(notif.id)} className={`p-4 border-b border-gray-200 transition-colors cursor-pointer ${notif.is_read ? 'opacity-60 bg-gray-50' : 'bg-white hover:bg-gray-50'}`}>
                                                    <div className="flex justify-between items-start mb-1">
                                                        <span className="text-sm font-bold text-gray-800">{notif.title}</span>
                                                        {!notif.is_read && <span className="w-2 h-2 rounded-full bg-blue-500 mt-1 shrink-0" />}
                                                    </div>
                                                    <p className="text-xs text-gray-600 line-clamp-2">{notif.message}</p>
                                                    <p className="text-[10px] text-gray-600 mt-2 font-medium">{new Date(notif.created_at).toLocaleString()}</p>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-medium text-gray-900 leading-none mb-1">{user?.full_name || 'Student'}</p>
                                <p className="text-xs text-gray-600 leading-none">{user?.email}</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 p-[2px]">
                                <div className="w-full h-full bg-white rounded-full flex items-center justify-center font-bold text-sm">
                                    {(user?.full_name || 'S').charAt(0).toUpperCase()}
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 p-6 lg:p-10 overflow-y-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                        key={location.pathname}
                        className="h-full"
                    >
                        {children}
                    </motion.div>
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
