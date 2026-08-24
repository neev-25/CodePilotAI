"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

type Theme = "light" | "dark";

interface ThemeContextValue {
    theme: Theme;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
    theme: "light",
    toggleTheme: () => { },
});

export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<Theme>("light");

    // On mount: read persisted preference or system preference
    useEffect(() => {
        const stored = localStorage.getItem("codepilot-theme") as Theme | null;
        if (stored === "dark" || stored === "light") {
            applyTheme(stored);
            setTheme(stored);
        } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            applyTheme("dark");
            setTheme("dark");
        }
    }, []);

    function applyTheme(t: Theme) {
        document.documentElement.classList.toggle("dark", t === "dark");
    }

    function toggleTheme() {
        setTheme((prev) => {
            const next: Theme = prev === "light" ? "dark" : "light";
            applyTheme(next);
            localStorage.setItem("codepilot-theme", next);
            return next;
        });
    }

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    return useContext(ThemeContext);
}
