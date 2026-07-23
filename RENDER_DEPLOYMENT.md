# Render Deployment Guide

This guide explains how to deploy the Django application to Render.

## Prerequisites

- A GitHub repository with the project code
- A Render account (free tier available)

## Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub account

### Step 3: Deploy to Render

**Option A: Using render.yaml (Recommended)**

1. In Render dashboard, click **New +**
2. Select **Web Service**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and pre-fill configuration
5. Click **Deploy**

**Option B: Manual Configuration**

1. In Render dashboard, click **New +**
2. Select **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: django-starter (or your preferred name)
   - **Region**: Choose nearest to your users
   - **Branch**: main
   - **Runtime**: Docker
   - **Build Command**: (leave empty, Dockerfile handles this)
   - **Start Command**: (leave empty, Dockerfile handles this)

### Step 4: Add Environment Variables

Go to your web service → **Settings** → **Environment Variables** and add:

**Required:**
- `DJANGO_SETTINGS_MODULE` = `config.settings.prod`
- `DEBUG` = `False`
- `ALLOWED_HOSTS` = `your-app-name.onrender.com` (replace with your actual Render URL)

**For Email (Optional):**
- `EMAIL_BACKEND` = `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_PORT` = `587`
- `EMAIL_USE_TLS` = `True`
- `EMAIL_HOST_USER` = `your-gmail@gmail.com`
- `EMAIL_HOST_PASSWORD` = `your-gmail-app-password`
- `DEFAULT_FROM_EMAIL` = `your-gmail@gmail.com`
- `SERVER_EMAIL` = `your-gmail@gmail.com`

### Step 5: Database Setup

**Option A: Render PostgreSQL (Recommended)**

1. In Render dashboard, click **New +**
2. Select **PostgreSQL**
3. Choose a plan (Free tier available)
4. Create database
5. Render will automatically add `DATABASE_URL` to your web service

**Option B: SQLite**

If you don't add a PostgreSQL database, the app will use SQLite by default. This works on Render since it provides persistent storage.

### Step 6: Run Migrations

After deployment, you need to run database migrations:

1. Go to your web service → **Shell**
2. Click **Open Shell**
3. Run:
   ```bash
   python manage.py migrate
   ```

### Step 7: Create Superuser (Optional)

To create an admin user:

1. Go to your web service → **Shell**
2. Click **Open Shell**
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow the prompts

### Step 8: Test Deployment

1. Visit your Render URL (e.g., `https://django-starter.onrender.com`)
2. Test login with your superuser credentials
3. Test password change functionality
4. If email is configured, test signup/password reset

## Troubleshooting

**Build fails:**
- Check the build logs in Render dashboard
- Ensure `render.yaml` is in the repository root
- Verify Dockerfile syntax

**Static files not loading:**
- Ensure `collectstatic` ran during build
- Check `DJANGO_VITE` settings in production

**Database errors:**
- Verify `DATABASE_URL` is set (if using PostgreSQL)
- For SQLite, ensure migrations have been run

**Email not working:**
- Verify Gmail App Password (not regular password)
- Check email environment variables are set correctly

## Advantages of Render vs Vercel

- **Persistent storage**: Render supports SQLite, Vercel doesn't
- **Simpler setup**: No serverless function complexity
- **Better Django support**: Render is optimized for Django
- **Free PostgreSQL**: Render offers free PostgreSQL database

## Monitoring

- View logs in Render dashboard under **Logs**
- Monitor performance under **Metrics**
- Set up alerts in **Settings** → **Alerts**
