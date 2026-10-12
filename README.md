# PayPilot

**An AI shopping agent with policy guardrails that executes real PayPal sandbox checkouts.**

Built for the [PayPal AI Hackathon 2026](https://paypalaihackathon.devpost.com/) ("Build What's Next with PayPal and AI").

PayPilot reads a natural-language shopping request, picks a product from a catalog *with evidence*, checks a spending policy **before** touching money, asks a human for approval when the amount is large, and then pays through the PayPal v2 Checkout API. Every decision in the trail is auditable — and the policy engine cannot be talked out of a "no" by the model.

- **Zero dependencies** — pure Python standard library. `pip install` nothing.
- **Two AI engines** — an OpenAI-compatible LLM brain (works with Xiaomi MiMo, OpenAI, etc.) *or* a deterministic offline brain. The agent degrades gracefully if the model is unavailable.
- **Guardrails first** — per-order cap, daily cap, category allowlist, merchant blocklist, and a human-approval threshold. The LLM never sees the policy override path.
- **Evidence-cited reasoning** — every candidate and every policy decision cites the fields it used.
- **53 assertions** — `python eval.py` runs the whole agent loop against an in-process PayPal mock, offline.

## Quick start

```bash
git clone https://github.com/Zhiyilang/paypilot.git
cd paypilot

# 1. run the test suite (offline, no keys needed)
python eval.py
# -> 53 passed, 0 failed

# 2. run the 4 scripted demo scenarios (mock PayPal, offline)
python -m paypilot demo

# 3. ask the agent something yourself (mock mode)
python -m paypilot shop "Birthday gift for my mom, under $50 - she loves gardening"
python -m paypilot shop "Find me the cheapest mechanical keyboard"
python -m paypilot shop "Get me nice wireless earbuds under $150" --approve

# 4. start the web demo UI (mock mode)
python -m paypilot serve --port 8780
# open http://127.0.0.1:8780
```

## How it works

```
request ──► PERCEIVE ──► SEARCH ──► SELECT ──► POLICY ──► APPROVAL ──► EXPLAIN ──► EXECUTE ──► CAPTURE ──► receipt
             (intent)     (rank +     (best       (hard       (human       (why, in     (PayPal     (payment
                           evidence)   cand.)      rules)      if ≥ thr.)   plain EN)    order)      captured)
```

**1. PERCEIVE** — the brain parses the request into a structured `Intent`: occasion, recipient, budget, keywords, category hint, "cheapest" flag. LLM brain when configured, offline heuristic otherwise.

**2. SEARCH** — the catalog is ranked with match evidence per candidate (`matches 'gardening' (name/category/tags)`, `price $34.99 within budget $50.00 (headroom $15.01)`, ...). Keyword filters are enforced: irrelevant products never reach the model.

**3. SELECT** — highest score wins (or lowest price when the user asked for the cheapest).

**4. POLICY** — the guardrail engine runs *before* any money moves:

| Rule | Effect |
|---|---|
| `BLOCKED_MERCHANT` | block: merchant on the blocklist |
| `CATEGORY_NOT_ALLOWED` | block: category outside the allowlist |
| `MAX_PER_ORDER` | block: price above the per-order cap |
| `DAILY_LIMIT` | block: spend would exceed the daily cap |
| `APPROVAL_THRESHOLD` | hold: a human must approve before payment |

**5. APPROVAL** — held orders are not paid until a human passes `--approve` (or ticks the box in the web UI).

**6. EXPLAIN** — the brain writes the justification in plain English ("I picked X because ..."), citing rating, price fit, and matched signals.

**7. EXECUTE / 8. CAPTURE** — PayPal v2 Checkout: OAuth2 client-credentials token → create order (`intent=CAPTURE`) → capture. The same client class runs against `api-m.sandbox.paypal.com` (live) or an in-process mock (offline), so tested code is shipped code.

**9. Receipt** — a plain-text receipt for the CLI and an HTML report with the full decision trail.

## Demo scenarios

`python -m paypilot demo` runs four scenarios that show the agent's full behavioural range:

| # | Request | What it demonstrates |
|---|---|---|
| 1 | "Birthday gift for my mom, under $50 - she loves gardening" | happy path: picks the Deluxe Garden Tool Set ($34.99), policy allows, pays |
| 2 | "Find me the cheapest mechanical keyboard" | "cheapest" intent → price-ascending ranking, pays |
| 3 | "Buy a luxury watch for $500 as a treat" | blocked: `CATEGORY_NOT_ALLOWED` — no payment attempted |
| 4 | "Get me nice wireless earbuds under $150" | held at `APPROVAL_THRESHOLD` ($129 ≥ $100) → pays only after human approval |

## Connecting the real PayPal sandbox

Mock mode is the default so anyone can run everything offline. To point the agent at the live sandbox:

1. Create a free PayPal Developer account at <https://developer.paypal.com/> and a sandbox REST app.
2. Export credentials:

```bash
export PAYPAL_CLIENT_ID="your-sandbox-client-id"
export PAYPAL_SECRET="your-sandbox-secret"
```

3. Run with `--live`:

```bash
python -m paypilot shop "wireless earbuds under $150" --live --approve
python -m paypilot serve --port 8780 --live
```

Live flow note: PayPal's hosted checkout requires a buyer to approve the order in a browser before capture. The agent prints the `approve_url` for the order it creates; after the sandbox buyer approves, the capture call completes the payment. (Mock mode runs the full loop in one step — that is what the demo and the eval suite use.)

## Adding an LLM brain

Any OpenAI-compatible chat endpoint works. Example with Xiaomi MiMo:

```bash
export PAYPILOT_LLM_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
export PAYPILOT_LLM_API_KEY="your-key"
export PAYPILOT_LLM_MODEL="mimo-v2-flash"
```

The LLM does intent parsing and justification writing. If the endpoint is unreachable or returns unusable JSON, PayPilot falls back to the offline brain automatically — the agent never breaks because a model is down. The eval suite asserts this fallback behaviour.

## Configuration reference

| Env var | Default | Meaning |
|---|---|---|
| `PAYPILOT_PAYPAL_MODE` | `mock` | `mock` (offline) or `live` (sandbox) |
| `PAYPAL_CLIENT_ID` / `PAYPAL_SECRET` | — | sandbox REST app credentials (live mode) |
| `PAYPILOT_LLM_BASE_URL` | Xiaomi MiMo endpoint | OpenAI-compatible base URL |
| `PAYPILOT_LLM_API_KEY` | — | enables the LLM brain when set |
| `PAYPILOT_LLM_MODEL` | `mimo-v2-flash` | model name |

Policy defaults live in `paypilot/policy.py` (`Policy` dataclass): `max_per_order=200`, `daily_limit=500`, `approval_threshold=100`, allowed categories `garden/electronics/apparel/books`.

## Project layout

```
paypilot/
├── paypilot/
│   ├── __init__.py
│   ├── __main__.py        # python -m paypilot
│   ├── catalog.py         # CSV catalog + evidence-cited ranking
│   ├── policy.py          # spending guardrails (block/hold/allow)
│   ├── reasoning.py       # LLM brain + offline brain (one interface)
│   ├── paypal.py          # PayPal v2 REST client (token/order/capture)
│   ├── mock_paypal.py     # in-process PayPal mock (tests + demo mode)
│   ├── agent.py           # the agent loop
│   ├── receipts.py        # text + HTML receipts with decision trail
│   ├── cli.py             # shop / demo / serve commands
│   └── web.py             # stdlib web demo UI
├── examples/
│   ├── catalog.csv        # 17 products across 5 categories
│   └── requests.txt       # example natural-language requests
├── eval.py                # 53 assertions, runs offline
├── requirements.txt       # (empty - stdlib only)
├── .env.example
├── LICENSE                # MIT
└── README.md / README.zh.md
```

## Why an agent that can spend money needs guardrails

An LLM will happily rationalize a purchase you did not authorize. PayPilot's design assumption is the opposite: **the model proposes, the policy disposes.** Keyword filtering keeps irrelevant products away from the model; the policy engine runs after selection with hard rules; anything at or above the approval threshold waits for a human. The model writes the explanation — it never writes the permission.

## Hackathon notes

- Category targets: *Best Use of PayPal + AI*, *Best Use of Agentic Commerce*, *Most Creative*, *Best Demo Delivery*.
- Submission requirements covered: public repo with license (MIT) — yes; working prototype runnable by judges — yes, offline mock mode needs zero setup; demo video — recorded separately; documentation — this file.

## License

MIT — see [LICENSE](LICENSE).
