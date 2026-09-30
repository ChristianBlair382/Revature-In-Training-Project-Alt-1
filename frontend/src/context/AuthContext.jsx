import { createContext, useContext, useMemo, useState } from "react";
import { apiClient } from "../api/client.js";

const AuthContext = createContext(null);

function decodeToken(token) {
    const payloadSegment = token.split('.')[1];
    return JSON.parse(atob(payloadSegment))
}

export function AuthProvider({children}) {
    const [token, setToken] = useState(() => localStorage.getItem('agricoreToken'));

    const user = useMemo(() => (token ? decodeToken(token): null), [token]);

    const login = async (username, password) => {
        const LoginFormData = new URLSearchParams();
        LoginFormData.append('username', username);
        LoginFormData.append('password', password);

        const response = await apiClient.post('/auth/token', LoginFormData, {
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        });
        localStorage.setItem('agricoreToken', response.data.access_token);
        setToken(response.data.access_token);
    }

    const logout = () => {
        localStorage.removeItem('agricoreToken');
        setToken(null);
    }

    const value = {token, user, isAuthenticated: Boolean(token), login, logout};

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
    const context = useContext(AuthContext);

    if (context === null) {
        throw new Error('useAuth must be used within AuthProvider')
    }
    return context;
}