"""PayPilot eval suite - runs fully offline against the mock PayPal client.

Covers intent parsing, ranking, every policy guardrail, the mocked PayPal
OAuth -> order -> capture flow, receipts, and brain fallback behaviour.

Usage:  python eval.py        (exit code 0 = all pass)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paypilot.agent import ShopAgent, _extract_capture
from paypilot.catalog import load_catalog, search
from paypilot.mock_paypal import MockPayPal
from paypilot.paypal import PayPalClient
from paypilot.policy import Policy, check as policy_check
from paypilot.reasoning import OfflineBrain, LLMBrain, BrainError, get_brain

CATALOG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "examples", "catalog.csv")
PRODUCTS = load_catalog(CATALOG)

PASS = 0
FAIL = 0
FAILURES = []


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("PASS  %s" % name)
    else:
        FAIL += 1
        FAILURES.append(name)
        print("FAIL  %s  %s" % (name, extra))


def make_agent(policy=None, daily_spent=0.0):
    return ShopAgent(PRODUCTS, policy=policy, brain=OfflineBrain(),
                     paypal=PayPalClient(mock=MockPayPal()),
                     daily_spent=daily_spent)


def main():
    # ---- catalog ------------------------------------------------------
    check("catalog_loads_all_products", len(PRODUCTS) == 17,
          "got %d" % len(PRODUCTS))
    check("catalog_out_of_stock_excluded",
          all(p.stock > 0 for p in PRODUCTS))

    # ---- offline intent parsing ---------------------------------------
    brain = OfflineBrain()
    i1 = brain.parse("Birthday gift for my mom, under $50 - she loves gardening")
    check("intent_budget_under_50", i1.budget == 50.0, str(i1.budget))
    check("intent_occasion_birthday", i1.occasion == "birthday", i1.occasion)
    check("intent_recipient_mom", i1.recipient == "mom", i1.recipient)
    check("intent_category_garden", i1.category_hint == "garden",
          i1.category_hint)
    i2 = brain.parse("Find me the cheapest mechanical keyboard")
    check("intent_cheapest_flag", i2.cheapest is True)
    check("intent_no_budget_without_amount", i2.budget is None)
    i3 = brain.parse("Buy a luxury watch for $500 as a treat")
    check("intent_budget_dollar_500", i3.budget == 500.0, str(i3.budget))

    # ---- search / ranking ----------------------------------------------
    cands = search(PRODUCTS, keywords=i1.keywords, category="garden",
                   max_price=50.0)
    check("search_respects_budget", all(c.product.price <= 50.0 for c in cands))
    check("search_respects_category",
          all(c.product.category == "garden" for c in cands))
    check("search_returns_candidates", len(cands) >= 3, str(len(cands)))
    check("every_candidate_has_evidence",
          all(len(c.evidence) >= 2 for c in cands))
    cheap = search(PRODUCTS, keywords=["keyboard"], category="electronics",
                   sort="price_asc")
    check("search_cheapest_sort_ascending",
          [c.product.price for c in cheap] ==
          sorted(c.product.price for c in cheap))
    check("search_no_match_category",
          search(PRODUCTS, category="nonexistent") == [])

    # ---- happy path: gift for mom --------------------------------------
    agent = make_agent()
    res = agent.run("Birthday gift for my mom, under $50 - she loves gardening")
    check("gift_completed", res.status == "completed", res.status)
    check("gift_picks_tool_set", res.chosen.product.id == "G001",
          res.chosen.product.id if res.chosen else "none")
    check("gift_amount", abs(res.amount - 34.99) < 0.001, str(res.amount))
    check("gift_capture_id", res.capture_id.startswith("MOCK-CAPTURE-"),
          res.capture_id)
    check("gift_order_created", bool(res.order and res.order.get("id")))
    check("gift_receipt_mentions_product",
          "Deluxe Garden Tool Set" in res.receipt_text)
    check("gift_receipt_html_has_capture",
          res.capture_id in res.receipt_html)
    phases = [s.phase for s in res.steps]
    check("gift_phase_order",
          phases == ["PERCEIVE", "SEARCH", "SELECT", "POLICY",
                     "EXPLAIN", "EXECUTE", "CAPTURE"], str(phases))
    check("gift_policy_allowed", res.policy.action == "allow",
          res.policy.rule)

    # ---- cheapest keyboard ----------------------------------------------
    res = make_agent().run("Find me the cheapest mechanical keyboard")
    check("keyboard_completed", res.status == "completed", res.status)
    check("keyboard_cheapest_pick", res.chosen.product.id == "T001",
          res.chosen.product.id if res.chosen else "none")
    check("keyboard_amount_79_99", abs(res.amount - 79.99) < 0.001)

    # ---- policy: category allowlist -------------------------------------
    res = make_agent().run("Buy a luxury watch for $500 as a treat")
    check("watch_blocked", res.status == "blocked", res.status)
    check("watch_rule_category",
          res.policy.rule == "CATEGORY_NOT_ALLOWED", res.policy.rule)
    check("watch_no_payment", res.order is None and res.capture_id == "")

    # ---- policy: approval threshold (hold -> approve -> pay) ------------
    res = make_agent().run("Get me nice wireless earbuds under $150")
    check("earbuds_held_for_approval",
          res.status == "awaiting_approval", res.status)
    check("earbuds_hold_rule",
          res.policy.rule == "APPROVAL_THRESHOLD", res.policy.rule)
    check("earbuds_no_payment_while_held", res.order is None)
    res2 = make_agent().run("Get me nice wireless earbuds under $150",
                            approve=True)
    check("earbuds_paid_after_approval", res2.status == "completed", res2.status)
    check("earbuds_pick", res2.chosen.product.id == "T002",
          res2.chosen.product.id if res2.chosen else "none")

    # ---- policy: per-order limit ----------------------------------------
    tight = Policy(max_per_order=30.0)
    res = make_agent(policy=tight).run(
        "Birthday gift for my mom, under $50 - she loves gardening")
    check("per_order_blocked", res.status == "blocked", res.status)
    check("per_order_rule", res.policy.rule == "MAX_PER_ORDER",
          res.policy.rule)

    # ---- policy: daily limit --------------------------------------------
    res = make_agent(daily_spent=490.0).run(
        "Birthday gift for my mom, under $50 - she loves gardening")
    check("daily_limit_blocked", res.status == "blocked", res.status)
    check("daily_limit_rule", res.policy.rule == "DAILY_LIMIT",
          res.policy.rule)

    # ---- policy: merchant blocklist --------------------------------------
    blocked = Policy(blocked_merchants=("GreenThumb Co",))
    res = make_agent(policy=blocked).run(
        "Birthday gift for my mom, under $50 - she loves gardening")
    check("merchant_blocked", res.status == "blocked", res.status)
    check("merchant_rule", res.policy.rule == "BLOCKED_MERCHANT",
          res.policy.rule)

    # ---- policy unit check ------------------------------------------------
    d = policy_check(Policy(), PRODUCTS[0], 0.0)
    check("policy_unit_allow", d.action == "allow" and d.rule == "ALL_CHECKS_PASSED",
          "%s/%s" % (d.action, d.rule))
    check("policy_allow_has_evidence", len(d.evidence) >= 3)

    # ---- no match ---------------------------------------------------------
    res = make_agent().run("Find a gift under $5")
    check("no_match_status", res.status == "no_match", res.status)

    # ---- mock PayPal client ------------------------------------------------
    mock = MockPayPal()
    client = PayPalClient(mock=mock)
    tok = client.token()
    check("mock_token", tok.startswith("MOCK-"), tok)
    order = client.create_order(34.99, description="test", ref_id="G001")
    check("mock_order_created", order["status"] == "CREATED")
    check("mock_order_amount", order["purchase_units"][0]["amount"]["value"] == "34.99")
    check("mock_order_approve_url", order["approve_url"].startswith("https://"))
    cap = client.capture_order(order["id"])
    cid, cstatus = _extract_capture(cap)
    check("mock_capture_completed", cstatus == "COMPLETED", str(cstatus))
    check("mock_capture_id", bool(cid and cid.startswith("MOCK-CAPTURE-")))
    check("mock_get_order", client.get_order(order["id"])["id"] == order["id"])

    # ---- AG Grid policy audit console ----------------------------------------
    from paypilot.catalog import Product
    from paypilot.grid import (audit_rows, render_grid_page, rows_payload,
                               summarize)

    pol = Policy()
    rows = audit_rows(PRODUCTS, pol)
    check("grid_audits_every_row", len(rows) == len(PRODUCTS),
          "%d vs %d" % (len(rows), len(PRODUCTS)))
    check("grid_decisions_are_valid",
          all(r["decision"] in ("allow", "block", "hold") for r in rows))
    check("grid_every_row_cites_a_rule", all(r["rule"] for r in rows))
    check("grid_every_row_has_evidence", all(r["evidence"] for r in rows))
    s = summarize(rows)
    check("grid_summary_counts_match",
          s["allow"] + s["block"] + s["hold"] == s["total"], str(s))
    check("grid_over_cap_is_blocked",
          all(r["decision"] == "block" for r in rows if r["price"] > pol.max_per_order))
    check("grid_approval_threshold_holds",
          all(r["decision"] == "hold" for r in rows
              if pol.approval_threshold <= r["price"] <= pol.max_per_order
              and r["category"] in pol.allowed_categories))
    check("grid_disallowed_category_blocked",
          all(r["rule"] == "CATEGORY_NOT_ALLOWED" for r in rows
              if r["category"] not in pol.allowed_categories))

    # daily spend is the interesting dial: raising it flips rows to DAILY_LIMIT
    base_blocked = summarize(rows)["block"]
    loaded = audit_rows(PRODUCTS, pol, daily_spent=480.0)
    check("grid_daily_limit_flips_rows",
          summarize(loaded)["block"] > base_blocked,
          "%d -> %d" % (base_blocked, summarize(loaded)["block"]))
    check("grid_daily_limit_rule_named",
          any(r["rule"] == "DAILY_LIMIT" for r in loaded))
    check("grid_deterministic",
          audit_rows(PRODUCTS, pol) == audit_rows(PRODUCTS, pol))

    # payload + page
    payload = rows_payload(PRODUCTS, pol, daily_spent=50.0)
    check("grid_payload_roundtrip",
          json.loads(json.dumps(payload))["summary"]["total"] == len(PRODUCTS))
    page = render_grid_page(PRODUCTS, pol)
    check("grid_page_loads_aggrid", "ag-grid-community" in page)
    check("grid_page_has_grid_mount", 'id="grid"' in page)
    check("grid_page_declares_columns", "columnDefs" in page)
    check("grid_page_emits_rows", "const ROWS =" in page)
    check("grid_page_has_fallback", "drawFallback" in page)
    check("grid_page_no_unreplaced_tokens", "__" not in page.split("<script>")[0])

    # hostile product name must not escape the <script> block
    nasty = [Product(id="X1", name="</script><script>alert(1)</script>",
                     category="books", price=9.0, rating=4.0, tags=[],
                     merchant="M", stock=1)]
    nasty_page = render_grid_page(nasty, pol)
    check("grid_escapes_script_breakout",
            nasty_page.count("</script>") == nasty_page.count("<script>"),
            "script tags unbalanced")
    check("grid_neutralises_breakout_payload",
          "<script>alert(1)</script>" not in nasty_page)

    # live HTTP: /grid renders and /api/rows returns JSON
    from http.server import ThreadingHTTPServer
    from paypilot.web import make_handler
    import threading
    import urllib.request

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(CATALOG, False))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        base = "http://127.0.0.1:%d" % httpd.server_address[1]
        with urllib.request.urlopen(base + "/grid", timeout=10) as r:
            body = r.read().decode("utf-8")
        check("http_grid_serves_page", "<title>PayPilot" in body and "ROWS =" in body)
        with urllib.request.urlopen(base + "/api/rows?spent=300", timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        check("http_api_rows_json", data["summary"]["total"] == len(PRODUCTS))
        check("http_api_rows_honours_spent",
              data["daily_spent"] == 300.0 and data["summary"]["block"] > 0)
        with urllib.request.urlopen(base + "/grid?spent=9999", timeout=10) as r:
            big = r.read().decode("utf-8")
        check("http_grid_extreme_spent_still_renders", "ROWS =" in big)
    finally:
        httpd.shutdown()

    # ---- LLM brain fallback --------------------------------------------------
    try:
        LLMBrain("http://127.0.0.1:1/unreachable", "k", "m").parse("buy a book")
        check("llm_unreachable_raises", False, "no exception raised")
    except BrainError:
        check("llm_unreachable_raises", True)
    b = get_brain(prefer_llm=False)
    check("get_brain_offline_default", isinstance(b, OfflineBrain))

    print()
    print("=" * 60)
    print("%d passed, %d failed" % (PASS, FAIL))
    if FAILURES:
        print("failed: %s" % ", ".join(FAILURES))
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
