<div align="center">

# Myntra Identity

<p><strong>Fashion that understands you.</strong></p>

<p>Built with React, FastAPI, SQLite, SQLAlchemy, and Scikit-Learn.</p>

</div>

---

## 🚀 The Vision

Gen Z and Gen Alpha do not shop only through traditional categories such as shirts, pants, and shoes. They often shop through aesthetics, occasions, identity, creators, and personal style.

**Myntra Identity** is an AI-powered fashion decision platform designed to understand a user's preferences through a mathematical **Fashion DNA** profile.

Instead of displaying hundreds of generic products, the application uses Natural Language Processing, TF-IDF vectorization, cosine similarity, preference signals, and explainable recommendation scores to help users understand:

* what matches their personal style,
* what works for a specific occasion,
* what fits their budget,
* why a product was recommended,
* and how their fashion identity changes over time.

The goal is to transform fashion discovery from endless browsing into a more personal and confident decision-making experience.

---

## ✨ 10 Key Features

### 1. Fashion DNA Engine

Users complete a visual onboarding quiz based on aesthetic preferences, colours, occasions, silhouettes, and personal style signals.

The backend converts the selected signals into TF-IDF vectors and compares them with predefined aesthetic profiles using cosine similarity.

The similarities are normalized into a Fashion DNA profile such as:

```text
60% Minimalist
30% Streetwear
10% Y2K
```

This Fashion DNA becomes the foundation for the application's recommendation and personalization features.

---

### 2. Explainable AI Feed

The home feed is dynamically ranked by the FastAPI backend according to the user's Fashion DNA and preferences.

Instead of displaying only a generic “Recommended” label, each product receives a compatibility breakdown across dimensions such as:

```text
Style Match
Occasion Match
Budget Match
Weather Match
Wardrobe Compatibility
```

Users can inspect the score and understand why a product was selected for them.

---

### 3. Reverse Shopping

Traditional shopping begins with a product category.

Reverse Shopping begins with the user's real-life requirement.

A user can enter a prompt such as:

```text
College fest on Saturday, retro theme, total budget ₹2,000.
```

The backend processes the prompt, matches its terms against product names, tags, occasions, and aesthetic information, and generates complete outfit recommendations.

The long-term goal is to convert free-form fashion intent into structured information such as:

* occasion,
* theme,
* budget,
* dress code,
* preferred colours,
* location,
* and outfit requirements.

---

### 4. Steal Their Vibe

Users can explore creator profiles and view their Fashion DNA.

The application supports weighted vector blending, allowing a selected percentage of a creator's aesthetic vector to be merged with the user's existing Fashion DNA.

For example:

```text
Original user DNA: 70% Minimalist, 30% Streetwear
Creator blend: 40%
Result: A newly weighted Fashion DNA profile
```

This changes the recommendation feed while preserving part of the user's original identity.

---

### 5. Wardrobe Twins

The backend uses cosine similarity to compare the user's Fashion DNA with profiles stored in the demonstration community dataset.

It returns profiles with the closest aesthetic compatibility and provides the foundation for future opt-in style communities.

This concept can later support insights such as:

```text
People with a similar style profile preferred this item.
Users with a similar budget saved this outfit.
Similar profiles frequently styled this product for campus wear.
```

The current implementation uses demonstration profiles and does not claim to represent Myntra's real customer data.

---


### 7. Anti-Trend Mode

Recommendation algorithms can sometimes create an aesthetic echo chamber by repeatedly showing products similar to previous choices.

Anti-Trend Mode reverses the recommendation order and displays products with lower Fashion DNA compatibility.

This allows users to:

* discover unfamiliar aesthetics,
* explore outside their usual style,
* find unexpected combinations,
* and intentionally experiment with their fashion identity.

---

### 8. Fashion Memory

Fashion Memory records important shopping activity together with recommendation context.

It is designed to remember information such as:

* selected products,
* Fashion DNA match score,
* purchase date,
* occasion,
* and the reason the product was recommended.

This creates the foundation for a personal fashion timeline and future regret-prevention capabilities.

The long-term version of Fashion Memory will distinguish between:

```text
Saved
Wishlisted
Added to cart
Purchased
Kept
Returned
Frequently worn
```

---

### 9. Voice-to-Outfit

