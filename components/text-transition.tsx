"use client"

import { useState, useEffect } from "react"

const phrases = ["Retail Analytics", "Customer Insights", "Inventory Management", "Sales Forecasting", "Market Trends"]

export default function TextTransition() {
  const [index, setIndex] = useState(0)
  const [fadeIn, setFadeIn] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setFadeIn(false)

      setTimeout(() => {
        setIndex((prevIndex) => (prevIndex + 1) % phrases.length)
        setFadeIn(true)
      }, 500) // Wait for fade out animation
    }, 3000) // Change text every 3 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <span className={`transition-opacity duration-500 ${fadeIn ? "opacity-100" : "opacity-0"}`}>{phrases[index]}</span>
  )
}

