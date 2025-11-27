# 🚀 PACCS DEPLOYMENT GUIDE
## How to Put Your Billion Dollar App Online

---

## OVERVIEW

This guide covers:
1. Preparing your code for deployment
2. Hosting on Railway.app (easiest option)
3. Connecting to your Wix website (peekaboon.com)
4. Setting up payments with Stripe
5. Going live and monetizing

---

## STEP 1: PREPARE YOUR FILES

Make sure you have these files in your `peekaboon-paccs` folder:

```
peekaboon-paccs/
├── app.py                    # Main Flask application
├── agents.py                 # AI agents (ultimate version)
├── consensus.py              # Consensus protocol
├── database.py               # Film database
├── auth.py                   # User authentication
├── pdf_generator.py          # PDF report generator
├── report_generator.py       # Report generator
├── requirements.txt          # Dependencies (create this)
├── Procfile                  # For hosting (create this)
├── FilmFreeway-Submissions-*.csv  # Your film data
├── templates/
│   ├── index.html            # Main interface
│   ├── signup.html           # Signup page
│   ├── login.html            # Login page
│   ├── dashboard.html        # User dashboard
│   └── landing.html          # Landing page
└── paccs_users.json          # User database (auto-created)
```

---

## STEP 2: CREATE REQUIRED FILES

### Create requirements.txt
In VS Code, create a new file called `requirements.txt` with:

```
flask==3.0.0
pandas==2.1.0
numpy==1.26.0
gunicorn==21.2.0
```

### Create Procfile
Create a file called `Procfile` (no extension) with:

```
web: gunicorn app:app
```

### Create runtime.txt
Create a file called `runtime.txt` with:

```
python-3.11.6
```

---

## STEP 3: SIGN UP FOR RAILWAY.APP

1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email
4. Free tier includes $5/month of free usage

---

## STEP 4: DEPLOY TO RAILWAY

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   # In Terminal, in your peekaboon-paccs folder:
   git init
   git add .
   git commit -m "Initial PACCS deployment"
   
   # Create a new repo on github.com, then:
   git remote add origin https://github.com/YOUR_USERNAME/paccs.git
   git push -u origin main
   ```

2. **Connect Railway to GitHub:**
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your paccs repository
   - Railway will automatically deploy!

### Option B: Deploy via Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   cd ~/Desktop/peekaboon-paccs
   railway login
   railway init
   railway up
   ```

---

## STEP 5: GET YOUR APP URL

After deployment, Railway gives you a URL like:
```
https://paccs-production.up.railway.app
```

Test it by visiting the URL in your browser!

---

## STEP 6: CONNECT CUSTOM DOMAIN

### Set up app.peekaboon.com

1. **In Railway:**
   - Go to your project → Settings → Domains
   - Click "Add Custom Domain"
   - Enter: `app.peekaboon.com`
   - Railway shows you DNS records to add

2. **In your domain provider (where you bought peekaboon.com):**
   - Add a CNAME record:
     - Type: CNAME
     - Name: app
     - Value: (the Railway URL they gave you)

3. **Wait 5-30 minutes for DNS to propagate**

4. **Test:** Visit https://app.peekaboon.com

---

## STEP 7: CONNECT TO WIX (peekaboon.com)

### Option A: Embed with iFrame

In Wix Editor:
1. Add an HTML iFrame element
2. Set the source to: `https://app.peekaboon.com`
3. This embeds PACCS inside your Wix page

### Option B: Link Buttons (Recommended)

In Wix Editor:
1. Create a button: "Get Your Film Analyzed"
2. Set the link to: `https://app.peekaboon.com/signup`
3. This sends visitors to your PACCS app

### Option C: Full Integration

Add these links to your Wix navigation:
- "Analyze Film" → `https://app.peekaboon.com/analyze`
- "Sign Up" → `https://app.peekaboon.com/signup`
- "Login" → `https://app.peekaboon.com/login`
- "Pricing" → `https://app.peekaboon.com/pricing`

---

## STEP 8: SET UP STRIPE PAYMENTS

### Create Stripe Account

1. Go to https://stripe.com
2. Sign up for an account
3. Get your API keys from Dashboard → Developers → API Keys

### Add Stripe to PACCS

1. Install Stripe:
   Add to requirements.txt: `stripe==7.0.0`

2. Add your Stripe keys as Railway environment variables:
   - `STRIPE_SECRET_KEY=sk_live_xxx`
   - `STRIPE_PUBLISHABLE_KEY=pk_live_xxx`

3. The payment integration is already in app.py (api/purchase endpoint)

---

## STEP 9: PRICING SETUP

Recommended pricing tiers:

| Plan | Price | Credits | Target Customer |
|------|-------|---------|-----------------|
| Free | £0 | 3 | Try it out |
| Starter | £15 | 5 | Casual filmmakers |
| Professional | £35 | 15 | Serious filmmakers |
| Festival | £500/year | Unlimited | Film festivals |

---

## STEP 10: GO LIVE CHECKLIST

Before announcing:

- [ ] Test signup flow
- [ ] Test login flow
- [ ] Test film analysis
- [ ] Test PDF report download
- [ ] Test payment (use Stripe test mode first)
- [ ] Set up custom domain
- [ ] Connect Wix buttons
- [ ] Create social media posts
- [ ] Prepare email announcement

---

## QUICK COMMANDS REFERENCE

### Local Development
```bash
cd ~/Desktop/peekaboon-paccs
python3 app.py
# Visit http://localhost:5000
```

### Deploy to Railway
```bash
railway up
```

### View Logs
```bash
railway logs
```

### Environment Variables (set in Railway dashboard)
```
SECRET_KEY=your-secret-key-here
STRIPE_SECRET_KEY=sk_live_xxx
DATABASE_URL=your-database-url (if using external DB)
```

---

## TROUBLESHOOTING

### "Module not found"
→ Make sure requirements.txt has all dependencies

### "Port already in use"
→ Kill other processes: `lsof -ti:5000 | xargs kill`

### "Database not found"
→ Make sure FilmFreeway CSV is in the project folder

### DNS not working
→ Wait up to 48 hours, clear browser cache

---

## SUPPORT

- Railway docs: https://docs.railway.app
- Flask docs: https://flask.palletsprojects.com
- Stripe docs: https://stripe.com/docs

---

## 🎉 CONGRATULATIONS!

Once deployed, your PACCS platform will be live at:
- **Main app:** https://app.peekaboon.com
- **Signup:** https://app.peekaboon.com/signup
- **Analysis:** https://app.peekaboon.com/analyze

**You're ready to start monetizing!** 💰
