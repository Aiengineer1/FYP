import Navbar from "@/components/navbar"
import TextTransition from "@/components/text-transition"
import VideoBackground from "@/components/video-background"

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="flex flex-col md:flex-row min-h-[calc(100vh-64px)]">
        {/* Left side with transitioning text */}
        <div className="w-full md:w-1/2 flex flex-col justify-center items-start p-8 md:p-16 z-10">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            <TextTransition />
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-md">
            Unlock the power of data to transform your retail business and drive growth.
          </p>
          <div className="flex gap-4">
            <a
              href="#features"
              className="bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-3 rounded-md font-medium"
            >
              Learn More
            </a>
            <a
              href="/signup"
              className="bg-background border border-input hover:bg-accent hover:text-accent-foreground px-6 py-3 rounded-md font-medium"
            >
              Get Started
            </a>
          </div>
        </div>

        {/* Right side with video background */}
        <div className="w-full md:w-1/2 relative">
          <VideoBackground />
        </div>
      </div>
    </main>
  )
}

