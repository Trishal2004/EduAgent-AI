import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { KeyRound, Loader2, ArrowLeft, Mail, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';

const VerifyEmail = () => {
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    
    // Timer state
    const [countdown, setCountdown] = useState(60);
    const [canResend, setCanResend] = useState(false);

    const navigate = useNavigate();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const email = searchParams.get('email');
    
    const { verifyEmail } = useAuth();
    
    const inputRefs = useRef([]);

    useEffect(() => {
        if (!email) {
            navigate('/login');
        }
    }, [email, navigate]);

    // Timer effect
    useEffect(() => {
        let timer;
        if (countdown > 0 && !canResend) {
            timer = setInterval(() => {
                setCountdown((prev) => prev - 1);
            }, 1000);
        } else if (countdown === 0) {
            setCanResend(true);
        }
        return () => clearInterval(timer);
    }, [countdown, canResend]);

    const handleChange = (element, index) => {
        if (isNaN(element.value)) return false;

        setOtp([...otp.map((d, idx) => (idx === index ? element.value : d))]);

        // Focus next input
        if (element.nextSibling && element.value) {
            element.nextSibling.focus();
        }
    };

    const handleKeyDown = (e, index) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            // Focus previous input on backspace
            inputRefs.current[index - 1].focus();
        }
    };

    const handleVerify = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        const otpCode = otp.join('');
        if (otpCode.length !== 6) {
            setError("Please enter a valid 6-digit code.");
            return;
        }

        setLoading(true);
        try {
            await verifyEmail(email, otpCode);
            setSuccess('Email verified successfully! Taking you to login...');
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || "Invalid or expired verification code.");
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        if (!canResend) return;
        
        setError('');
        setSuccess('');
        setLoading(true);
        try {
            await authService.resendOtp(email);
            setSuccess('A new verification code has been sent to your email.');
            setCountdown(60);
            setCanResend(false);
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0].focus();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to resend code. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (!email) return null;

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/20 blur-[120px]" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/20 blur-[120px]" />

            <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <div className="flex justify-center mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-sm shadow-indigo-500/30">
                        <Mail className="h-8 w-8 text-gray-900" />
                    </div>
                </div>
                <h2 className="mt-2 text-center text-3xl font-extrabold text-gray-900 tracking-tight">
                    Verify Your Email
                </h2>
                <p className="mt-4 text-center text-sm text-gray-600 max-w-sm mx-auto">
                    We've sent a 6-digit verification code to<br/>
                    <span className="font-semibold text-gray-900">{email}</span>
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <div className="bg-gray-50/80 backdrop-blur-xl py-8 px-4 shadow-md sm:rounded-2xl sm:px-10 border border-gray-200">
                    <form className="space-y-6" onSubmit={handleVerify}>
                        
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg text-sm flex items-center gap-2">
                                <div className="w-1 h-1 rounded-full bg-red-400"></div>
                                {error}
                            </div>
                        )}
                        
                        {success && (
                            <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 p-3 rounded-lg text-sm flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                                {success}
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-4 text-center">
                                Enter your verification code
                            </label>
                            <div className="flex justify-center gap-2 sm:gap-3">
                                {otp.map((data, index) => {
                                    return (
                                        <input
                                            key={index}
                                            type="text"
                                            name="otp"
                                            maxLength="1"
                                            ref={(el) => inputRefs.current[index] = el}
                                            value={data}
                                            onChange={(e) => handleChange(e.target, index)}
                                            onFocus={(e) => e.target.select()}
                                            onKeyDown={(e) => handleKeyDown(e, index)}
                                            className="w-10 h-12 sm:w-12 sm:h-14 text-center text-xl font-bold bg-slate-950/50 border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all shadow-sm"
                                        />
                                    );
                                })}
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || success || otp.join('').length !== 6}
                            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Verify Email'}
                        </button>
                    </form>

                    <div className="mt-8 flex flex-col items-center justify-center gap-4">
                        <button 
                            onClick={handleResend}
                            disabled={!canResend || loading || success}
                            className={`text-sm font-medium transition-colors ${
                                canResend 
                                    ? 'text-indigo-400 hover:text-indigo-300' 
                                    : 'text-gray-600 cursor-not-allowed'
                            }`}
                        >
                            {canResend ? 'Resend verification code' : `Resend code in ${countdown}s`}
                        </button>

                        <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors flex items-center gap-2">
                            <ArrowLeft className="h-4 w-4" />
                            Back to Login
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VerifyEmail;
