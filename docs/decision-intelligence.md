# Phase 4 — Decision Intelligence

## Overview

Phase 4 replaces recomputed recommendation confidence with persisted, immutable Decision Intelligence snapshots.

A recommendation decision is calculated once by the backend, stored in the database, and referenced using a stable snapshot UUID.

The same stored decision is then used by:

- Home recommendation feed
- Product Detail
- Decision Intelligence
- Fashion Memory

This prevents scores, explanations, and warnings from changing between screens or after a page reload.

## Decision flow

```text
Current user profile
        +
Current Fashion DNA
        +
User preferences
        +
Product information
        +
Request context
        +
Wardrobe and event evidence
        ↓
Decision Intelligence engine
        ↓
Persisted RecommendationSession
        ↓
Persisted RecommendationItem
        ↓
Immutable snapshot UUID
```

Product Detail and Decision Intelligence read the same stored `RecommendationItem` snapshot.

Fashion Memory also reads the stored recommendation-time snapshot rather than calculating a new score.

## Server-owned profile

The frontend does not submit Fashion DNA, confidence values, profile snapshots, or score breakdowns.

The backend loads the current user's latest persisted:

- Style profile
- Fashion DNA
- Profile version
- Preferences
- Wardrobe items
- User events

Requests containing frontend-owned recommendation fields such as `user_profile`, `dna`, `confidence`, or `score_breakdown` are rejected.

This prevents clients from manipulating recommendation results.

## Decision model version

The current scoring model is:

```text
decision-v1.0.0
```

Every recommendation session stores the model version used when the decision was created.

Historical decisions retain their original model version even when the application later introduces a newer scoring model.

## Scoring model

The overall recommendation score is calculated using five weighted components.

| Component | Weight |
|---|---:|
| Style DNA compatibility | 35% |
| Occasion compatibility | 20% |
| Budget compatibility | 20% |
| Wardrobe compatibility | 15% |
| Season compatibility | 10% |
| Total | 100% |

Every component stores:

- Raw component score
- Component weight
- Weighted score
- Evidence source
- Evidence used during calculation

The overall score is calculated from the stored weighted component scores:

```text
overall score =
    style weighted score
  + occasion weighted score
  + budget weighted score
  + wardrobe weighted score
  + season weighted score
```

Every component score and the final overall score are constrained to the range `0–100`.

## Style DNA compatibility — 35%

Style compatibility compares the product's stored tags with the user's persisted Fashion DNA and identity.

Evidence may include:

- Profile version
- Primary identity
- Secondary identity
- Product tags
- Matched style tags
- Fashion DNA values

The frontend cannot provide or override this evidence.

## Occasion compatibility — 20%

Occasion compatibility uses:

- Requested occasion
- User occasion priorities
- Product occasions

A direct requested-occasion match receives the strongest score.

When no explicit occasion is provided, the engine uses persisted occasion preferences where available.

When occasion evidence is unavailable, the component uses a neutral score and the explanation states the limitation.

## Budget compatibility — 20%

Budget compatibility uses real numeric values:

- User budget minimum
- User budget maximum
- Product price
- Amount over budget, when applicable

Products inside the selected budget range receive the strongest score.

Products above the maximum budget receive a progressively lower score based on how far they exceed the range.

When numeric budget information is unavailable, the engine may use the stored budget tier.

When no budget evidence exists, the component uses a neutral score rather than inventing a budget match.

## Wardrobe compatibility — 15%

Wardrobe compatibility uses persisted wardrobe items.

Evidence may include:

- Number of active wardrobe items
- Complementary categories
- Matching tags
- Matching colours
- Exact subcategory and colour duplicates

Complementary wardrobe items may increase the score.

Existing duplicates may reduce the score and generate a `wardrobe_duplicate` regret signal.

When the user has no wardrobe data, the component uses a neutral score and the explanation clearly states that wardrobe evidence was limited.

## Season compatibility — 10%

Season compatibility uses stored request context and the product's stored season field.

Examples:

- All-season product: strongest compatibility
- Matching requested season: strong compatibility
- Unknown season context: neutral compatibility
- Season mismatch: reduced compatibility

Phase 4 does not claim to use live weather.

A live weather claim must not be added unless an actual weather service is integrated and its evidence is stored.

