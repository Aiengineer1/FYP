"use client"

import { useEffect } from 'react'
import { useAuthStore, initializeAuthFromStorage } from '@/stores/auth-store'
import { apiClient } from '@/lib/api-client'
import { logConfiguration } from '@/lib/config'

export function AuthInitializer() {
    const { token, isAuthenticated, logout, setLoading } = useAuthStore()

    useEffect(() => {
        const initializeAuth = async () => {
            try {
                setLoading(true)

                // Log configuration and validate environment variables
                logConfiguration()

                // Initialize auth state from localStorage
                initializeAuthFromStorage()

                // If we have a token, verify it with the backend
                if (token && isAuthenticated) {
                    try {
                        await apiClient.verifyToken()
                        console.log('Token verified successfully')
                    } catch (error) {
                        console.error('Token verification failed:', error)
                        logout()
                    }
                }
            } catch (error) {
                console.error('Auth initialization error:', error)
            } finally {
                setLoading(false)
            }
        }

        initializeAuth()
    }, []) // Only run on mount

    // This component doesn't render anything
    return null
} 