Users can describe their occasion through voice instead of typing.

The Reverse Shopping screen integrates the browser's native Speech Recognition API.

A user can tap the microphone and say:

```text
I need an outfit for a beach party in Goa this weekend.
```

The browser transcribes the spoken input and uses it as the Reverse Shopping prompt.

> Voice recognition support depends on the browser. Google Chrome provides the most reliable support for the current implementation.

---

### 10. Myntra Muse

Myntra Muse is a floating fashion-assistant interface powered by Google Gemini (an LLM-backed assistant).

It is deeply grounded in the user's stored profile, active wardrobe, and the live product catalog. It strictly recommends candidate products mathematically aligned with the user's DNA, preventing hallucinations. 

If the LLM is unreachable or the API key is unconfigured, it gracefully falls back to an offline rule-based intent matching system.

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* React Router
* Vanilla CSS
* Context API
* Browser Speech Recognition API
* Vitest
* React Testing Library
* Playwright

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### Database

* SQLite
* SQLAlchemy
* Alembic

### Machine Learning and Recommendation Logic

* Scikit-Learn
* TF-IDF Vectorizer
* Cosine Similarity
* Weighted Vector Operations
* Rule-based recommendation scoring

### Development and Quality

* Oxlint
* Pytest
* Pytest Coverage
* GitHub Actions
* Centralized frontend API errors
* React Error Boundary
* Centralized FastAPI error responses

---

## 📁 Project Structure

```text
Stackers/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── scripts/
│   │   └── bootstrap_legacy_sqlite.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_cors.py
│   │   ├── test_health.py
│   │   └── test_products.py
│   ├── alembic.ini
│   ├── config.py
│   ├── database.py
│   ├── errors.py
│   ├── main.py
│   ├── ml.py
│   ├── models.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── seed.py
│
├── src/
│   ├── api/
│   ├── app/
│   ├── components/
│   ├── context/
│   ├── data/
│   ├── screens/
│   ├── styles/
│   ├── App.jsx
│   └── main.jsx
│
├── tests/
│   └── e2e/
│       └── smoke.spec.js
│
├── .env.example
├── .gitignore
├── package.json
├── playwright.config.js
├── start.sh
└── vite.config.js
```

---

## 💻 How to Run Locally

The application uses a React frontend and a FastAPI backend.

You can either start both services using the project startup script or run them manually in separate terminals.

---

## 1. Clone the Repository

```bash
git clone https://github.com/pavani0959/Stackers.git
cd Stackers
```

---

## 2. Configure Environment Variables

From the repository root:

```bash
cp .env.example .env
```

Open `.env` and confirm that it contains suitable local-development values:

```env
VITE_API_BASE_URL=http://localhost:8000
DATABASE_URL=sqlite:///./myntra.db
FRONTEND_ORIGINS=["http://localhost:5173"]
ENVIRONMENT=development
```

### Environment variable details

#### `VITE_API_BASE_URL`

The backend URL used by the React application.

```env
VITE_API_BASE_URL=http://localhost:8000
```

Vite exposes frontend environment variables through `import.meta.env`.

`VITE_API_BASE_URL` is embedded into the frontend during the build process. Configure the correct value before running:

```bash
npm run build
```

for a production deployment.

#### `DATABASE_URL`

The SQLAlchemy database connection URL.

For local SQLite development:

```env
DATABASE_URL=sqlite:///./myntra.db
```

#### `FRONTEND_ORIGINS`

A JSON list of frontend origins allowed by the backend CORS configuration.

```env
FRONTEND_ORIGINS=["http://localhost:5173"]
```

#### `ENVIRONMENT`

The current application environment.

```env
ENVIRONMENT=development
```

Supported examples include:

```text
development
test
production
```

---

## 3. Start the Backend

From the repository root:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the locked backend dependencies:

```bash
pip install -r requirements.txt
```

Safely prepare the database:

```bash
python scripts/bootstrap_legacy_sqlite.py
alembic upgrade head
python seed.py
```

Start the FastAPI development server:

```bash
uvicorn main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

The interactive API documentation will be available at:

```text
http://localhost:8000/docs
```

### Database startup behavior

The startup sequence supports:

* fresh SQLite databases,
* databases already managed by Alembic,
* and compatible SQLite databases created before Alembic was introduced.

The bootstrap command validates legacy tables before adding migration tracking.

The seed command is idempotent. It inserts or updates demonstration records without dropping tables or deleting unrelated data.

---

## 4. Start the Frontend

Open a second terminal at the repository root:

```bash
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

