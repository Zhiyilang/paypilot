# PayPilot demo video — under 3 minutes, English

**Rendered video:** `paypilot_demo.mp4` (repo root) — recorded from the four `python -m paypilot demo` scenarios, no editing needed. Upload it to YouTube/Vimeo and paste the link into the Devpost submission.

Judges reject static mockups, so the video must show the app **actually running**.
Everything below runs offline with zero credentials (PayPal mock mode), so you can
record it right now.

**Setup before you hit record (5 min)**

```powershell
cd D:\桌面\part-time jobs\GitHub\paypilot
python -m paypilot serve            # opens http://127.0.0.1:8780
```

Keep these tabs open in this order: `http://127.0.0.1:8780` (agent console),
`/grid`, `/renewals`, `/docs`. Open the terminal off to the side.

**Recording tips**
- 1920×1080, no copyrighted music, speak clearly in English.
- Do one clean take per segment; splice if you must, but never speed-ramp a segment
  where a number changes — judges need to read the numbers.
- Resize the browser window so text is legible when scaled down.

---

## 0:00 – 0:15 · Hook (say this, don't read it)

> "Everyone is building AI agents that can spend money. I wanted to know what
> happens when the agent is wrong — so I built the guardrails first, then let
> the agent loose. This is PayPilot."

*Visual: browser at the PayPilot home page. No scrolling yet.*

## 0:15 – 0:45 · The agent, end to end

1. In the textarea type:
   `Birthday gift for my mom, under $50 - she loves gardening`
2. Click **Run agent** (leave "pre-approve" **unchecked**).
3. Walk the **decision trail** out loud, top to bottom:
   - `PERCEIVE` — budget 50, keywords gardening, category garden
   - `SEARCH` — ranked candidates with evidence
   - `SELECT` — best score
   - `POLICY` — *point at the rule id shown*
   - `EXECUTE` / `CAPTURE` — PayPal order id + capture id

> "Every phase cites the field that produced it. That trail is the product —
> not the purchase."

4. Now type: `Buy the most expensive telescope you have`
   → status **BLOCKED by policy**, rule `MAX_PER_ORDER`.

> "The agent does not get to argue. Policy runs before money moves."

## 0:45 – 1:15 · Policy Audit Grid (AG Grid)

1. Click **Open the Policy Audit Grid**.
2. Say: "One demo proves one decision. This proves the whole policy surface —
   every catalog item, one row each."
3. Click any row → show the rule + evidence panel underneath.
4. **Drag "already spent today" from 0 to about 480.**
   → rows flip to BLOCK live, rule `DAILY_LIMIT`. This is the money shot — hold
   it for two seconds.

> "I did not add AG Grid as decoration. Sorting and filtering hundreds of
> policy decisions is the only way to check the guardrails hold everywhere."

5. Click **Export CSV** to show the export works.

## 1:15 – 1:45 · Renewal Radar

1. Click **Renewal Radar**.
2. Point at the calendar: "The next 60 days of charges, predicted from each
   merchant's own cadence."
3. Point at NETFLIX.COM → `PRICE_HIKE`, $15.49 → $22.99, verdict *renegotiate*.
4. Point at ADOBE → `DUPLICATE`, two identical charges 3 days apart, verdict
   *cancel*, and note **next charge is blank**.

> "It refuses to predict what it cannot see. A charge it can't explain is left
> off the calendar instead of guessed."

5. Read one nudge aloud — it is a polite, ready-to-send message, not a demand.

> "AI writes the wording. It never writes the facts — those are deterministic."

## 1:45 – 2:15 · The API (OpenAPI / agent context)

1. Click **API docs** → Swagger UI over `openapi.yaml`.
2. In the terminal:

```powershell
curl -s localhost:8780/api/v1/quote -H 'Content-Type: application/json' `
     -d '{\"request\":\"birthday gift for my mom, under $50, she gardens\"}'
```

3. Then:

```powershell
python -m paypilot context
```

> "That's the API compressed into about fifteen hundred tokens — operations, the
> five policy rules, catalog shape, runnable examples. Paste it into a system
> prompt and a *different* agent can call PayPilot correctly on the first try.
> Point `PAYPILOT_EXTRA_SPEC` at any other OpenAPI document and it merges in."

## 2:15 – 2:40 · Proof it is real

1. Terminal:

```powershell
python eval.py
```

Let the final line land on screen: **`172 passed, 0 failed`**.

> "172 assertions, fully offline — including a rogue-brain test where the model
> proposes a tool that doesn't exist and a destructive fix: both get rejected
> and not one byte of data changes."

2. Quick scroll of the repo tree.

> "Zero dependencies. Python standard library only — no SDK, no build step."

## 2:40 – 2:55 · Close

> "PayPilot: an agent that can pay, and a policy engine it can't talk its way
> past. PayPal sandbox when you bring keys, mock offline when you don't.
> Source is on GitHub — link in the description. Thank you."

*Visual: `github.com/Zhiyilang/paypilot` on screen for the last 3 seconds.*

---

## YouTube metadata (copy-paste)

**Title** (≤ 60 chars):
`PayPilot — the AI shopping agent that can't outspend its guardrails`

**Description:**
```
PayPilot is an AI shopping agent with hard spending guardrails. It parses a
natural-language request, ranks products with evidence, checks a deterministic
policy engine BEFORE touching money, pays through the PayPal sandbox, and
returns an auditable decision trail.

Built for Build What's Next with PayPal and AI.

What's in the demo:
0:00  the premise: guardrails first, agent second
0:15  full agent loop, and a request the policy refuses
0:45  Policy Audit Grid (AG Grid) - every catalog item, decision per row,
      live daily-limit flip
1:15  Renewal Radar - renewal calendar, price hikes, duplicate charges,
      polite nudges
1:45  REST API, OpenAPI 3.0.3, and a ~1.5k-token agent context block
2:15  172 offline assertions, zero dependencies
2:40  close

Categories submitted to: Best Use of AG Studio, Best Use of APIMatic,
Best Use of Postman, Best Use of Render.

Source: https://github.com/Zhiyilang/paypilot
Spec:   /openapi.yaml (OpenAPI 3.0.3)
Stack:  Python 3 standard library only (no SDK, no build step)

#PayPalHackathon #AIAgents #AGGrid #OpenAPI #Python
```

**Tags:** `paypal hackathon, ai agent, agentic commerce, ag grid, openapi,
apimatic, postman, policy engine, python stdlib, guardrails`

**Checklist before you publish**
- [ ] Public on YouTube (unlisted is fine only if the Devpost form accepts it —
      prefer **public**)
- [ ] Under 3:00
- [ ] No copyrighted music
- [ ] `172 passed, 0 failed` is legible on screen
- [ ] GitHub link in the description
