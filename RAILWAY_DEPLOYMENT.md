# Railway Deployment Guide - Work Tracker App

## 🎯 What You'll Get
- **Permanent public URL** that works 24/7
- **No need to keep your computer on**
- **Automatic HTTPS** for secure access
- **Free tier available** (500 hours/month)

## 📋 Prerequisites
- GitHub account (free)
- Railway account (free tier available)
- 10 minutes of your time

## 🚀 Step-by-Step Deployment

### Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in top-right → **"New repository"**
3. Repository name: `work-tracker-app`
4. Set to **Private** (recommended)
5. **DON'T** check "Add README", ".gitignore", or "license"
6. Click **"Create repository"**

### Step 2: Upload Code to GitHub

**Option A: Using GitHub Web Interface (Easiest)**

1. In your new repo, click **"uploading an existing file"**
2. Open this folder in Finder: `/Users/mina_ibrahim/.iclaw/conversations/users/system_default_user/2026/09/07/iclawcore-temp-31326486/work-tracker-app`
3. **Select ALL files** (Command+A)
4. **Drag them** to the GitHub upload area
5. Click **"Commit changes"**

**Option B: Using Git Command Line**

```bash
cd /Users/mina_ibrahim/.iclaw/conversations/users/system_default_user/2026/09/07/iclawcore-temp-31326486/work-tracker-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/work-tracker-app.git
git push -u origin main
```

### Step 3: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Sign up"** → **"Sign in with GitHub"**
3. Authorize Railway to access your GitHub

4. Click **"New Project"**
5. Select **"Deploy from GitHub repo"**
6. Choose your `work-tracker-app` repository
7. Railway will auto-detect it's a Python app

8. **Configure Environment Variables:**
   - Click on your service
   - Go to **"Variables"** tab
   - Add these variables:
     - `SECRET_KEY`: Any random string (e.g., `my-secret-key-12345`)
     - `PORT`: `5000`

9. Wait for deployment (takes ~2-3 minutes)

### Step 4: Get Your Public URL

1. In your Railway project dashboard
2. Click on your app service
3. Go to the **"Settings"** tab
4. Scroll to **"Networking"** section
5. Click **"Generate Domain"**
6. You'll get a URL like: `work-tracker.up.railway.app`

**This is your permanent public link!**

### Step 5: Share with Colleagues

Send them the Railway URL (e.g., `https://work-tracker.up.railway.app`)

They can:
- Access it from anywhere (no firewall issues)
- Log in with their @trip.com email
- Each person gets their own private data
- Works 24/7 even when you're offline

## 💰 Railway Pricing

- **Free tier**: $5/month credit (enough for this app)
- **Usage**: ~$3-5/month for light usage
- **No credit card required** for free tier
- **Upgrade anytime** if needed

## 🔧 Troubleshooting

**App won't start?**
- Check Railway logs in the dashboard
- Make sure all files are uploaded (especially `requirements.txt`)
- Verify environment variables are set

**Can't access the URL?**
- Wait 1-2 minutes after deployment
- Check that the domain is generated in Settings → Networking
- Try accessing in incognito mode

**Database issues?**
- Railway uses ephemeral storage by default
- For persistent data, add PostgreSQL:
  - Click **"New"** → **"Database"** → **"PostgreSQL"**
  - Railway will automatically link it to your app

## 📊 Monitoring

- View logs in Railway dashboard
- Monitor resource usage
- Scale up if needed (more resources = more cost)

## 🔄 Updating the App

To update your deployed app:

1. Make changes locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Railway will auto-redeploy

## 🎉 You're Done!

Your Work Tracker is now live on the internet with a permanent URL. Share it with your colleagues and start tracking work together!
