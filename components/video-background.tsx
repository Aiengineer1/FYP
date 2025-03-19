export default function VideoBackground() {
  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden">
      <div className="absolute inset-0 bg-black/40 z-10" />
      <video autoPlay muted loop playsInline className="w-full h-full object-cover">
        <source
          src="https://assets.mixkit.co/videos/preview/mixkit-people-walking-in-a-shopping-mall-4347-large.mp4"
          type="video/mp4"
        />
        Your browser does not support the video tag.
      </video>
    </div>
  )
}

