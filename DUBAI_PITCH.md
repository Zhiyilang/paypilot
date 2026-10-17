# PayPilot — Pitch Deck (Dubai Create AI Agents Championship)
## Target category: Best Business AI Agent (fallback: Best Personal AI Agent)

> Championship: Create AI Agents Championship, Dubai Chamber of Digital Economy.
> Prize: **USD 150,000 per category winner** (official site; announced as AED 550,000); one winner also named Dubai AI Agent of the Year (+funding). Total pool > AED 2.5M.
> Registration: opened 2026-10-07; **closes January 2027** (official timeline + FAQ — press reported December, official page wins). Free. English-only materials.
> Submission: AI-agent prototype + pitch deck + demo video (submission window Nov 2026 – Jan 2027). Multiple entries allowed with one registration.
> Grand final: first week of May 2027 — finalists demonstrate a **fully working agent live**, not an MVP.
> Eligibility: open worldwide, no minimum age, teams ≤6; idea/prototype/early-MVP stage only (not fully commercialised). ✅ PayPilot qualifies (open-source prototype, no revenue).

---

### Slide 1 — Title
**PayPilot: the AI shopping agent that cannot be talked into a bad purchase**
An autonomous agent that shops, checks policy before spending, asks a human when it matters, and pays with real PayPal — with every decision auditable.
Builder: Zhiyilang (solo) · Repo: github.com/Zhiyilang/paypilot · MIT, zero-dependency Python

### Slide 2 — The problem: agents are getting wallets, but no guardrails
- 2026 is the year AI agents start transacting on users' behalf (agentic commerce). Every major payments platform is shipping "agent checkout".
- But an LLM will rationalize a purchase you did not authorize. Prompt injection in a product page, a hallucinated "deal", a socially-engineered urgency message — all it takes is convincing text.
- The failure is already documented in adjacent domains (chatbots promising refunds they could not honor). Now imagine the agent holds your card.
- **There is no safety layer between "the model decided to buy" and "the money moved".**

### Slide 3 — The solution: the model proposes, the policy disposes
PayPilot separates *reasoning* from *authorization*:
1. **The AI brain** (any OpenAI-compatible LLM, or a deterministic offline engine) parses the request and explains its choice in plain language.
2. **The policy engine** — code, not prompt — runs hard rules before any money moves:
   - `MAX_PER_ORDER` / `DAILY_LIMIT` — hard spending caps
   - `CATEGORY_NOT_ALLOWED` / `BLOCKED_MERCHANT` — allowlists
   - `APPROVAL_THRESHOLD` — at/above a threshold, a human must approve. The LLM has no path around this.
3. **Real execution** — PayPal v2 Checkout (OAuth → order → capture), sandbox-verified.
4. **Audit trail** — every decision cites the fields it used; the full trail ships as a receipt.

Demo line for judges: *"Buy a $500 luxury watch."* → **Blocked: category not allowed. No payment attempted.**

### Slide 4 — Proof it works (the "measure" requirement)
- **172 automated assertions** (`python eval.py`, offline, no keys): intent parsing, ranking, every guardrail (block/hold/allow), the mocked PayPal OAuth→order→capture loop, receipt generation, and LLM-failure fallback.
- **CI green across Python 3.8 / 3.10 / 3.12** (GitHub Actions).
- **4 scripted demo scenarios** covering the full behavioral range: allowed+paid, cheapest-sort+paid, blocked, held→human-approved→paid.
- Zero dependencies: any judge can clone and run the entire agent in 30 seconds, offline.

### Slide 5 — Why this matters beyond shopping
The same pattern — *LLM proposes, code disposes* — is the missing safety layer for every agent that touches money, contracts, or infrastructure:
- Enterprise procurement agents (payments, POs)
- Trading agents (position limits, drawdown circuit-breakers)
- Expense agents (policy-compliant spend)
PayPilot is the reference implementation, and the open-source core of a control plane.

### Slide 6 — Commercial route
- **Open-source core** (this repo) → developer adoption, the standard pattern for "agent spending guardrails".
- **Enterprise control plane**: managed policy management (SSO, role-based approval workflows, immutable audit logs, multi-provider payments beyond PayPal), sold per-seat to companies deploying agentic commerce — the exact buyers every payments platform is courting in 2026.
- Grant use: build the control plane, run 3 paid pilots with SMB procurement teams, publish the safety benchmark.

### Slide 7 — The ask
**USD 150,000 development grant** (Best Business AI Agent) to turn the reference implementation into the enterprise control plane — with 172 passing evals and a live PayPal integration as the starting proof.

---

## Speaker notes / likely judge questions
- *"Is the AI real?"* — Two engines behind one interface: an OpenAI-compatible LLM (intent parsing + justification) and a deterministic offline fallback. The eval suite asserts the fallback works, so the agent never breaks when a model is down.
- *"Isn't the offline engine just rules?"* — The rules are the *safety* layer (they must be deterministic to be trustworthy). The AI layer handles ambiguity: intent, preferences, explanation. Separation of concerns is the design.
- *"Why PayPal?"* — It is the most widely integrated payments API; the client is a thin, swap-able module (same interface runs against an in-process mock, which is why tests are honest).
- *"Commercialised?"* — No. Open-source prototype, no revenue, no paying customers. Grant would fund the first pilots.
- *"Grand final needs a fully working agent?"* — The PayPal sandbox path is already live-verified; the grant funds hardening it to production grade by May 2027.
