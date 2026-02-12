# Pavishna Global Service - Admin Panel

## 🌍 Features
- Client Management (CRUD)
- Interview, Visa, Medical Tracking
- Gulf Process (MOFA/VFS/Takamual)
- Payment Tracking (Advance & Full)
- Reports & Analytics
- Export to Excel/CSV

## 🚀 Local Development

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd pavishna-global-service

# Install dependencies
pip install -r requirements.txt

# Run locally (uses SQLite)
python app.py
```

### Access
- URL: http://localhost:5001
- Login: admin / admin123

## ☁️ Deploy to Render

### Method 1: One-Click Deploy
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repo
5. Render will auto-detect `render.yaml` and deploy

### Method 2: Manual Deploy
1. **Create PostgreSQL Database:**
   - Render Dashboard → New → PostgreSQL
   - Name: `pavishna-db`
   - Plan: Free
   - Copy the "External Database URL"

2. **Create Web Service:**
   - Render Dashboard → New → Web Service
   - Connect GitHub repo
   - Settings:
     - Name: `pavishna-global-service`
     - Environment: Python 3
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

3. **Add Environment Variables:**
   - `DATABASE_URL`: (paste PostgreSQL connection string)
   - `SECRET_KEY`: (generate random string)
   - `FLASK_DEBUG`: false

### After Deployment
- Access: `https://pavishna-global-service.onrender.com`
- Login: admin / admin123
- Change password immediately!

## 📁 Project Structure
```
pavishna-global-service/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── Procfile              # Process file for Render
├── .gitignore            # Git ignore rules
└── templates/
    ├── login.html        # Login page
    └── dashboard.html    # Main dashboard
```

## 🔧 Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | SQLite (local) |
| SECRET_KEY | Session secret | Auto-generated |
| PORT | Server port | 5001 |
| FLASK_DEBUG | Debug mode | true (local) |

## 📝 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /login | GET/POST | Login page |
| /dashboard | GET | Main dashboard |
| /api/clients | GET/POST | List/Add clients |
| /api/clients/:id | GET/PUT/DELETE | Client operations |
| /api/stats | GET | Dashboard statistics |
| /health | GET | Health check |

## ⚡ Performance Tips
- Render free tier may sleep after 15 mins inactivity
- First request after sleep takes ~30 seconds
- Upgrade to paid plan for always-on service

## 🔐 Security Notes
- Change default admin password immediately
- Use strong SECRET_KEY in production
- Enable HTTPS (automatic on Render)

## 📞 Support
For issues or questions, contact the developer.
