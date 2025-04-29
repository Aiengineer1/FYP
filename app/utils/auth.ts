export interface UserData {
    user_id: number
    email: string
    name: string
    mall_id: number | null
    created_at: string
}

export interface LoginResponse {
    access_token: string
    token_type: string
    user_id: number
    email: string
    name: string
    mall_id: number | null
    created_at: string
}

export const getAuthToken = (): string | null => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem("token")
    }
    return null
}

export const getUserData = (): UserData | null => {
    if (typeof window !== 'undefined') {
        const userData = localStorage.getItem("user")
        return userData ? JSON.parse(userData) : null
    }
    return null
}

export const isAuthenticated = (): boolean => {
    return !!getAuthToken()
}

export const clearAuth = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
    }
}

export const getAuthHeaders = () => {
    const token = getAuthToken()
    return {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
    }
}

export const handleLoginResponse = (data: LoginResponse) => {
    localStorage.setItem("token", data.access_token)
    localStorage.setItem("user", JSON.stringify({
        user_id: data.user_id,
        email: data.email,
        name: data.name,
        mall_id: data.mall_id,
        created_at: data.created_at
    }))
} 