## Evidence rules

All scores, explanations, and regret signals must be supported by stored evidence.

The engine may use:

- Style profile
- Fashion DNA
- User preferences
- Product information
- Wardrobe items
- User events
- Request context

The engine must not generate unsupported claims such as:

- Similar users loved this
- People with your DNA bought this
- 90% of matching users purchased this
- Items under a certain score are returned 60% of the time
- Bought by people like you
- Perfect for you

Community behaviour is not used because Phase 4 does not currently have a verified aggregate community evidence pipeline.

Community claims may only be introduced when a valid numerator, denominator, aggregation method, privacy policy, and stored evidence source exist.

## Evidence-backed explanations

Explanations are generated only from the stored score breakdown and evidence.

Approved wording includes:

- Strong match
- Moderate match
- Limited match
- Within your selected budget
- Above your selected budget
- Aligned with your current Fashion DNA
- Limited wardrobe evidence
- Matching the requested occasion

Explanations must not promise that a product is perfect for the user.

Each explanation reason stores:

- Reason code
- Title
- Detail
- Component score
- Evidence source

Limitations are stored when relevant evidence is unavailable.

## Regret signals

Regret signals are generated only when real evidence exists.

### Over budget

Code:

```text
over_budget
```

Created only when the product price exceeds the user's persisted maximum budget.

### Weak style alignment

Code:

```text
weak_style_alignment
```

Created only when the calculated style score is below the configured threshold.

### Occasion mismatch

Code:

```text
occasion_mismatch
```

Created only when occasion evidence produces a low compatibility score.

### Wardrobe duplicate

Code:

```text
wardrobe_duplicate
```

Created only when matching wardrobe items actually exist.

Evidence includes the matching subcategory, colour, and duplicate count.

### Category return history

Code:

```text
category_return_history
```

Created only when actual return events exist for products in the same category.

The signal stores the real category and return count.

No return-rate percentage is generated without a verified numerator and denominator.

## Immutable snapshots

A recommendation snapshot stores the state used at recommendation time.

### RecommendationSession stores

- User ID
- Style profile ID
- Profile version
- Profile snapshot
- Context snapshot
- Session type
- Parsed intent
- Model version
- Creation time

### RecommendationItem stores

- Snapshot UUID
- Recommendation session ID
- Product ID
- Product snapshot
- Overall score
- Score breakdown
- Evidence sources
- Explanation
- Regret signals
- Rank
- Creation time

After a snapshot is created:

- A later Fashion DNA version does not change it.
- A later product price change does not change it.
- A later product tag change does not change it.
- Reloading a screen does not calculate it again.
- Fashion Memory reads the original recommendation-time result.

## Product snapshot

The product snapshot stores the product data used when the recommendation was created, including:

- Product ID
- SKU
- Name
- Brand
- Description
- Price
- Original price
- Image
- Category
- Subcategory
- Primary colour
- Tags
- Occasions
- Budget tier
- Season

Historical recommendation screens use this stored product snapshot instead of rebuilding the result from current product data.

## Profile snapshot

The profile snapshot stores:

- Profile ID
- Profile version
- Fashion DNA
- Identity
- Profile confidence

The snapshot allows historical decisions to remain explainable even after the user updates their Fashion DNA.

## Persisted Decision Intelligence endpoints

### Create one product decision

```http
POST /api/decisions/products/{product_id}
```

The backend loads the current user's profile and creates one persisted decision snapshot.

The response includes the stable snapshot UUID.

### Read a stored decision

```http
GET /api/decisions/{snapshot_id}
```

This endpoint performs no scoring.

It only loads and returns the persisted snapshot.

### Create the persisted feed

```http
POST /api/decisions/feed
```

The feed creates one `RecommendationSession` and stores the ranked `RecommendationItem` records belonging to that session.

Every returned feed item contains its own snapshot UUID.

### Read Fashion Memory

```http
GET /api/decisions/memory
```

Fashion Memory joins:

```text
UserEvent
    ↓ recommendation_item_id
RecommendationItem
    ↓ session_id
RecommendationSession
```

It returns the stored recommendation-time snapshot.

It does not invoke the score calculator.

## Frontend flow

### Home

Home calls:

