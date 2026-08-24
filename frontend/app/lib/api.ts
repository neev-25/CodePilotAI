import axios from "axios";

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    timeout: 60_000,
});

// Attach stored JWT token to every request
api.interceptors.request.use(async (config) => {
    let token = null;

    if (typeof window !== "undefined") {
        token = localStorage.getItem("codepilot-token");
    } else {
        try {
            const { cookies } = await import("next/headers");
            const cookieStore = await cookies();
            token = cookieStore.get("codepilot-token")?.value;
        } catch (err) {
            // next/headers might not be available
        }
    }

    if (token) {
        config.headers = config.headers ?? {};
        config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
});

export default api;
