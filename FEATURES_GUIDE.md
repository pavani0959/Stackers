# 🏆 Myntra Identity App — Complete Feature & Verification Guide

> **Stack:** React (Vite) + FastAPI (Python) + SQLite + Scikit-Learn
> **Status:** 100% Production Ready. All backend ML algorithms and frontend interfaces are fully connected and functional. No mocked API responses.

---

## ✅ FEATURE 1 — AI Onboarding & DNA Quiz
**Type:** Full-Stack ML
**What it does:** A 4-step onboarding (Gender → Budget → Colours → Occasions) followed by a 5-question visual quiz. The answers are sent to the Python ML backend which calculates your Fashion DNA percentages using clustering logic.
**How to check:**
1. Open `http://localhost:5173`
2. Click through the splash screen.
3. Select Gender, set Age using the slider → click **Continue**
4. Pick your Budget tier → **Continue**
5. Pick your Colours and Occasions → **Continue**
6. Answer all 5 quiz visual style questions.
7. **PROOF:** After Q5, the app calls the real Python `/api/dna/calculate` endpoint. Watch the screen transform into your DNA Result page with real percentages (e.g. "78% Minimalist, 22% Streetwear").

---

## ✅ FEATURE 2 — ML Personalized Home Feed & "Real Eyes"
**Type:** Full-Stack ML
**What it does:** The Home Feed is generated dynamically. Every time you load it, it calls `/api/recommend/feed` with your DNA vector. Python's scikit-learn cosine similarity sorts all 20 products from highest to lowest match score for your specific DNA. 
**How to check:**
1. Complete the quiz and reach the Home screen.
2. **PROOF:** The products shown are in a different order for a Minimalist vs a Streetwear person. Look at the **🧬 XX% Match** badge on each product card.
3. **PROOF 2:** Click **"See all (20)"** to expand the grid and verify all backend items were sorted correctly. 
4. Check the **"👁 Real Eyes"** horizontal scrolling section for items popular with users who share your exact DNA.

---

## ✅ FEATURE 3 — Explainable AI (Decision Intelligence)
**Type:** Full-Stack ML
**What it does:** When you click on any product, the app calls `/api/recommend/confidence/{id}` to get a breakdown of *why* the product was recommended — with 5 individual scores: Style Match, Occasion Match, Budget Match, Weather Match, Wardrobe Fit.
**How to check:**
1. From the Home Feed, click on any product card.
2. Scroll down to the **"🎯 Confidence Score"** card.
3. **PROOF:** You will see 5 animated progress bars all showing real percentages. Click **"🤔 Why is this recommended for me?"** to see the detailed written explanation.

---

## ✅ FEATURE 4 — Reverse Shopping (NLP Engine)
**Type:** Full-Stack NLP
**What it does:** You type an occasion in plain English. Python's `TfidfVectorizer` converts your text into mathematical vectors, compares them against all product tags and occasions, and generates **3 distinct outfits** (Optimal, Alternative, Bold) composed of exactly a top, bottom, and accessory.
**How to check:**
1. Click the **🔮 Reverse** tab in the bottom nav.
2. Click a quick-prompt chip (e.g. "💼 Interview") OR type your own: *"College fest Saturday, retro theme, ₹1500"*
3. Click **"✨ Generate My Outfits"**.
4. **PROOF:** The backend will return 3 completely assembled outfits. You can purchase them individually by clicking "Buy All".

---

## ✅ FEATURE 5 — Voice-to-Outfit (Speech AI)
**Type:** Frontend Web API
**What it does:** Instead of typing, you can speak your occasion. The browser's native SpeechRecognition API transcribes your voice, fills the text box, and auto-generates the outfit.
**How to check:**
1. Go to the **🔮 Reverse** tab.
2. Click the **🎤 Microphone button** inside the text box.
3. When it turns red and pulses, speak clearly: *"I need an outfit for a night out with friends"*.
4. **PROOF:** Your spoken words appear in the text box automatically and the 3 outfits generate themselves automatically. *(Note: Requires Google Chrome).*

---

