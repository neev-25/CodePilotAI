import api from "./api";

export interface AuthUser {
    id: number;
    name: string;
    email: string;
    created_at: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    user: AuthUser;
}

export async function registerUser(
    name: string,
    email: string,
    password: string
): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/register", {
        name,
        email,
        password,
    });
    return data;
}

export async function loginUser(
    email: string,
    password: string
): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/login", {
        email,
        password,
    });
    return data;
}
