import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiLock, FiArrowRight, FiArrowLeft } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { authService } from '../services/authService';

const ResetPassword = () => {
    const [password, setPassword] = useState('');
    const [passwordConfirm, setPasswordConfirm] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [otp, setOtp] = useState('');
    const [email, setEmail] = useState('');
    
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Extract email from URL query params
        const params = new URLSearchParams(location.search);
        const emailParam = params.get('email');
        if (emailParam) {
            setEmail(emailParam);
        } else {
            toast.error("Invalid or missing email.");
            navigate('/forgot-password');
        }
    }, [location, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (password !== passwordConfirm) {
            toast.error("Passwords do not match");
            return;
        }
        
        if (!email || !otp) {
            toast.error("Missing email or OTP.");
            return;
        }

        setIsLoading(true);
        try {
            await authService.resetPassword(email, otp, password, passwordConfirm);
            setIsSuccess(true);
            toast.success("Password reset successfully! Redirecting to login...");
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            toast.error(err.customMessage || 'Failed to reset password. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center relative overflow-hidden py-10">
            <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-emerald-500/20 rounded-full blur-[100px] -z-10" />
            
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md"
            >
                <div className="glass-card p-10 relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />
                    
                    <div className="text-center mb-8">
                        <motion.h2 
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="text-3xl font-bold text-gray-900 mb-2"
                        >
                            New Password
                        </motion.h2>
                        <p className="text-[var(--color-text-muted)]">
                            Enter your new password below
                        </p>
                    </div>

                    {!isSuccess ? (
                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">6-Digit OTP *</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-600">
                                        <FiLock />
                                    </div>
                                    <input 
                                        type="text" 
                                        placeholder="Enter OTP" 
                                        value={otp} 
                                        onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))} 
                                        required 
                                        maxLength={6}
                                        className="w-full pl-10 pr-4 py-3 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-gray-900 placeholder-gray-500 tracking-widest text-center text-xl font-mono"
                                    />
                                </div>
                            </div>
                            
                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">New Password *</label>
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
                                        className="w-full pl-10 pr-4 py-3 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-gray-900 placeholder-gray-500"
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-[var(--color-text-muted)] ml-1">Confirm New Password *</label>
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
                                        className="w-full pl-10 pr-4 py-3 bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-gray-900 placeholder-gray-500"
                                    />
                                </div>
                            </div>

                            <motion.button 
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit" 
                                disabled={isLoading || otp.length !== 6 || !email}
                                className="w-full py-3 mt-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl font-medium shadow-[0_0_20px_rgba(16,185,129,0.3)] flex justify-center items-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <span className="flex items-center gap-2">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Resetting...
                                    </span>
                                ) : (
                                    <>Reset Password <FiArrowRight /></>
                                )}
                            </motion.button>
                        </form>
                    ) : (
                        <div className="p-4 bg-emerald-900/30 border border-emerald-500/50 rounded-xl text-emerald-200 text-sm text-center mb-6">
                            Your password has been reset successfully! Redirecting to login...
                        </div>
                    )}
                    
                    <div className="mt-8 text-center text-sm text-[var(--color-text-muted)]">
                        <Link to="/login" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors flex items-center justify-center gap-1">
                            <FiArrowLeft /> Back to Login
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default ResetPassword;
