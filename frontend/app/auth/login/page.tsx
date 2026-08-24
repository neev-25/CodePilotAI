"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
    AlertCircle,
    Eye,
    EyeOff,
    Loader2,
    GitBranch,
    Sparkles,
    Bot,
    Zap,
    ArrowRight,
    User,
    Lock,
    Mail,
} from "lucide-react";
import { loginUser, registerUser } from "@/app/lib/authApi";
import { useAuth } from "@/app/contexts/AuthContext";

/* ─── tiny animated "code rain" dots in the bg ─ */
const DOTS = Array.from({ length: 18 }, (_, i) => i);

export default function FlipAuthPage() {
    const router = useRouter();
    const { login } = useAuth();
    const [flipped, setFlipped] = useState(false);

    /* ── Login state ── */
    const [loginEmail, setLoginEmail] = useState("");
    const [loginPass, setLoginPass] = useState("");
    const [showLoginPass, setShowLoginPass] = useState(false);
    const [loginError, setLoginError] = useState("");
    const [loginLoading, setLoginLoading] = useState(false);

    /* ── Register state ── */
    const [regName, setRegName] = useState("");
    const [regEmail, setRegEmail] = useState("");
    const [regPass, setRegPass] = useState("");
    const [showRegPass, setShowRegPass] = useState(false);
    const [regError, setRegError] = useState("");
    const [regLoading, setRegLoading] = useState(false);

    async function handleLogin(e: React.FormEvent) {
        e.preventDefault();
        setLoginError("");
        setLoginLoading(true);
        try {
            const res = await loginUser(loginEmail, loginPass);
            login(res.access_token, res.user);
            router.replace("/");
        } catch (err: unknown) {
            const msg =
                (err as { response?: { data?: { detail?: string } } })?.response?.data
                    ?.detail ?? "Invalid email or password.";
            setLoginError(msg);
        } finally {
            setLoginLoading(false);
        }
    }

    async function handleRegister(e: React.FormEvent) {
        e.preventDefault();
        setRegError("");
        if (regPass.length < 8) {
            setRegError("Password must be at least 8 characters.");
            return;
        }
        setRegLoading(true);
        try {
            const res = await registerUser(regName, regEmail, regPass);
            login(res.access_token, res.user);
            router.replace("/");
        } catch (err: unknown) {
            const msg =
                (err as { response?: { data?: { detail?: string } } })?.response?.data
                    ?.detail ?? "Registration failed. Please try again.";
            setRegError(msg);
        } finally {
            setRegLoading(false);
        }
    }

    return (
        <div className="flip-auth-scene">
            {/* ── Animated background ── */}
            <div className="flip-auth-bg" aria-hidden>
                <div className="flip-bg-blob flip-blob-1" />
                <div className="flip-bg-blob flip-blob-2" />
                <div className="flip-bg-blob flip-blob-3" />
                {DOTS.map((i) => (
                    <div
                        key={i}
                        className="flip-particle"
                        style={{
                            left: `${(i * 5.8) % 100}%`,
                            top: `${(i * 7.3 + 10) % 100}%`,
                            animationDelay: `${(i * 0.37) % 3}s`,
                            animationDuration: `${3 + (i % 4)}s`,
                        }}
                    />
                ))}
                {/* floating code snippets */}
                <span className="flip-code-float" style={{ left: "8%", top: "20%", animationDelay: "0s" }}>
                    {"{ AI }"}
                </span>
                <span className="flip-code-float" style={{ right: "9%", top: "35%", animationDelay: "1.5s" }}>
                    {"<CodePilot />"}
                </span>
                <span className="flip-code-float" style={{ left: "12%", bottom: "25%", animationDelay: "0.8s" }}>
                    {"git push"}
                </span>
                <span className="flip-code-float" style={{ right: "7%", bottom: "20%", animationDelay: "2.2s" }}>
                    {"⚡ Gemini"}
                </span>
            </div>

            {/* ── Card wrapper (perspective container) ── */}
            <div className={`flip-card-wrapper ${flipped ? "flipped" : ""}`}>
                {/* ─── FRONT: Login ─────────────────────────── */}
                <div className="flip-face flip-front">
                    {/* Glass header */}
                    <div className="flip-card-header">
                        <div className="flip-logo">
                            <span className="flip-logo-icon">
                                <Sparkles size={18} />
                            </span>
                            <span>CodePilot AI</span>
                        </div>
                        <div className="flip-header-badges">
                            <span className="flip-badge">
                                <GitBranch size={13} /> GitHub
                            </span>
                            <span className="flip-badge">
                                <Bot size={13} /> Gemini
                            </span>
                        </div>
                    </div>

                    {/* Hero text */}
                    <div className="flip-card-hero">
                        <h1 className="flip-title">Welcome back</h1>
                        <p className="flip-subtitle">Sign in to your AI workspace</p>
                    </div>

                    {/* Error */}
                    {loginError && (
                        <div className="flip-error">
                            <AlertCircle size={14} />
                            {loginError}
                        </div>
                    )}

                    <form onSubmit={handleLogin} className="flip-form">
                        {/* Email */}
                        <div className="flip-field">
                            <span className="flip-field-icon">
                                <Mail size={15} />
                            </span>
                            <input
                                type="email"
                                autoComplete="email"
                                required
                                placeholder="Email address"
                                value={loginEmail}
                                onChange={(e) => setLoginEmail(e.target.value)}
                                className="flip-input"
                            />
                        </div>

                        {/* Password */}
                        <div className="flip-field">
                            <span className="flip-field-icon">
                                <Lock size={15} />
                            </span>
                            <input
                                type={showLoginPass ? "text" : "password"}
                                autoComplete="current-password"
                                required
                                placeholder="Password"
                                value={loginPass}
                                onChange={(e) => setLoginPass(e.target.value)}
                                className="flip-input flip-input-pw"
                            />
                            <button
                                type="button"
                                onClick={() => setShowLoginPass((s) => !s)}
                                className="flip-pw-toggle"
                                tabIndex={-1}
                            >
                                {showLoginPass ? <EyeOff size={15} /> : <Eye size={15} />}
                            </button>
                        </div>

                        <button
                            type="submit"
                            disabled={loginLoading}
                            className="flip-submit-btn"
                        >
                            {loginLoading ? (
                                <>
                                    <Loader2 size={15} className="animate-spin" /> Signing in…
                                </>
                            ) : (
                                <>
                                    Sign in <ArrowRight size={15} />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="flip-divider">
                        <span>Don&apos;t have an account?</span>
                    </div>

                    <button
                        type="button"
                        onClick={() => {
                            setLoginError("");
                            setFlipped(true);
                        }}
                        className="flip-toggle-btn"
                    >
                        Create free account <Zap size={14} />
                    </button>

                    <p className="flip-footer-note">
                        <Sparkles size={11} /> AI-powered · GitHub-integrated · Free forever
                    </p>
                </div>

                {/* ─── BACK: Register ───────────────────────── */}
                <div className="flip-face flip-back">
                    {/* Glass header */}
                    <div className="flip-card-header">
                        <div className="flip-logo">
                            <span className="flip-logo-icon">
                                <Sparkles size={18} />
                            </span>
                            <span>CodePilot AI</span>
                        </div>
                        <div className="flip-header-badges">
                            <span className="flip-badge">
                                <GitBranch size={13} /> GitHub
                            </span>
                            <span className="flip-badge">
                                <Bot size={13} /> Gemini
                            </span>
                        </div>
                    </div>

                    {/* Hero text */}
                    <div className="flip-card-hero">
                        <h1 className="flip-title">Create account</h1>
                        <p className="flip-subtitle">Free forever — no credit card required</p>
                    </div>

                    {/* Error */}
                    {regError && (
                        <div className="flip-error">
                            <AlertCircle size={14} />
                            {regError}
                        </div>
                    )}

                    <form onSubmit={handleRegister} className="flip-form">
                        {/* Name */}
                        <div className="flip-field">
                            <span className="flip-field-icon">
                                <User size={15} />
                            </span>
                            <input
                                type="text"
                                autoComplete="name"
                                required
                                placeholder="Full name"
                                value={regName}
                                onChange={(e) => setRegName(e.target.value)}
                                className="flip-input"
                            />
                        </div>

                        {/* Email */}
                        <div className="flip-field">
                            <span className="flip-field-icon">
                                <Mail size={15} />
                            </span>
                            <input
                                type="email"
                                autoComplete="email"
                                required
                                placeholder="Email address"
                                value={regEmail}
                                onChange={(e) => setRegEmail(e.target.value)}
                                className="flip-input"
                            />
                        </div>

                        {/* Password */}
                        <div className="flip-field">
                            <span className="flip-field-icon">
                                <Lock size={15} />
                            </span>
                            <input
                                type={showRegPass ? "text" : "password"}
                                autoComplete="new-password"
                                required
                                placeholder="Password (min 8 chars)"
                                value={regPass}
                                onChange={(e) => setRegPass(e.target.value)}
                                className="flip-input flip-input-pw"
                            />
                            <button
                                type="button"
                                onClick={() => setShowRegPass((s) => !s)}
                                className="flip-pw-toggle"
                                tabIndex={-1}
                            >
                                {showRegPass ? <EyeOff size={15} /> : <Eye size={15} />}
                            </button>
                        </div>
                        {regPass.length > 0 && (
                            <p className="flip-pw-hint">
                                {regPass.length < 8
                                    ? `${8 - regPass.length} more character${8 - regPass.length === 1 ? "" : "s"} required`
                                    : "✓ Strong enough"}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={regLoading}
                            className="flip-submit-btn"
                        >
                            {regLoading ? (
                                <>
                                    <Loader2 size={15} className="animate-spin" /> Creating…
                                </>
                            ) : (
                                <>
                                    Create account <ArrowRight size={15} />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="flip-divider">
                        <span>Already have an account?</span>
                    </div>

                    <button
                        type="button"
                        onClick={() => {
                            setRegError("");
                            setFlipped(false);
                        }}
                        className="flip-toggle-btn"
                    >
                        Sign in instead <Zap size={14} />
                    </button>

                    <p className="flip-footer-note">
                        <Sparkles size={11} /> AI-powered · GitHub-integrated · Free forever
                    </p>
                </div>
            </div>
        </div>
    );
}
