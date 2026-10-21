import { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Run this once when the app loads to check if a user is already logged in
    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    // Fetch the user's profile using the token
                    const userData = await authService.getMe();
                    setUser(userData);
                } catch (error) {
                    console.error('Token expired or invalid');
                    localStorage.removeItem('token');
                    setUser(null);
                }
            }
            setLoading(false);
        };
        fetchUser();
    }, []);

    const login = async (email, password) => {
        const data = await authService.login(email, password);
        localStorage.setItem('token', data.access_token);
        if (data.user) {
            setUser(data.user);
        } else {
            try {
                const userData = await authService.getMe();
                setUser(userData);
            } catch (e) {
                console.error("Failed to fetch user after login", e);
            }
        }
    };

    const loginRequest = async (email, password) => {
        return await authService.loginRequest(email, password);
    };

    const verifyLoginOtp = async (email, otp) => {
        const data = await authService.verifyLoginOtp(email, otp);
        localStorage.setItem('token', data.access_token);
        if (data.user) {
            setUser(data.user);
        }
        return data;
    };

    const register = async (email, fullName, password, passwordConfirm) => {
        await authService.register(email, password, passwordConfirm, fullName);
    };

    const verifyEmail = async (email, otp) => {
        const data = await authService.verifyEmail(email, otp);
        return data;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, loginRequest, verifyLoginOtp, register, verifyEmail, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