---

## 5. Start Both Services Using the Startup Script

From the repository root, make the script executable once:

```bash
chmod +x start.sh
```

Then run:

```bash
./start.sh
```

The script prepares the backend database, safely seeds demonstration data, and starts the required development services.

---

## 🗄️ Database Migrations

Alembic manages the application database schema.

Before starting the backend, apply all migrations:

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

Check the currently applied revision:

```bash
alembic current
```

Check whether SQLAlchemy models and Alembic migrations are synchronized:

```bash
alembic check
```

A successful consistency check prints:

```text
No new upgrade operations detected.
```

---

## Existing Local SQLite Database

Older versions of the project created SQLite tables before Alembic migration tracking was introduced.

Do not run the following command manually:

```bash
alembic stamp head
```

Instead, use the safe bootstrap script:

```bash
cd backend
source venv/bin/activate

python scripts/bootstrap_legacy_sqlite.py
alembic upgrade head
```

The bootstrap script checks the existing tables and columns before adding an Alembic revision.

It handles the following situations:

### Fresh database

No application tables exist.

The script leaves the database unchanged so Alembic can create the schema.

### Alembic-managed database

An `alembic_version` table already exists.

The script leaves the database unchanged and reports the current revision.

### Compatible legacy database

The required application tables and columns exist, but there is no `alembic_version` table.

The script verifies the schema before stamping the initial revision.

### Incompatible database

Only part of the expected schema exists, or required columns are missing.

The script refuses to stamp the database instead of incorrectly marking it as migrated.

---

## 🌱 Demonstration Data

Run:

```bash
cd backend
source venv/bin/activate
python seed.py
```

The seed operation is safe to run multiple times.

It:

* inserts missing demonstration products,
* inserts missing community profiles,
* updates existing seed records,
* preserves unrelated database records,
* rolls back changes if an exception occurs,
* and does not drop any table.

---

## 🧪 Development and CI Checks

### Frontend Checks

Install the exact frontend dependency versions:

```bash
npm ci
```

Run linting, unit tests, and the production build:

```bash
npm run check
```

The `check` command runs:

```text
npm run lint
npm run test
npm run build
```

You can also run the commands separately.

#### Lint

```bash
npm run lint
```

#### Unit tests

```bash
npm run test
```

#### Production build

```bash
npm run build
```

---

## Browser End-to-End Test

Install Playwright Chromium once:

```bash
npm run test:e2e:install
```

Run the browser smoke test:

```bash
npm run test:e2e
```

The smoke test verifies that:

* the application loads,
* React renders the splash screen,
* the main heading is visible,
* the main call-to-action is visible,
* and the shared rendering error screen is not displayed.

---

## Backend Checks

From the repository root:

```bash
cd backend
source venv/bin/activate
```

Run backend tests with coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

The backend test foundation currently verifies areas including:

* health endpoint behavior,
* standardized validation errors,
* configured CORS origins,
* rejection of unknown CORS origins,
* missing-product error responses,
* and isolated test database initialization.

Backend tests configure their own test environment and do not depend on the ignored development `.env` file.

---

## GitHub Actions

The repository includes an automated GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

The workflow runs for configured pushes and pull requests.

### Frontend job

The frontend CI job performs:

```text
npm ci
npm run check
Playwright Chromium installation
npm run test:e2e
```

### Backend job

The backend CI job performs:

```text
pip install -r requirements.txt
alembic upgrade head
alembic check
pytest --cov=. --cov-report=term-missing
```

A pull request should not be merged until both the frontend and backend jobs pass.

---

## 🧯 Error Handling

### Frontend API Errors

All backend requests use a shared API client.

The client handles:

* missing API base URLs,
* network failures,
* non-JSON responses,
* unsuccessful HTTP status codes,
* FastAPI validation errors,
* and centralized backend error messages.

Feature screens use a shared retryable API error component for user-facing failures.

### React Rendering Errors

The React application is wrapped in a shared Error Boundary.

Unexpected component-rendering failures display a fallback page instead of leaving the application blank.

