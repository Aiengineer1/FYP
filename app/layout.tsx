import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/toaster"
import { SWRConfig } from 'swr'
import ErrorBoundary from "@/components/error-boundary"
import { AuthInitializer } from "@/components/auth-initializer"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "InsightCart - Mall Analytics Platform",
  description: "AI-powered retail analytics and customer behavior monitoring system",
}

// SWR configuration (without event handlers for server component compatibility)
const swrConfig = {
  refreshInterval: 30000,
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  errorRetryCount: 3,
  errorRetryInterval: 5000,
  dedupingInterval: 10000,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ErrorBoundary>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <SWRConfig value={swrConfig}>
              <AuthInitializer />
              {children}
            </SWRConfig>
            <Toaster />
          </ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}



import './globals.css'