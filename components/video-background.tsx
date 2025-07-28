"use client"

import { useState, useEffect } from 'react'

export default function VideoBackground() {
  const [isLoading, setIsLoading] = useState(true)
  const [useAnimation, setUseAnimation] = useState(false)

  // Working mall person tracking videos
  const mallVideos = [
    "https://assets.mixkit.co/videos/preview/mixkit-people-walking-in-a-shopping-mall-4347-large.mp4",
    "https://player.vimeo.com/external/434045526.sd.mp4?s=c27eecc69a27dbc4ff2b87d38afc35f1a9e7c02d&profile_id=164&oauth2_token_id=57447761"
  ]

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
      // If videos don't work, use animation
      setTimeout(() => {
        setUseAnimation(true)
      }, 3000)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="absolute inset-0 w-full h-full overflow-hidden bg-gradient-to-br from-primary/20 via-secondary/20 to-accent/20">
        <div className="absolute inset-0 bg-black/30 z-10" />
        <div className="absolute inset-0 flex items-center justify-center z-20">
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p>Loading mall tracking video...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden">
      <div className="absolute inset-0 bg-black/30 z-10" />
      
      {/* Mall Background with Person Tracking Animation */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-secondary/20 to-accent/20">
        {/* Grid pattern for mall floor */}
        <div className="absolute inset-0 opacity-10">
          <div className="grid grid-cols-20 grid-rows-12 h-full">
            {Array.from({ length: 240 }).map((_, i) => (
              <div key={i} className="border border-white/20"></div>
            ))}
          </div>
        </div>
        
        {/* Moving people dots representing person tracking */}
        <div className="absolute inset-0">
          {/* Group 1 - Primary dots (active visitors) */}
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={`primary-${i}`}
              className="absolute w-4 h-4 bg-primary rounded-full animate-pulse shadow-lg"
              style={{
                left: `${15 + (i * 12)}%`,
                top: `${25 + (i * 8)}%`,
                animationDelay: `${i * 0.3}s`,
                animationDuration: '2s'
              }}
            />
          ))}
          
          {/* Group 2 - Secondary dots (tracked individuals) */}
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={`secondary-${i}`}
              className="absolute w-3 h-3 bg-secondary rounded-full animate-pulse shadow-lg"
              style={{
                left: `${55 + (i * 8)}%`,
                top: `${45 + (i * 6)}%`,
                animationDelay: `${i * 0.5}s`,
                animationDuration: '3s'
              }}
            />
          ))}
          
          {/* Group 3 - Accent dots (analytics data points) */}
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={`accent-${i}`}
              className="absolute w-5 h-5 bg-accent rounded-full animate-pulse shadow-lg"
              style={{
                left: `${35 + (i * 15)}%`,
                top: `${65 + (i * 5)}%`,
                animationDelay: `${i * 0.7}s`,
                animationDuration: '4s'
              }}
            />
          ))}
        </div>
        
        {/* Connection lines showing tracking relationships */}
        <svg className="absolute inset-0 w-full h-full">
          <defs>
            <linearGradient id="trackingLine" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="hsl(var(--primary))" />
              <stop offset="50%" stopColor="hsl(var(--secondary))" />
              <stop offset="100%" stopColor="hsl(var(--accent))" />
            </linearGradient>
          </defs>
          <line x1="20%" y1="30%" x2="60%" y2="50%" stroke="url(#trackingLine)" strokeWidth="2" opacity="0.7" />
          <line x1="50%" y1="70%" x2="80%" y2="55%" stroke="url(#trackingLine)" strokeWidth="2" opacity="0.7" />
          <line x1="35%" y1="45%" x2="55%" y2="75%" stroke="url(#trackingLine)" strokeWidth="2" opacity="0.7" />
          <line x1="25%" y1="40%" x2="45%" y2="60%" stroke="url(#trackingLine)" strokeWidth="2" opacity="0.7" />
        </svg>
        
        {/* Zone indicators */}
        <div className="absolute top-1/4 left-1/4 z-15">
          <div className="bg-primary/20 backdrop-blur-sm rounded-lg p-2 border border-primary/30">
            <div className="text-primary text-xs font-medium">Zone A: 8 visitors</div>
          </div>
        </div>
        
        <div className="absolute top-1/3 right-1/3 z-15">
          <div className="bg-secondary/20 backdrop-blur-sm rounded-lg p-2 border border-secondary/30">
            <div className="text-secondary text-xs font-medium">Zone B: 12 visitors</div>
          </div>
        </div>
        
        <div className="absolute bottom-1/3 right-1/4 z-15">
          <div className="bg-accent/20 backdrop-blur-sm rounded-lg p-2 border border-accent/30">
            <div className="text-accent text-xs font-medium">Zone C: 6 visitors</div>
          </div>
        </div>
      </div>
      
      {/* Analytics overlay with person tracking visualization */}
      <div className="absolute inset-0 z-20 flex items-center justify-center">
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 max-w-md mx-4 border border-white/20">
          <div className="text-white text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Live Person Tracking</h3>
            <p className="text-blue-100 text-sm mb-4">
              Real-time analytics and customer behavior insights
            </p>
            
            {/* Live stats simulation */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">24</div>
                <div className="text-xs text-gray-300">Active Visitors</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-secondary">156</div>
                <div className="text-xs text-gray-300">Today's Count</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-accent">89%</div>
                <div className="text-xs text-gray-300">Engagement</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Floating analytics elements */}
      <div className="absolute top-8 right-8 z-30">
        <div className="bg-primary/20 backdrop-blur-sm rounded-lg p-3 border border-primary/30">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <span className="text-primary text-sm font-medium">Live Tracking Active</span>
          </div>
        </div>
      </div>
      
      <div className="absolute bottom-8 left-8 z-30">
        <div className="bg-secondary/20 backdrop-blur-sm rounded-lg p-3 border border-secondary/30">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-secondary rounded-full animate-pulse"></div>
            <span className="text-secondary text-sm font-medium">AI Analytics Running</span>
          </div>
        </div>
      </div>
      
      {/* Person tracking status */}
      <div className="absolute top-8 left-8 z-30">
        <div className="bg-accent/20 backdrop-blur-sm rounded-lg p-3 border border-accent/30">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            <span className="text-accent text-sm font-medium">18 People Tracked</span>
          </div>
        </div>
      </div>
    </div>
  )
}