```text
POST /api/decisions/feed
```

It does not send the frontend user profile.

Each `ProductCard` receives a persisted decision item.

### Product Detail

When opened from Home, Product Detail reads the decision UUID from:

```text
/product/{product_id}?decision={snapshot_uuid}
```

It calls:

```text
GET /api/decisions/{snapshot_uuid}
```

When Product Detail is opened directly without a UUID, it creates one decision using:

```text
POST /api/decisions/products/{product_id}
```

It then places the returned UUID into the URL.

### Decision Intelligence

Decision Intelligence uses:

```text
/decision/{snapshot_uuid}
```

It calls only:

```text
GET /api/decisions/{snapshot_uuid}
```

It does not request the product confidence endpoint and does not recalculate the score.

### Fashion Memory

Fashion Memory calls:

```text
GET /api/decisions/memory
```

Local `purchaseMemory` and `buyItem` state are not used.

A recommendation appears in Fashion Memory only when a meaningful backend event such as `purchase`, `keep`, or `return` is linked through `recommendation_item_id`.

## Removed endpoints

Phase 4 removes the old recomputed endpoints:

```text
POST /api/recommend/feed
POST /api/recommend/confidence/{product_id}
```

It also removes public access to generic client-written recommendation session endpoints.

Reverse Shopping remains available temporarily through:

```text
POST /api/recommend/reverse
```

Reverse Shopping will receive its own persisted architecture in a later phase.

## Migration

The Phase 4 Alembic migration:

```text
a66d2cc193f6
```

extends the existing recommendation tables.

The migration:

1. Adds new columns as nullable.
2. Backfills existing recommendation sessions.
3. Generates a unique UUID for every existing recommendation item.
4. Stores product snapshots for existing items.
5. Adds empty evidence and regret-signal containers for legacy rows.
6. Changes the new fields to `NOT NULL`.
7. Creates the unique snapshot UUID index.

The migration is designed to support SQLite development and PostgreSQL CI.

## Testing requirements

Phase 4 tests verify:

- Every score is between 0 and 100.
- Weighted scores produce the stored overall score.
- The frontend cannot submit Fashion DNA for scoring.
- Snapshots can be retrieved in a new database session.
- Old decisions do not change after a profile update.
- Old decisions do not change after a product update.
- Model and profile versions are stored.
- Regret signals require actual evidence.
- Unsupported community claims do not appear.
- Feed items share one recommendation session.
- Fashion Memory returns stored snapshots.
- Fashion Memory does not invoke the score calculator.
- Product Detail and Decision Intelligence display the same score.
- Reloading Decision Intelligence preserves the same score.

## Validation commands

Backend:

```bash
cd backend
source venv/bin/activate

alembic heads
alembic current
alembic check

pytest --cov=. --cov-report=term-missing
```

Frontend:

```bash
npm run check
npm run test:e2e
```

Repository checks:

```bash
grep -RInE   "Similar DNA users loved|Real Eyes recommendation|returned 60%|People with your DNA preferred|90% of users|bought in the last 7 days"   src backend   --exclude-dir=venv   --exclude-dir=node_modules   --exclude="*.test.jsx"   --exclude="test_*.py"   || true
```

```bash
grep -RInE   "purchaseMemory|buyItem"   src   --exclude="*.test.jsx"   --exclude-dir=node_modules   || true
```

```bash
grep -RIn   "user_profile"   src/api/decisions.js   src/screens/Home   src/screens/ProductDetail   src/screens/DecisionIntelligence   --exclude="*.test.jsx"   || true
```

## Definition of done

Phase 4 is complete only when:

- Server-owned scoring is used.
- Decisions are persisted once.
- Product and profile snapshots are immutable.
- Every score component contains traceable evidence.
- Product Detail and Decision Intelligence use the same snapshot.
- Reloading Decision Intelligence preserves the score.
- Fashion Memory reads stored decisions.
- Fashion Memory does not recalculate historical scores.
- No unsupported community claim remains.
- No unsupported return-rate percentage remains.
- No fabricated fallback score remains.
- Fresh SQLite migration passes.
- Existing-row migration backfill passes.
- PostgreSQL CI migration passes.
- Backend tests pass.
- Frontend tests pass.
- Playwright decision consistency tests pass.