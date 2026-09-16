# Railway Deployment Guide

## Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click **"New repository"**
3. Name it: `work-tracker-app`
4. Set to **Private** (recommended)
5. Click **"Create repository"**

## Step 2: Upload Your App to GitHub

### Option A: Using GitHub Web Interface (Easiest)

1. In your new repo, click **"uploading an existing file"**
2. **Zip the entire `work-tracker-app` folder**
3. Drag the zip file to GitHub
4. Extract it (GitHub will extract automatically)
5. Commit the files

### Option B: Using Git Command Line

```bash
cd /Users/mina_ibrahim/.iclaw/conversations/users/system_default_user/2026/09/07/iclawcore-temp-31326486/work-tracker-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/work-tracker-app.git
git push -u origin main
```

## Step 3: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Sign up"** → **"Sign in with GitHub"**
3. Authorize Railway to access your GitHub

4. Click **"New Project"**
5. Select **"Deploy from GitHub repo"**
6. Choose your `work-tracker-app` repository
7. Railway will auto-detect it's a Python app

8. Wait for deployment (takes ~2-3 minutes)

## Step 4: Get Your Public URL

1. In your Railway project dashboard
2. Click on your app service
3. Go to the **"Settings"** tab
4. Scroll to **"Networking"** section
5. Click **"Generate Domain"**
6. You'll get a URL like: `work-tracker.up.railway.app`

**This is your public link!** Share it with colleagues.

## Step 5: Share with Colleagues

Send them the Railway URL (e.g., `https://work-tracker.up.railway.app`)

They can:
- Access it from anywhere (no firewall issues)
- Log in with their @trip.com email
- Each person gets their own private data

## Important Notes

- **Free tier**: Railway gives you $5/month free credit (enough for this app)
- **Database**: The SQLite database is stored in Railway's ephemeral filesystem
  - Data persists during deployment but may reset on redeploy
  - For production, consider migrating to PostgreSQL (Railway supports it)
- **Settings**: OpenAI API key is stored in `settings.json` (not in git)
  - Each deployment starts fresh
  - Users can configure it in the Settings tab

## Troubleshooting

**App won't start?**
- Check Railway logs in the dashboard
- Make sure all files are uploaded (especially `requirements.txt`)

**Can't access the URL?**
- Wait 1-2 minutes after deployment
- Check that the domain is generated in Settings → Networking

**Need to update the app?**
- Push changes to GitHub
- Railway will auto-redeploy
