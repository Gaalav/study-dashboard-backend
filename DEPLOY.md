# Study Dashboard Backend

## Deploy to Railway

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Push this backend folder to GitHub first

### Step 3: Add PostgreSQL Database
1. In Railway dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway auto-connects it via DATABASE_URL

### Step 4: Set Environment Variables
In Railway project settings, add:
```
SECRET_KEY=your-super-secret-key-here-make-it-long
DEBUG=False
CORS_ALLOW_ALL=True
RAILWAY_ENVIRONMENT=production
```

### Step 5: Deploy
Railway auto-deploys when you push to GitHub.

### Step 6: Create Admin User
In Railway terminal:
```
python manage.py createsuperuser
```

### Step 7: Seed Data
```
python manage.py seed_data
```

Your API will be at: `https://your-app.railway.app/api/`
