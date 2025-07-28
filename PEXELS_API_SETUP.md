# 🎥 Pexels API Setup for Mall Person Tracking Videos

## 🚀 **Quick Setup Guide**

### 1. **Get Your Free Pexels API Key**

1. Go to [https://www.pexels.com/api/](https://www.pexels.com/api/)
2. Click "Get Started" or "Sign Up"
3. Create a free account
4. Get your API key from the dashboard

### 2. **Add API Key to Environment**

Create a `.env.local` file in your project root:

```bash
# .env.local
NEXT_PUBLIC_PEXELS_API_KEY=YOUR_ACTUAL_PEXELS_API_KEY_HERE
```

### 3. **Restart Your Development Server**

```bash
npm run dev
# or
yarn dev
```

---

## 🎯 **What This Does**

The VideoBackground component now:

- ✅ **Fetches real mall videos** from Pexels API
- ✅ **Searches for "mall people walking"** videos
- ✅ **Has multiple fallback options** if API fails
- ✅ **Shows loading state** while fetching
- ✅ **Displays error indicator** if using fallback

---

## 🔧 **API Features**

### **Search Query**: `mall people walking`
- Returns videos of people walking in malls
- Perfect for person tracking demonstrations
- High-quality, free-to-use videos

### **Fallback Videos**:
1. Vimeo mall video
2. Mixkit shopping mall video  
3. Videezy sample video
4. Unsplash mall image (final fallback)

---

## 🛠️ **Troubleshooting**

### **If API Key Doesn't Work:**
1. Check if API key is correct
2. Verify `.env.local` file exists
3. Restart development server
4. Check browser console for errors

### **If No Videos Load:**
- Component will automatically use fallback videos
- Yellow indicator shows "Using Fallback Video"
- All functionality still works

### **Rate Limiting:**
- Pexels free tier: 200 requests/hour
- Component caches results
- Fallback videos prevent issues

---

## 🎨 **Customization Options**

### **Change Search Query:**
```typescript
// In video-background.tsx, line ~30
const response = await fetch('https://api.pexels.com/videos/search?query=YOUR_QUERY&per_page=1', {
```

**Popular Queries:**
- `mall people walking`
- `shopping center crowd`
- `retail store customers`
- `surveillance footage`
- `people tracking`

### **Add More Fallback Videos:**
```typescript
const fallbackVideos = [
  "your-video-url-1",
  "your-video-url-2",
  "your-video-url-3"
]
```

---

## 📱 **Mobile Optimization**

- Videos are responsive
- Auto-play with mute (mobile-friendly)
- Fallback images for slow connections
- Optimized loading states

---

## 🔒 **Privacy & Licensing**

- ✅ All Pexels videos are free to use
- ✅ No attribution required
- ✅ Commercial use allowed
- ✅ No privacy concerns (public videos)

---

## 🚀 **Ready to Use!**

Once you add your Pexels API key, your homepage will show:

1. **Real mall videos** from Pexels API
2. **Live analytics overlay** with tracking simulation
3. **Professional appearance** with loading states
4. **Reliable fallbacks** if anything fails

**Your mall person tracking video background is now ready!** 🎉 