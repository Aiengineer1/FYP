import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    user_id: number
    name: string
    email: string
    mall_id: number | null
}

interface AuthState {
    // State
    isAuthenticated: boolean
    user: User | null
    token: string | null
    isLoading: boolean

    // Actions
    login: (token: string, user: User) => void
    logout: () => void
    setLoading: (loading: boolean) => void
    updateUser: (user: Partial<User>) => void
    setMallId: (mallId: number | null) => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            // Initial state
            isAuthenticated: false,
            user: null,
            token: null,
            isLoading: false,

            // Actions
            login: (token: string, user: User) => {
                // Store in localStorage and cookies for compatibility with existing code
                if (typeof window !== 'undefined') {
                    localStorage.setItem('token', token)
                    localStorage.setItem('user', JSON.stringify(user))
                    document.cookie = `token=${token}; path=/; max-age=86400; SameSite=Lax`
                    document.cookie = `user=${JSON.stringify(user)}; path=/; max-age=86400; SameSite=Lax`
                }

                set({
                    isAuthenticated: true,
                    user,
                    token,
                    isLoading: false,
                })
            },

            logout: () => {
                // Clear localStorage
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('token')
                    localStorage.removeItem('user')
                    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT'
                    document.cookie = 'user=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT'
                }

                set({
                    isAuthenticated: false,
                    user: null,
                    token: null,
                    isLoading: false,
                })
            },

            setLoading: (loading: boolean) => {
                set({ isLoading: loading })
            },

            updateUser: (userData: Partial<User>) => {
                const currentUser = get().user
                if (currentUser) {
                    const updatedUser = { ...currentUser, ...userData }

                    // Update localStorage and cookies for compatibility
                    if (typeof window !== 'undefined') {
                        localStorage.setItem('user', JSON.stringify(updatedUser))
                        document.cookie = `user=${JSON.stringify(updatedUser)}; path=/; max-age=86400; SameSite=Lax`
                    }

                    set({ user: updatedUser })
                }
            },

            setMallId: (mallId: number | null) => {
                const currentUser = get().user
                if (currentUser) {
                    const updatedUser = { ...currentUser, mall_id: mallId }

                    // Update localStorage and cookies for compatibility
                    if (typeof window !== 'undefined') {
                        localStorage.setItem('user', JSON.stringify(updatedUser))
                        document.cookie = `user=${JSON.stringify(updatedUser)}; path=/; max-age=86400; SameSite=Lax`
                    }

                    set({ user: updatedUser })
                }
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                isAuthenticated: state.isAuthenticated,
                user: state.user,
                token: state.token,
            }),
        }
    )
)

// Helper function to initialize auth state from localStorage
export const initializeAuthFromStorage = () => {
    if (typeof window === 'undefined') return

    const token = localStorage.getItem('token')
    const userString = localStorage.getItem('user')

    if (token && userString) {
        try {
            const user = JSON.parse(userString)
            useAuthStore.getState().login(token, user)
        } catch (error) {
            console.error('Error parsing user data from localStorage:', error)
            useAuthStore.getState().logout()
        }
    }
} 