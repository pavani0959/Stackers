<div align="center">

  <p><strong>Fashion that understands you. .</strong></p>
  <p>Built with React, FastAPI, SQLite, and Scikit-Learn.</p>
</div>

---

## 🚀 The Vision
Gen Z and Gen Alpha don't shop by categories like "shirts" or "pants"—they shop by **aesthetics, identity, and vibes**. 

**Myntra Identity** is a next-generation, AI-native shopping architecture that replaces static category browsing with a mathematical **Fashion DNA** model. We use Natural Language Processing (NLP), TF-IDF vectorization, and Cosine Similarity to completely personalize the e-commerce experience.

---

## ✨ 8 Killer Features (The Tech)

### 1. The Fashion DNA Engine (ML Clustering)
Users take a highly visual onboarding quiz. We don't just tag them; we use an ML algorithm to map their answers against Ground Truth aesthetic clusters, generating an exact mathematical DNA vector (e.g., *60% Minimalist, 30% Streetwear, 10% Y2K*).

### 2. Explainable AI Feed (Decision Intelligence)
The Home Feed is dynamically sorted by the Python backend based on the user's DNA vector. Clicking on a product reveals our **Confidence Score**, breaking down exactly *why* the AI recommended the item across 5 dimensions: Style, Occasion, Budget, Weather, and Wardrobe Compatibility.

### 3. Reverse Shopping (NLP Semantic Match)
Users don't search for items; they describe an event. By typing *"College fest, retro theme, ₹2000"*, our NLP pipeline extracts the intent, vectorizes the prompt, and searches the SQLite database to automatically construct a custom 3-piece outfit.

### 4. Steal Their Vibe (Creator Merging)
Gen Z shops via creators. We allow users to view a creator's Fashion DNA and use **Vector Addition** to mathematically merge a percentage of the creator's aesthetic into their own algorithmic profile, dynamically shifting their feed.

### 5. Wardrobe Twins (Community)
Using **Cosine Similarity**, our backend scans the database to find other real users who have a >90% match with your exact aesthetic, creating hyper-niche shopping tribes.

### 6. DNA Dynamic Pricing (Gamification)
To solve the e-commerce problem of high return rates, we financially incentivize authentic shopping. If the AI calculates that an item is a >90% match to your DNA, you automatically unlock a dynamic **15% DNA Discount**.

### 7. Anti-Trend Mode
Algorithmic echo chambers are boring. By flipping a toggle, the Python backend reverses its sorting algorithm, showing you items that are the exact mathematical opposite of your Fashion DNA to help you break out of your comfort zone.

### 8. Fashion Memory
A closed-loop system where every purchase is tracked with its ML Confidence Score and Date, proving that the algorithm learns from real purchasing behavior over time.

### 9. Voice-to-Outfit (Speech AI)
Typing is slow. We integrated the browser's native Speech Recognition API into our Reverse Shopping engine. Users can tap the microphone and speak their occasion (e.g., "I have a beach party in Goa this weekend"), and the app instantly transcribes and builds the outfit.

### 10. Myntra Muse (AI Stylist Chatbot)
A floating conversational AI widget that is context-aware. The chatbot reads the user's Fashion DNA and recent Purchase Memory to give hyper-personalized styling advice and insights directly in the chat window.

---

## 🛠️ Tech Stack
- **Frontend:** React, Vite, Vanilla CSS (Glassmorphism & Modern UI)
- **Backend:** Python, FastAPI, Uvicorn
- **Database:** SQLite, SQLAlchemy
- **Machine Learning:** `scikit-learn` (TF-IDF Vectorizer, Cosine Similarity, Vector Math)

---

## 💻 How to Run Locally

You need two terminals to run the Full-Stack application.

### 1. Start the Backend (Python ML API)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy scikit-learn
python seed.py  # Populates the SQLite database
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend (React App)
```bash
# In a new terminal window at the root directory
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser!

---

## 🏆 Business Value for Myntra
1. **Reduced Return Rates:** By using DNA Dynamic Pricing and Confidence Scores, users buy items they actually keep.
2. **Higher AOV (Average Order Value):** Reverse Shopping NLP bundles 3-piece outfits instead of single items.
3. **Community Retention:** Wardrobe Twins and Creator Merging turns Myntra from a utility app into a daily-use social network.

---

## Production foundation setup

### Environment

Copy the documented environment template before starting either service:

```bash
cp .env.example .env
```

`VITE_API_BASE_URL` is exposed to the frontend by Vite. `DATABASE_URL`,
`FRONTEND_ORIGINS`, and `ENVIRONMENT` are loaded by the FastAPI settings class.
For `FRONTEND_ORIGINS`, use a JSON list such as
`["http://localhost:5173"]`.

### Frontend commands

```bash
npm install
npm run lint
npm run test
npm run build
```

Install the Playwright Chromium binary once, then run the browser smoke test:

```bash
npm run test:e2e:install
npm run test:e2e
```

Run all frontend CI checks with:

```bash
npm run check
```

### Backend commands

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python seed.py
pytest --cov=. --cov-report=term-missing
uvicorn main:app --reload --port 8000
```

### Existing local SQLite database

The repository originally created tables with `Base.metadata.create_all()`. If your
local `backend/myntra.db` already contains the `products` and
`community_profiles` tables but has no `alembic_version` table, mark it at the
initial revision once instead of running the create-table migration:

```bash
cd backend
source venv/bin/activate
alembic stamp head
```

After that one-time stamp, use `alembic upgrade head` normally for every future
migration.
