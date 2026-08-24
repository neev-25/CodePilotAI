"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import api from "@/app/lib/api";

interface AuthUser {
    id: number;
    name: string;
    email: string;
    created_at: string;
}

interface AuthContextValue {
    user: AuthUser | null;
    token: string | null;
    loading: boolean;
    login: (token: string, user: AuthUser) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
    user: null,
    token: null,
    loading: true,
    login: () => { },
    logout: () => { },
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // On mount: restore session from localStorage
    useEffect(() => {
        const storedToken = localStorage.getItem("codepilot-token");
        if (storedToken) {
            api.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
            api
                .get<AuthUser>("/auth/me")
                .then((res) => {
                    setToken(storedToken);
                    setUser(res.data);
                })
                .catch(() => {
                    localStorage.removeItem("codepilot-token");
                    delete api.defaults.headers.common["Authorization"];
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    function login(newToken: string, newUser: AuthUser) {
        localStorage.setItem("codepilot-token", newToken);
        document.cookie = `codepilot-token=${newToken}; path=/; max-age=604800`;
        api.defaults.headers.common["Authorization"] = `Bearer ${newToken}`;
        setToken(newToken);
        setUser(newUser);
    }

    function logout() {
        localStorage.removeItem("codepilot-token");
        document.cookie = "codepilot-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        delete api.defaults.headers.common["Authorization"];
        setToken(null);
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, token, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
