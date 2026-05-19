# Contributing to Order Assistant

Thanks for your interest! This is a demo of conversational AI for the food, restaurant ordering & delivery domain, so contributions are welcome — but **allergen-safety-critical code paths have extra rules**.

## Code of conduct

Be kind. Disagree on technical merits, not on people.

## Quick start for contributors

```bash
git clone https://github.com/drcinfotech/Food-AI-Chatbot.git
cd Food-AI-Chatbot

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest -v       # must be 54/54 green before you start

# Frontend
cd ../frontend
npm install
npm run dev
```

## What we accept

✅ **Good contributions:**

- New intents with corresponding tests
- New block renderers in `Blocks.jsx` with corresponding Pydantic models
- New allergen detection patterns — with both a positive test AND a no-false-positive test
- More fictional restaurants, menu items, or offers (must be invented, not real)
- Documentation, README improvements, screenshots
- Accessibility improvements
- i18n / localization support
- Tighter test coverage

❌ **What we do NOT accept:**

- Real food delivery, restaurant chain, or aggregator brand names. The CI test `test_no_real_food_brands_in_data` will fail your PR.
- Removing or weakening the allergen safety layer
- Adding "guarantees" of allergen-free preparation — that's exactly what we refuse, and for good reason
- Removing the cross-contamination disclaimer
- Removing payment-privacy guards
- Removing or relaxing prompt-injection blocks
- Real FSSAI numbers, real restaurant addresses, or any data that could be confused for real listings
- Adding personal API keys, payment gateway credentials, or real card data
- Code that connects to real payment processors without explicit opt-in and clear documentation of PCI-DSS implications
- Replacing "Order Assistant" with an unverified brand name

## Allergen-safety rule changes (require extra review)

Any PR that modifies the following files **must** include test coverage and a written rationale in the PR description:

- `backend/app/safety.py` — allergen detection, allergen-promise refusal, payment privacy, social engineering
- `backend/app/chatbot.py` — the safety-first dispatch and `_check_cart_for_allergens` logic
- `backend/data/catalog.json` — particularly the `allergens` arrays on menu items
- Any change that touches how warnings are surfaced in the UI

**The default position when in doubt:** refuse to make claims about allergen safety. False confidence is the failure mode that kills people. When unsure whether a query is "asking for help avoiding an allergen" (which we DO help with) vs "asking us to guarantee safety" (which we DON'T), bias toward the refusal pattern.

## Style

- Python: PEP 8, type hints on public functions, docstrings on modules
- JS/JSX: 2-space indent, prefer functional components, hooks for state
- Commits: imperative present tense ("Add X", "Fix Y")
- One logical change per PR

## Reporting a security issue

For anything that looks like a real security issue (not just a demo limitation), please email the maintainers privately rather than opening a public issue.