## ✅ FEATURE 6 — Community / Wardrobe Twins
**Type:** Full-Stack ML
**What it does:** Calls `/api/community/twins` with your DNA vector. Python computes Cosine Similarity between your DNA and every other profile in the SQLite database, returning only the users with a high match.
**How to check:**
1. Click the **🌐 Tribe** tab in the bottom nav.
2. Scroll down to the **"👥 Wardrobe Twins"** section.
3. **PROOF:** Real users with their match percentages appear (e.g. "Priya S. — 94% Match"). These are calculated live via the Python ML engine.

---

## ✅ FEATURE 7 — Steal Their Vibe (Creator DNA Blend)
**Type:** Full-Stack ML
**What it does:** You can "steal" the DNA of a celebrity creator. The app calls `/api/dna/blend` which does weighted vector addition of your DNA and the creator's DNA, fundamentally altering your profile permanently.
**How to check:**
1. On the **🌐 Tribe** tab, scroll to the **"Creators"** section.
2. Tap **"Blend DNA"** on any creator.
3. Move the slider to 50% and click **"Confirm Identity Shift"**.
4. **PROOF:** Go back to the **🏠 Home** tab and reload — your product feed will have shifted entirely to include items that match the new merged DNA.

---

## ✅ FEATURE 8 — Anti-Trend Mode
**Type:** Full-Stack ML
**What it does:** Reverses the ML recommendation ranking. Instead of showing your highest DNA matches, it shows the *lowest* matches — items that break your style echo chamber.
**How to check:**
1. On the **🏠 Home** tab, look at the top card: **"🔀 Anti-Trend Mode"**.
2. Click the toggle switch — it turns pink.
3. **PROOF:** The product feed instantly reloads with completely different products (low match scores). The banner text changes to "Opposite of your DNA".

---

## ✅ FEATURE 9 — Dynamic DNA Pricing
**Type:** Full-Stack
**What it does:** When a product has a 90%+ DNA match confidence score, the backend automatically applies a 15% discount as a reward for buying items that fit your identity.
**How to check:**
1. Go to the **🏠 Home** tab (ensure Anti-Trend is OFF).
2. Look for product cards showing **"✨ -15% DNA"** in green.
3. Click on one of those products.
4. **PROOF:** On the Product Detail page, you will see: *"💰 Because this is a 90%+ match, you unlocked a 15% DNA Discount!"*

---

## ✅ FEATURE 10 — Virtual Try-On (AR)
**Type:** Frontend UI Simulation
**What it does:** A simulated Augmented Reality fitting room. Shows a camera UI with the product overlaid using a scanning animation to demonstrate the UX of how ML pose estimation would work in a real production camera.
**How to check:**
1. Click any product to go to its Detail page.
2. Tap the **"📸 Try It On (AR)"** button on the bottom left of the product image.
3. **PROOF:** A full-screen AR overlay appears with the product image superimposed, corner guides, a body alignment prompt, and a neon scanning line.

---

## ✅ FEATURE 11 — Fashion Memory
**Type:** Full-Stack (Context API)
**What it does:** Every item you "Add to Cart" or "Buy All" is logged with its DNA Match %, date, occasion, and purchase reason. 
**How to check:**
1. Click any product → Select a size → Click **"Add to Cart"**.
2. Now click the **📖 Memory** tab in the bottom nav.
3. **PROOF:** Your purchased item appears in the list. If the match was below 80%, it shows a ⚠️ regret warning. If above 80%, it shows a 🧬 success message. It also tracks the total drift in your DNA over time.

---

## ✅ FEATURE 12 — Myntra Muse (AI Stylist Chatbot)
**Type:** Full-Stack API
**What it does:** A floating conversational AI that reads your Fashion DNA. It uses intent matching on the backend API (`/api/muse/chat`) to give personalized style advice.
**How to check:**
1. Look for the **✨** floating button in the bottom right of any screen.
2. Tap it to open the chat window.
3. Type: *"What should I wear?"* or *"Night out"*.
4. **PROOF:** The bot sends the message to the Python server, which calculates a response using your live DNA (e.g. "Based on your DNA, you have an 85% affinity for Streetwear...").
