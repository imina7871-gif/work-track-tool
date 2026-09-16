# Work Tracker — Deployment Guide

This guide explains how to deploy the Work Tracker app with Lark OAuth so your colleagues can access it with their own private workspaces.

---

## Overview

The Work Tracker now supports **multi-user access** with **Lark OAuth authentication**. Each colleague:
- Logs in with their Lark account
- Gets their own private workspace (tasks, reports, presentations)
- Cannot see other users' data
- Has the same full features as the original app

---

## Step 1: Create a Lark App

1. Go to [Lark Open Platform](https://open.larksuite.com) (or https://open.feishu.cn for China)
2. Click **"Create App"** → Select **"Enterprise Internal App"**
3. Fill in:
   - **App Name:** Work Tracker
   - **Description:** Daily work logging and presentation generator
   - **Icon:** Upload any icon (optional)
4. Click **"Create"**

---

## Step 2: Configure Permissions

1. In your app dashboard, go to **"Permissions"** (left sidebar)
2. Search for and enable:
   - `authen:user_info` — Read user basic info
   - `contact:user.base:readonly` — Read user profile (optional, for avatar)
3. Click **"Bulk Open"** or enable each individually
4. Go to **"Version & Release"** → **"Create Version"** → Submit for approval
5. Wait for admin approval (usually instant for internal apps)

---

## Step 3: Configure OAuth Redirect URL

1. In your app dashboard, go to **"App Configuration"** → **"Security"**
2. Find **"Redirect URLs"** or **"Callback URLs"**
3. Add your callback URL:
   - **Local testing:** `http://localhost:5000/auth/lark/callback`
   - **Production:** `https://your-domain.com/auth/lark/callback`
4. Save

---

## Step 4: Get Credentials

1. In your app dashboard, go to **"App Configuration"** → **"Basic Information"**
2. Copy:
   - **App ID** (looks like: `cli_xxxxxxxxxxxxx`)
   - **App Secret** (long string)
3. Keep these secure — never commit to git or share publicly

---

## Step 5: Configure Environment Variables

Edit the launcher script (`Work Tracker.command` on Desktop):

```bash
#!/bin/zsh
cd "/path/to/work-tracker-app"

# Set your Lark credentials
export LARK_APP_ID="cli_xxxxxxxxxxxxx"
export LARK_APP_SECRET="your_app_secret_here"
export LARK_CALLBACK_URL="http://localhost:5000/auth/lark/callback"
export SECRET_KEY="random-secret-key-here"

python3 web_app.py
```

**For production deployment**, set these as environment variables on your server:

```bash
export LARK_APP_ID="cli_xxxxxxxxxxxxx"
export LARK_APP_SECRET="your_app_secret_here"
export LARK_CALLBACK_URL="https://your-domain.com/auth/lark/callback"
export SECRET_KEY="random-secret-key-here"
```

---

## Step 6: Test Locally

1. Double-click `Work Tracker.command` on Desktop
2. Browser opens to login page
3. Click **"Sign in with Lark"**
4. Authorize the app
5. You should be redirected to the dashboard

---

## Step 7: Deploy for Colleagues

### Option A: Local Network (Simple)

If all colleagues are on the same office network:

1. Find your computer's local IP:
   ```bash
   ipconfig getifaddr en0
   # Example: 192.168.1.100
   ```

2. Update the callback URL in Lark app:
   ```
   http://192.168.1.100:5000/auth/lark/callback
   ```

3. Update the launcher script:
   ```bash
   export LARK_CALLBACK_URL="http://192.168.1.100:5000/auth/lark/callback"
   ```

4. Start the app and share the link:
   ```
   http://192.168.1.100:5000
   ```

5. Colleagues can access from their browsers on the same network

### Option B: Cloud Deployment (Recommended)

For remote access or larger teams:

**Using Railway/Render/Heroku:**

1. Create a `requirements.txt`:
   ```
   flask==3.0.0
   flask-session==0.5.0
   requests==2.31.0
   openai==1.3.0
   ```

2. Create a `Procfile`:
   ```
   web: python web_app.py
   ```

3. Deploy to your preferred platform

4. Update Lark callback URL to your production domain

5. Share the public URL with colleagues

**Using a VPS (DigitalOcean, AWS, etc.):**

1. Set up a server with Python 3.10+
2. Clone/copy the app
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables
5. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
   ```
6. Set up Nginx reverse proxy with SSL
7. Update Lark callback URL to your domain

---

## Step 8: Share with Colleagues

Once deployed, share:

1. **The URL:** `https://your-domain.com` or `http://your-ip:5000`
2. **Instructions:**
   - Click "Sign in with Lark"
   - Authorize the app
   - Start logging tasks
3. **Privacy assurance:** Each user sees only their own data

---

## Data Isolation

The app ensures complete privacy:

- **Database:** All tasks have a `user_id` column
- **Queries:** Every API call filters by `session['user_id']`
- **Reports:** Weekly reports only include the logged-in user's tasks
- **Sessions:** Flask sessions are encrypted with `SECRET_KEY`

**Example:** When User A generates a weekly report, they only see User A's tasks — never User B's.

---

## Troubleshooting

### "Invalid OAuth state" error
- Clear browser cookies and try again
- Ensure `SECRET_KEY` is set consistently

### "Failed to get access token" error
- Check Lark App ID and Secret are correct
- Verify callback URL matches exactly (including http/https)
- Ensure app permissions are approved

### User sees no tasks after login
- This is expected — each user starts with a clean workspace
- Tasks are isolated per user

### App not accessible from other computers
- Check firewall settings
- Ensure you're using the correct IP address
- For cloud deployment, check security groups/firewall rules

---

## Security Notes

1. **Never commit credentials** — Keep `LARK_APP_SECRET` and `SECRET_KEY` out of git
2. **Use HTTPS in production** — Lark requires HTTPS for callback URLs in production
3. **Rotate secrets periodically** — Update Lark App Secret and SECRET_KEY every few months
4. **Monitor usage** — Check Lark app dashboard for unusual activity

---

## Support

For issues:
- Check Lark Open Platform documentation: https://open.larksuite.com/docs
- Review Flask session docs: https://flask.palletsprojects.com/en/3.0.x/
- Check app logs for error messages

---

## Quick Start Checklist

- [ ] Created Lark app
- [ ] Enabled permissions (`authen:user_info`)
- [ ] Added callback URL
- [ ] Copied App ID and Secret
- [ ] Set environment variables
- [ ] Tested login locally
- [ ] Deployed to network or cloud
- [ ] Shared URL with colleagues
- [ ] Verified each user sees only their own data
