"use client";

import {
    createContext,
    useContext,
    useEffect,
    useSyncExternalStore,
    type ReactNode,
} from "react";

type Theme = "light" | "dark";
const THEME_CHANGE_EVENT = "codepilot-theme-change";

interface ThemeContextValue {
    theme: Theme;
    toggleTheme: () => void;
    setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue>({
    theme: "light",
    toggleTheme: () => { },
    setTheme: () => { },
});

function getThemeSnapshot(): Theme {
    const stored = localStorage.getItem("codepilot-theme");
    if (stored === "dark" || stored === "light") {
        return stored;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getServerThemeSnapshot(): Theme {
    return "light";
}

function subscribeToThemeChanges(callback: () => void) {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const onSystemThemeChange = () => {
        if (!localStorage.getItem("codepilot-theme")) {
            callback();
        }
    };
    window.addEventListener(THEME_CHANGE_EVENT, callback);
    window.addEventListener("storage", callback);
    mediaQuery.addEventListener("change", onSystemThemeChange);
    return () => {
        window.removeEventListener(THEME_CHANGE_EVENT, callback);
        window.removeEventListener("storage", callback);
        mediaQuery.removeEventListener("change", onSystemThemeChange);
    };
}

function applyTheme(theme: Theme) {
    document.documentElement.classList.toggle("dark", theme === "dark");
}

export function ThemeProvider({ children }: { children: ReactNode }) {
    const theme = useSyncExternalStore(
        subscribeToThemeChanges,
        getThemeSnapshot,
        getServerThemeSnapshot,
    );

    useEffect(() => {
        applyTheme(theme);
    }, [theme]);

    function selectTheme(next: Theme) {
        applyTheme(next);
        localStorage.setItem("codepilot-theme", next);
        window.dispatchEvent(new Event(THEME_CHANGE_EVENT));
    }

    function toggleTheme() {
        selectTheme(theme === "light" ? "dark" : "light");
    }

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme, setTheme: selectTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    return useContext(ThemeContext);
}