### Backend Errors

FastAPI uses centralized exception handling for:

* application-specific exceptions,
* missing resources,
* request validation failures,
* HTTP exceptions,
* and unexpected server errors.

Backend errors follow a consistent response structure.

Example:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Product not found"
  }
}
```

---

## 🔒 Repository Hygiene

Local environment files and generated artifacts are excluded through `.gitignore`.

Ignored files include:

```text
.env
SQLite database files
Python virtual environments
Python cache directories
pytest caches
coverage output
node_modules
frontend build output
Playwright test output
```

The following file remains committed intentionally:

```text
.env.example
```

It documents the required environment variables without storing real secrets.

---

## 🏆 Business Value for Myntra

### 1. Reduced Decision Uncertainty

Confidence breakdowns help users understand whether a product fits their style, occasion, budget, weather, and wardrobe.

### 2. Lower Return Potential

Fashion Memory and future regret-prevention signals can identify repeated purchases, low-compatibility items, and patterns associated with returns.

### 3. Higher Average Order Value

Reverse Shopping recommends complete outfits rather than isolated products, creating opportunities for multi-item purchases.

### 4. Stronger Personalization

Fashion DNA allows recommendations to use identity and aesthetic compatibility instead of depending only on clicks and product categories.

### 5. Improved Customer Trust

Explainable scores help users understand why the system is recommending a product.

### 6. Greater Retention

Fashion Memory, Wardrobe Twins, creators, and style-evolution features can turn Myntra from a transactional shopping application into a long-term fashion companion.

---

## 🧭 Current Product Status

The project currently contains a functional React and FastAPI foundation with:

* onboarding,
* Fashion DNA calculation,
* personalized recommendations,
* Decision Intelligence,
* Reverse Shopping,
* creator DNA blending,
* Wardrobe Twins,
* Anti-Trend Mode,
* Fashion Memory,
* voice input,
* Myntra Muse,
* centralized error handling,
* Alembic migrations,
* isolated backend tests,
* frontend tests,
* Playwright smoke testing,
* and GitHub Actions configuration.

Some functionality currently uses a demonstration dataset, deterministic recommendation logic, browser-local state, or rule-based responses.

The project is being developed incrementally toward a more production-ready architecture with persistent user profiles, structured fashion events, improved recommendation scoring, and evidence-based regret prevention.

---

## ⚠️ Known limitations / demo scope

* **Virtual Try-On (AR):** This is purely a front-end UI simulation of what an AR fitting room would look like; no real computer vision or pose estimation runs in the background.
* **Style Twins:** The community matches use a seeded synthetic cohort of demo users, not live production users.
* **Myntra Muse AI:** When the Google Gemini API key is missing or unreachable, the assistant degrades gracefully to a simpler, rule-based fallback mode.
* **Demo Mode:** The frontend runs as a client-side demo connected to a local backend.

---

## 🛣️ Planned Improvements

The next development phases include:

* persistent user accounts and profiles,
* versioned Fashion DNA history,
* structured product categories,
* database-backed Fashion Memory,
* separate cart, purchase, keep, and return events,
* real budget extraction for Reverse Shopping,
* complete outfit compatibility scoring,
* improved wardrobe intelligence,
* evidence-based regret prevention,
* richer Style Twin cohort insights,
* responsive desktop layouts,
* GSAP-powered motion design,
* improved accessibility,
* PostgreSQL deployment,
* and production observability.

---

## 🤝 Contributing

Create a dedicated branch before making changes:

```bash
git checkout -b feat/your-feature-name
```

Run all checks before committing:

```bash
npm run check
npm run test:e2e

cd backend
source venv/bin/activate
alembic upgrade head
alembic check
pytest --cov=. --cov-report=term-missing
```

Commit using a clear message:

```bash
git add .
git commit -m "feat: describe the implemented feature"
```

Push the branch:

```bash
git push -u origin feat/your-feature-name
```

Open a pull request and confirm that both GitHub Actions jobs pass.

---

## 📄 License

This project was created as a hackathon and educational implementation.

Before using the application commercially, review the licences and usage rights of all images, datasets, libraries, creator identities, trademarks, and third-party services included in the project.

---

<div align="center">

### Myntra Identity

**From product recommendations to confident fashion decisions.**

</div>
