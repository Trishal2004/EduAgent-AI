import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiRefreshCw } from 'react-icons/fi';

const OtpInput = ({ length = 6, onComplete, onResend, isLoading }) => {
    const [otp, setOtp] = useState(new Array(length).fill(''));
    const [countdown, setCountdown] = useState(60);
    const inputRefs = useRef([]);

    useEffect(() => {
        let timer;
        if (countdown > 0) {
            timer = setTimeout(() => setCountdown(countdown - 1), 1000);
        }
        return () => clearTimeout(timer);
    }, [countdown]);

    const handleChange = (e, index) => {
        const { value } = e.target;
        if (isNaN(value)) return;

        const newOtp = [...otp];
        // Allow only one character per box
        newOtp[index] = value.substring(value.length - 1);
        setOtp(newOtp);

        // Move to next input if not the last one
        if (value && index < length - 1) {
            inputRefs.current[index + 1].focus();
        }

        if (newOtp.every(v => v !== '')) {
            onComplete(newOtp.join(''));
        }
    };

    const handleKeyDown = (e, index) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            const newOtp = [...otp];
            newOtp[index - 1] = '';
            setOtp(newOtp);
            inputRefs.current[index - 1].focus();
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').slice(0, length).replace(/\D/g, '');
        if (pastedData) {
            const newOtp = [...otp];
            pastedData.split('').forEach((char, i) => {
                newOtp[i] = char;
            });
            setOtp(newOtp);
            if (pastedData.length === length) {
                onComplete(newOtp.join(''));
                inputRefs.current[length - 1].focus();
            } else {
                inputRefs.current[pastedData.length].focus();
            }
        }
    };

    const handleResend = () => {
        if (countdown === 0) {
            setOtp(new Array(length).fill(''));
            setCountdown(60);
            inputRefs.current[0].focus();
            onResend();
        }
    };

    return (
        <div className="flex flex-col items-center space-y-6">
            <div className="flex justify-center gap-3">
                {otp.map((data, index) => (
                    <input
                        key={index}
                        type="text"
                        name="otp"
                        maxLength="1"
                        ref={el => inputRefs.current[index] = el}
                        value={data}
                        onChange={e => handleChange(e, index)}
                        onKeyDown={e => handleKeyDown(e, index)}
                        onPaste={handlePaste}
                        disabled={isLoading}
                        className="w-12 h-14 text-center text-xl font-bold bg-[var(--color-bg-base)]/50 border border-[var(--color-border-subtle)] rounded-xl focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                ))}
            </div>

            <div className="flex items-center text-sm text-[var(--color-text-muted)] gap-2">
                {countdown > 0 ? (
                    <p>Resend code in {countdown}s</p>
                ) : (
                    <button
                        type="button"
                        onClick={handleResend}
                        disabled={isLoading}
                        className="text-blue-400 hover:text-blue-300 font-medium transition-colors flex items-center gap-1 disabled:opacity-50"
                    >
                        <FiRefreshCw size={14} /> Resend Code
                    </button>
                )}
            </div>
        </div>
    );
};

export default OtpInput;
