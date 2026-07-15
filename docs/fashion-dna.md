# Fashion DNA and Identity Profile

## Overview

Fashion DNA is the backend-owned representation of a user's style identity.

The frontend sends eight controlled quiz answers using question IDs and choice IDs. It does not calculate DNA percentages, identity names, confidence scores, evidence, or profile versions.

The backend is responsible for:

- Validating all eight quiz answers
- Mapping answer choices to controlled style features
- Including saved onboarding preferences
- Calculating deterministic Fashion DNA
- Normalizing Fashion DNA to exactly 100.00%
- Generating the identity name and description
- Calculating confidence and its breakdown
- Collecting profile evidence
- Creating a new profile version
- Persisting the result in the database

## Request Contract

The frontend sends one answer for each of the eight quiz questions.

Example:

```json
{
  "answers": [
    {
      "question_id": "everyday-look",
      "choice_id": "minimal-campus"
    },
    {
      "question_id": "silhouette",
      "choice_id": "relaxed-fit"
    },
    {
      "question_id": "brand-personality",
      "choice_id": "clean-premium"
    },
    {
      "question_id": "colour-palette",
      "choice_id": "neutral-palette"
    },
    {
      "question_id": "comfort-expression",
      "choice_id": "comfort-balanced"
    },
    {
      "question_id": "occasion-priority",
      "choice_id": "campus-priority"
    },
    {
      "question_id": "shopping-motivation",
      "choice_id": "versatility-first"
    },
    {
      "question_id": "fashion-goal",
      "choice_id": "shop-smarter"
    }
  ]
}