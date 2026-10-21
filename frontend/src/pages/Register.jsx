import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { FiMail, FiLock, FiUser, FiUserPlus, FiKey } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { authService } from '../services/authService';

const Register = () => {
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [passwordConfirm, setPasswordConfirm] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Frontend validation
        if (password !== passwordConfirm) {
            toast.error("Passwords do not match");
            return;
        }
        
        setIsLoading(true);
        try {
            await register(email, fullName, password, passwordConfirm);
            toast.success("Registration successful! Please check your email for the verification code.");
            navigate(`/verify-email?email=${encodeURIComponent(email)}`);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to register. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[85vh] flex items-center justify-center relative overflow-hidden py-10">
            {/* Background elements */}
            <div className="absolute top-1/4 right-1/4 w-80 h-80 bg-indigo-500/20 rounded-full blur-[120px] -z-10" />
            <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-[100px] -z-10" />
            
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md"
            >
                <div className="glass-card p-10 relative overflow-hidden group">
                    {/* Glowing top border */}
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />
                    
                    <div className="text-center mb-8">
                        <motion.h2 
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="text-3xl font-bold text-gray-900 mb-2"
                        >
                            Create Account
                        </motion.h2>
                        <p className="text-[var(--color-text-muted)]">
                            Join us and start your journey
                        </p>
                    </div>
                    
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">Email Address *</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-600">
                                    <FiMail />
                                </div>
                                <input 
                                    type="email" 
                                    placeholder="you@example.com" 
                                    value={email} 
                                    onChange={(e) => setEmail(e.target.value)} 
                                    required 
                                    className="w-full pl-10 pr-4 py-2.5 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-gray-900 placeholder-gray-500"
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">Full Name (Optional)</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-600">
                                    <FiUser />
                                </div>
                                <input 
                                    type="text" 
                                    placeholder="John Doe" 
                                    value={fullName} 
                                    onChange={(e) => setFullName(e.target.value)} 
                                    className="w-full pl-10 pr-4 py-2.5 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-gray-900 placeholder-gray-500"
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">Password *</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-600">
                                    <FiLock />
                                </div>
                                <input 
                                    type="password" 
                                    placeholder="Min 8 characters" 
                                    value={password} 
                                    onChange={(e) => setPassword(e.target.value)} 
                                    required 
                                    minLength={8}
                                    className="w-full pl-10 pr-4 py-2.5 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-gray-900 placeholder-gray-500"
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">Confirm Password *</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-600">
                                    <FiLock />
                                </div>
                                <input 
                                    type="password" 
                                    placeholder="Re-enter password" 
                                    value={passwordConfirm} 
                                    onChange={(e) => setPasswordConfirm(e.target.value)} 
                                    required 
                                    minLength={8}
                                    className="w-full pl-10 pr-4 py-2.5 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-gray-900 placeholder-gray-500"
                                />
                            </div>
                        </div>

                        <motion.button 
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            type="submit" 
                            disabled={isLoading}
                            className="w-full py-3 mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-medium shadow-[0_0_20px_rgba(79,70,229,0.3)] flex justify-center items-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <span className="flex items-center gap-2">
                                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Processing...
                                </span>
                            ) : (
                                <>
                                    Create Account <FiUserPlus />
                                </>
                            )}
                        </motion.button>
                    </form>
                    
                    <div className="mt-6 text-center text-sm text-[var(--color-text-muted)]">
                        Already have an account?{' '}
                        <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                            Sign in here
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Register;
