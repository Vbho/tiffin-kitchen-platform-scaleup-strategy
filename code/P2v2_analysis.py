"""
analysis.py — Business Transformation & Scale-Up Strategy
         Vegetarian Tiffin Home Kitchen → Deliveroo / Uber Eats
=================================================================
Analyst  : Vaishnavi Bhor

Context  : A UK home kitchen operates a vegetarian tiffin service
           (30 orders/day, WhatsApp-only ordering). The founders want
           to scale onto Deliveroo and Uber Eats while keeping a
           vegetarian-only niche. They have no website, no legal
           food business registration setup, no standardised menu,
           and no order management system.

This is a Business Transformation project, not a unit economics model.
The analytical framework is a McKinsey Situation-Complication-Resolution
structured around five strategic workstreams.

Analytical Framework
--------------------
Root question: What is the end-to-end roadmap to transform this business
               from a 30-order WhatsApp operation to a scalable, platform-
               listed vegetarian food brand?

Workstream 1 — Current State Economics
  What does the business look like today? Revenue, margin, capacity.

Workstream 2 — Platform Economics & Pricing Strategy
  Do current prices survive Deliveroo/Uber Eats commission?
  What must prices be on-platform to protect margin?

Workstream 3 — Menu Standardisation
  How do you transform a daily WhatsApp menu into a platform-ready
  fixed menu with proper allergen info and photos?

Workstream 4 — Compliance & Legal Setup
  What does UK law require before going live on any food platform?

Workstream 5 — 90-Day Implementation Roadmap
  What gets done in what order, with what cost and who owns it?

Sources
-------
  - Deliveroo commission: 30-35% for independent UK restaurants
    (Deliverect 2025; PayoutLedger 2026; HomeCooks research)
  - Deliveroo onboarding fee: £510 incl VAT, split over 8 payments
    (Delta Digital 2025)
  - Uber Eats commission: 20-30% depending on plan (Deliverect 2025)
  - Food business registration: free, mandatory 28 days before trading
    (FSA / GOV.UK)
  - Level 2 Food Hygiene certificate: recommended, ~£20-30 online
    (FSA guidance)
  - HMRC self-employment registration: required (GOV.UK)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

CHARTS = Path("charts")
OUT    = Path("outputs")
for p in [CHARTS, OUT]:
    p.mkdir(exist_ok=True)

# ── Design system ─────────────────────────────────────────────────────────────
NAVY  = "#1A3C5E"; CORAL = "#C0392B"; AMBER = "#E67E22"
GREEN = "#27AE60"; SKY   = "#2980B9"; SILVER = "#BDC3C7"
BG    = "#FAFAFA"; DGREY = "#2C3E50"; SAFFRON = "#F39C12"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlepad": 14, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False,
})

def save(fig, name):
    fig.savefig(CHARTS / name, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓  {name}")


# ══════════════════════════════════════════════════════════════════════════════
# WORKSTREAM 1 — CURRENT STATE ECONOMICS
# ══════════════════════════════════════════════════════════════════════════════
print("\n── WS1: Current State Economics ──────────────────────────────")

# Current WhatsApp menu (Wednesday sample — menu changes daily)
MENU_ITEMS = [
    ("Bhurji + Masoor + Rice + 3 Chapatis",      7.00, "combo"),
    ("Bhurji + Masoor + 4 Chapatis",              7.00, "combo"),
    ("Medium Rice + Bhurji + Masoor",             7.00, "combo"),
    ("Medium Bhurji + Chapatis or Rice",          7.00, "combo"),
    ("Medium Masoor + Chapatis or Rice",          6.00, "single"),
    ("Large Bhurji",                              8.00, "single"),
    ("Large Masoor",                              7.00, "single"),
    ("Large Bhurji + Large Masoor",              14.00, "sharing"),
]

# Estimated order mix: combos dominate, sharing rare
ORDER_MIX = [0.20, 0.20, 0.15, 0.15, 0.10, 0.08, 0.07, 0.05]
weighted_aov = sum(p * m for (_, p, _), m in zip(MENU_ITEMS, ORDER_MIX))

# Current state parameters
DAILY_ORDERS     = 30
TRADING_DAYS     = 260    # Monday–Friday + some Saturdays
COGS_PCT         = 0.40   # 40% of revenue — ingredients + packaging (vegetarian, UK home kitchen)
PACKAGING_COST   = 0.50   # per order — foil trays, insulated bags
DELIVERY_OWN     = 2.50   # current self-delivery cost per order (petrol/time proxy)

daily_revenue    = DAILY_ORDERS * weighted_aov
annual_revenue   = daily_revenue * TRADING_DAYS
daily_cogs       = daily_revenue * COGS_PCT
daily_gross_profit = daily_revenue - daily_cogs
gross_margin_pct = daily_gross_profit / daily_revenue

print(f"  Weighted AOV                 : £{weighted_aov:.2f}")
print(f"  Daily revenue (30 orders)    : £{daily_revenue:.2f}")
print(f"  Annual revenue (est.)        : £{annual_revenue:,.0f}")
print(f"  Gross margin (direct)        : {gross_margin_pct:.0%}")
print(f"  Daily gross profit           : £{daily_gross_profit:.2f}")

# Current state table for export
current_state = pd.DataFrame({
    "metric": ["Daily orders", "Weighted AOV", "Daily revenue",
                "Annual revenue (est.)", "COGS %", "Gross margin %",
                "Daily gross profit", "Trading channel", "Order management"],
    "value":  [str(DAILY_ORDERS), f"£{weighted_aov:.2f}", f"£{daily_revenue:.2f}",
               f"£{annual_revenue:,.0f}", f"{COGS_PCT:.0%}", f"{gross_margin_pct:.0%}",
               f"£{daily_gross_profit:.2f}", "WhatsApp only", "Manual / WhatsApp"],
})
current_state.to_csv(OUT / "current_state.csv", index=False)

# Chart 1: Current state revenue waterfall + scale projections
order_targets = [30, 50, 75, 100, 150]
daily_revenues = [o * weighted_aov for o in order_targets]
daily_gps      = [r * gross_margin_pct for r in daily_revenues]
annual_revs    = [r * TRADING_DAYS for r in daily_revenues]

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle("Workstream 1: Current State & Revenue Scale Potential\n"
             "From 30-order WhatsApp operation to scaled platform business",
             fontsize=12, fontweight="bold", color=DGREY, y=1.01)

ax1 = axes[0]
bar_colors = [CORAL] + [AMBER, SKY, GREEN, NAVY]
bars = ax1.bar(order_targets, [r/1000 for r in annual_revs],
               color=bar_colors, width=10, zorder=2)
ax1.axvline(30, color=CORAL, ls="--", lw=1.5, alpha=0.7)
for bar, orders, rev in zip(bars, order_targets, annual_revs):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
             f"£{rev/1000:.0f}K\n({orders} ord/day)",
             ha="center", fontsize=9, fontweight="bold")
ax1.set_xlabel("Daily Orders")
ax1.set_ylabel("Annual Revenue (£000)")
ax1.set_title("Annual Revenue by Order Volume\n(Current: 30 orders/day — red bar)", fontsize=11)
ax1.grid(axis="y", alpha=0.2, zorder=1)

ax2 = axes[1]
# Today's revenue split
labels = ["Ingredients\n& packaging", "Gross Profit\n(keep)"]
sizes  = [COGS_PCT, gross_margin_pct]
colors = [CORAL, GREEN]
wedges, texts, autotexts = ax2.pie(
    sizes, labels=labels, colors=colors, autopct="%1.0f%%",
    startangle=90, pctdistance=0.6,
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
for at in autotexts:
    at.set_fontsize(13); at.set_fontweight("bold"); at.set_color("white")
ax2.set_title(f"Gross Margin at Current Prices\nAOV = £{weighted_aov:.2f} · 30 orders/day · WhatsApp direct",
              fontsize=11)
ax2.text(0, -1.3, f"Daily revenue: £{daily_revenue:.0f}   |   Daily gross profit: £{daily_gross_profit:.0f}",
         ha="center", fontsize=10, color=DGREY)
plt.tight_layout()
save(fig, "01_current_state_economics.png")


# ══════════════════════════════════════════════════════════════════════════════
# WORKSTREAM 2 — PLATFORM ECONOMICS & PRICING STRATEGY
# ══════════════════════════════════════════════════════════════════════════════
print("\n── WS2: Platform Economics & Pricing ─────────────────────────")

# THE CORE PROBLEM: at current prices (£6-8), 30% commission leaves thin margin
# A £7 order: Deliveroo takes £2.10 → restaurant gets £4.90 → COGS £2.80 → GP £2.10
# That's still positive but reduces GP from 60% to 30%
# Solution: price differently ON platform (this is standard industry practice)

platforms = {
    "Deliveroo": {"commission": 0.30, "onboarding": 510, "payments": "1st & 16th monthly"},
    "Uber Eats (Standard)": {"commission": 0.25, "onboarding": 0, "payments": "Weekly"},
    "Uber Eats (Premium)": {"commission": 0.30, "onboarding": 0, "payments": "Weekly"},
    "Own Website (direct)": {"commission": 0.029, "onboarding": 200, "payments": "Daily (Stripe)"},
}

# Recommended platform pricing: raise prices by ~30% to absorb commission
# while staying competitive vs. restaurant competition at these AOVs
PLATFORM_PRICE_UPLIFT = 1.30   # 30% higher than WhatsApp price
PLATFORM_AOV = weighted_aov * PLATFORM_PRICE_UPLIFT   # £9.80

pricing_analysis = []
for option, (_, direct_price, _) in zip(["Bhurji Combo", "Masoor Combo", "Single", "Large", "Sharing"],
                                          [(None,7.00,None),(None,7.00,None),(None,6.00,None),
                                           (None,8.00,None),(None,14.00,None)]):
    platform_price = round(direct_price * PLATFORM_PRICE_UPLIFT, 0) - 0.01  # e.g. £9.99
    for platform_name, pf in platforms.items():
        commission = platform_price * pf["commission"]
        receives   = platform_price - commission
        cogs       = direct_price * COGS_PCT   # COGS stays same — food cost unchanged
        gp         = receives - cogs
        gm         = gp / platform_price if gp > 0 else 0
        pricing_analysis.append({
            "menu_item": option,
            "whatsapp_price": direct_price,
            "platform_price": platform_price,
            "platform": platform_name,
            "commission_pct": pf["commission"],
            "commission_£": commission,
            "restaurant_receives": receives,
            "cogs": cogs,
            "gross_profit": gp,
            "gross_margin": gm,
        })

pricing_df = pd.DataFrame(pricing_analysis)
pricing_df.to_csv(OUT / "platform_pricing.csv", index=False)

# Key summary table — main combo at £7 across platforms
combo = pricing_df[pricing_df["menu_item"] == "Bhurji Combo"].copy()
print(f"  Weighted AOV (WhatsApp)      : £{weighted_aov:.2f}")
print(f"  Recommended platform AOV     : £{PLATFORM_AOV:.2f}  (+{PLATFORM_PRICE_UPLIFT-1:.0%})")
print()
print("  Platform economics on £7 WhatsApp item → £9.00 platform price:")
for _, row in combo.iterrows():
    print(f"  {row['platform']:30s} → receives £{row['restaurant_receives']:.2f}  "
          f"GP £{row['gross_profit']:.2f}  ({row['gross_margin']:.0%})")

# Chart 2: Platform margin comparison — three prices per platform
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle("Workstream 2: Platform Economics & Pricing Strategy\n"
             "Current prices cannot go directly onto Deliveroo/Uber Eats without repricing",
             fontsize=12, fontweight="bold", color=DGREY, y=1.01)

ax1 = axes[0]
# Show: what happens to a £7 item at different commission rates
test_prices   = [7.00, 9.00, 10.00]  # WhatsApp, recommended platform, high-end
test_labels   = ["£7\n(current\nWhatsApp)", "£9\n(recommended\nplatform)", "£10\n(premium\ntier)"]
comm_rates    = [0.30, 0.25]
commission_labels = ["30% commission (Deliveroo)", "25% commission (Uber Eats Standard)"]
bar_width = 0.3
x = np.arange(len(test_prices))

for j, (cr, label, col) in enumerate(zip(comm_rates, commission_labels, [CORAL, AMBER])):
    gps = [(p * (1-cr) - p * 0.40) / p * 100 for p in test_prices]
    bars = ax1.bar(x + j * bar_width, gps, bar_width, color=col, label=label, zorder=2, alpha=0.85)
    for bar, gp in zip(bars, gps):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"{gp:.0f}%", ha="center", fontsize=9, fontweight="bold")

ax1.set_xticks(x + bar_width/2)
ax1.set_xticklabels(test_labels)
ax1.axhline(30, color=GREEN, ls="--", lw=1.5, label="30% minimum viable margin")
ax1.set_ylabel("Gross Margin After Commission (%)")
ax1.set_title("Gross Margin by Price Point & Commission Rate\n(COGS assumed 40% of WhatsApp price)", fontsize=11)
ax1.legend(fontsize=9)
ax1.set_ylim(0, 45)
ax1.yaxis.set_major_formatter(mticker.PercentFormatter())
ax1.grid(axis="y", alpha=0.2, zorder=1)

ax2 = axes[1]
# Revenue comparison: 30 orders current vs 100 orders platform
scenarios = {
    "Current\n(30 ord,\nWhatsApp £7)":   {"orders": 30,  "price": weighted_aov, "net_pct": 1.00},
    "Platform\n(50 ord,\nDeliveroo £9)": {"orders": 50,  "price": PLATFORM_AOV, "net_pct": 0.70},
    "Platform\n(75 ord,\nDeliveroo £9)": {"orders": 75,  "price": PLATFORM_AOV, "net_pct": 0.70},
    "Mixed\n(100 ord,\n70% platform)":   {"orders": 100, "price": None, "net_pct": None,
                                           "daily_net": (30*weighted_aov*1.0 + 70*PLATFORM_AOV*0.70)},
}
net_daily = []
for k, v in scenarios.items():
    if "daily_net" in v:
        net = v["daily_net"]
    else:
        net = v["orders"] * v["price"] * v["net_pct"]
    net_daily.append(net)

sc_colors = [CORAL, AMBER, SKY, GREEN]
bars2 = ax2.bar(list(scenarios.keys()), net_daily, color=sc_colors, width=0.5, zorder=2)
for bar, nd in zip(bars2, net_daily):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+3,
             f"£{nd:.0f}/day\n(£{nd*260/1000:.0f}K/yr)",
             ha="center", fontsize=9, fontweight="bold")
ax2.set_ylabel("Daily Revenue Received (after commission)")
ax2.set_title("Daily Net Revenue: Current vs Platform Scenarios\n(After commission deduction)", fontsize=11)
ax2.grid(axis="y", alpha=0.2, zorder=1)
ax2.set_ylim(0, 700)

plt.tight_layout()
save(fig, "02_platform_economics.png")


# ══════════════════════════════════════════════════════════════════════════════
# WORKSTREAM 3 — MENU STANDARDISATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n── WS3: Menu Standardisation ─────────────────────────────────")

# The WhatsApp menu has CRITICAL problems for platform listing:
# 1. 8 options per day — too many for a small operation on a platform
# 2. "Medium" and "Large" not quantified (no gram weights)
# 3. No allergen information (LEGALLY REQUIRED)
# 4. No photos (conversion killer on Deliveroo/Uber Eats)
# 5. Menu changes daily — platforms need a stable permanent menu
# 6. "3 chapaties" vs "4 chapaties" is a confusing differentiator

# Recommended: consolidate to 5-6 permanent menu items
# Keep daily specials as "Today's Special" — one rotating item
STANDARDISED_MENU = [
    {
        "item": "Tiffin Combo (Regular)",
        "description": "Paneer Bhurji or Masoor Dal + Basmati Rice (250g) + 3 Chapatis. "
                       "Home-style North Indian vegetarian meal, freshly prepared daily.",
        "whatsapp_price": 7.00,
        "platform_price": 9.49,
        "portion_weight": "approx 500g",
        "allergens": "Gluten (chapati/wheat), Dairy (paneer), May contain: nuts",
        "photo_needed": True,
        "est_daily_orders": 12,
    },
    {
        "item": "Tiffin Combo (Large)",
        "description": "Paneer Bhurji or Masoor Dal + Basmati Rice (350g) + 4 Chapatis. "
                       "Bigger portion for a heartier appetite.",
        "whatsapp_price": 7.00,
        "platform_price": 10.49,
        "portion_weight": "approx 700g",
        "allergens": "Gluten (chapati/wheat), Dairy (paneer), May contain: nuts",
        "photo_needed": True,
        "est_daily_orders": 8,
    },
    {
        "item": "Paneer Bhurji (Large, Solo)",
        "description": "Generously portioned Paneer Peas Bhurji in a rich tomato-onion masala. "
                       "Served with 4 chapatis OR large basmati rice. Your choice at checkout.",
        "whatsapp_price": 8.00,
        "platform_price": 10.99,
        "portion_weight": "approx 400g (solo portion)",
        "allergens": "Dairy (paneer), May contain: nuts, gluten if chapati selected",
        "photo_needed": True,
        "est_daily_orders": 4,
    },
    {
        "item": "Masoor Dal (Large, Solo)",
        "description": "Red lentil dal cooked low and slow with whole spices. "
                       "Served with 4 chapatis OR large basmati rice. Your choice at checkout.",
        "whatsapp_price": 7.00,
        "platform_price": 9.99,
        "portion_weight": "approx 400g (solo portion)",
        "allergens": "May contain: nuts, gluten if chapati selected. Fully vegan without chapati.",
        "photo_needed": True,
        "est_daily_orders": 3,
    },
    {
        "item": "Family Sharing Box",
        "description": "Large Paneer Bhurji + Large Masoor Dal + 6 chapatis + large rice. "
                       "Feeds 2-3 people. Perfect for the whole family.",
        "whatsapp_price": 14.00,
        "platform_price": 17.99,
        "portion_weight": "approx 1.2kg total",
        "allergens": "Gluten (chapati/wheat), Dairy (paneer), May contain: nuts",
        "photo_needed": True,
        "est_daily_orders": 2,
    },
    {
        "item": "Today's Special",
        "description": "Ask us what's cooking today! Daily rotating dish — "
                       "seasonal vegetables, extra curries, or festive specials.",
        "whatsapp_price": 6.00,
        "platform_price": 8.49,
        "portion_weight": "varies",
        "allergens": "Listed daily — check description before ordering",
        "photo_needed": False,
        "est_daily_orders": 1,
    },
]

menu_df = pd.DataFrame(STANDARDISED_MENU)
menu_df["price_uplift_%"] = ((menu_df["platform_price"] - menu_df["whatsapp_price"]) /
                              menu_df["whatsapp_price"] * 100)
menu_df.to_csv(OUT / "standardised_menu.csv", index=False)

# Platform menu revenue at standardised prices
daily_platform_orders = menu_df["est_daily_orders"].sum()
daily_platform_rev = (menu_df["platform_price"] * menu_df["est_daily_orders"]).sum()
daily_platform_net = daily_platform_rev * 0.70  # after 30% commission

print(f"  Current menu items/day       : 8 (too many for platform)")
print(f"  Recommended menu items       : {len(STANDARDISED_MENU)}")
print(f"  Estimated daily platform orders: {daily_platform_orders}")
print(f"  Estimated daily platform revenue: £{daily_platform_rev:.2f}")
print(f"  After 30% commission         : £{daily_platform_net:.2f}")

# Chart 3: Menu transformation — before vs after
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Workstream 3: Menu Standardisation — WhatsApp Menu → Platform-Ready Menu\n"
             "Platform listings require: fixed items · gram weights · allergen info · product photos",
             fontsize=12, fontweight="bold", color=DGREY, y=1.01)

ax1 = axes[0]
current_prices = [p for _, p, _ in MENU_ITEMS]
current_labels = [f"Opt {i+1}" for i in range(len(MENU_ITEMS))]
bars1 = ax1.bar(current_labels, current_prices, color=CORAL, width=0.6, zorder=2, alpha=0.85)
for bar, val in zip(bars1, current_prices):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f"£{val:.0f}", ha="center", fontweight="bold", fontsize=11)
ax1.set_ylabel("Price (£)")
ax1.set_title("Current WhatsApp Menu\n8 options · No allergens · No photos · Changes daily", fontsize=11)
ax1.set_ylim(0, 18)
ax1.grid(axis="y", alpha=0.2, zorder=1)

# Problems annotation
problems = ["No allergen info\n(LEGAL RISK)", "No gram weights\n(Platform req.)",
            "Daily menu changes\n(Can't list on app)", "No product photos\n(Conversion killer)"]
for i, prob in enumerate(problems):
    ax1.text(0.02, 0.95 - i*0.12, f"✗  {prob}", transform=ax1.transAxes,
             fontsize=8, color=CORAL, va="top")

ax2 = axes[1]
new_labels = [item["item"].replace(" ", "\n")[:20] for item in STANDARDISED_MENU]
new_labels_short = ["Tiffin\nCombo\n(Reg)", "Tiffin\nCombo\n(Large)", "Bhurji\n(Solo)",
                    "Masoor\n(Solo)", "Family\nBox", "Today's\nSpecial"]
old_prices = [item["whatsapp_price"] for item in STANDARDISED_MENU]
new_prices = [item["platform_price"] for item in STANDARDISED_MENU]

x = np.arange(len(STANDARDISED_MENU))
w = 0.35
bars_old = ax2.bar(x - w/2, old_prices, w, color=SILVER, label="WhatsApp price", zorder=2, alpha=0.8)
bars_new = ax2.bar(x + w/2, new_prices, w, color=GREEN, label="Platform price", zorder=2, alpha=0.85)

for bar, val in zip(bars_new, new_prices):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f"£{val:.2f}", ha="center", fontsize=8, fontweight="bold", color=GREEN)

ax2.set_xticks(x)
ax2.set_xticklabels(new_labels_short, fontsize=9)
ax2.set_ylabel("Price (£)")
ax2.set_title("Standardised Platform Menu\n6 permanent items · Allergens · Photos · Fixed description", fontsize=11)
ax2.set_ylim(0, 22)
ax2.legend(fontsize=9)
ax2.grid(axis="y", alpha=0.2, zorder=1)

# Tick marks for good things
goods = ["Fixed menu\n(Platform needs this)", "Allergens listed\n(Legal compliance)",
         "Photos per item\n(Conversion +40%)", "Gram weights\n(Customer trust)"]
for i, g in enumerate(goods):
    ax2.text(0.02, 0.95 - i*0.12, f"✓  {g}", transform=ax2.transAxes,
             fontsize=8, color=GREEN, va="top")

plt.tight_layout()
save(fig, "03_menu_standardisation.png")


# ══════════════════════════════════════════════════════════════════════════════
# WORKSTREAM 4 — COMPLIANCE CHECKLIST
# ══════════════════════════════════════════════════════════════════════════════
print("\n── WS4: Compliance & Legal Setup ─────────────────────────────")

compliance = [
    # (item, urgency, cost_£, timeline, status_assumed, source)
    ("Register as food business with local authority",
     "LEGAL MUST — cannot operate without",      0,     "28 days before trading",  "Likely not done", "FSA / GOV.UK"),
    ("HMRC self-employment registration",
     "LEGAL MUST — tax compliance",              0,     "Before trading",           "Unknown",         "GOV.UK / HMRC"),
    ("Level 2 Food Hygiene Certificate",
     "Strongly recommended, platforms may require", 25, "1 day (online course)",   "Unknown",         "FSA guidance"),
    ("Food Safety Management System (HACCP-lite)",
     "Required — documented procedures",          0,    "1-2 days to document",    "Not done",        "FSA Safer Food pack"),
    ("Allergen information for all menu items",
     "LEGAL MUST — 14 allergens to document",     0,   "Immediate",                "Not done",        "UK FIC Regulation"),
    ("Kitchen inspection by Environmental Health",
     "Follows registration — council visits",      0,   "Council arranges post-reg","Auto-triggered",  "FSA"),
    ("Food Hygiene Rating — aim for 5-star",
     "Required for Deliveroo/Uber Eats listing",   0,  "At inspection",            "Not rated",       "FHRS"),
    ("Public liability insurance",
     "Strongly recommended for delivery ops",     150,  "1-2 days",                "Not done",        "Industry standard"),
    ("Labelling: business name + allergens on packaging",
     "LEGAL MUST for delivery orders",            100,  "Before platform go-live",  "Not done",        "UK food labelling law"),
    ("Deliveroo onboarding fee",
     "Platform requirement",                       510,  "Split over 8 payments",   "Not started",     "Deliveroo/Delta Digital 2025"),
    ("Uber Eats onboarding",
     "Platform requirement (lower barrier than Deliveroo)", 0, "Faster onboarding", "Not started",    "Deliverect 2025"),
    ("Product photography (6 items)",
     "Platform conversion — not optional",        200,  "1 day shoot",             "Not done",        "Industry standard"),
    ("Simple website / ordering page",
     "Owned channel — reduces platform dependency", 200, "1-2 weeks",              "Not done",        "Recommended"),
    ("Order management system (tablet/app)",
     "Required once on platforms — can't use WhatsApp", 30, "Monthly sub",         "Not done",        "Platform provides tablet"),
]

comp_df = pd.DataFrame(compliance, columns=["item", "urgency", "cost_£", "timeline", "status", "source"])
comp_df["urgency_category"] = comp_df["urgency"].apply(
    lambda x: "LEGAL" if "LEGAL MUST" in x else "PLATFORM" if "platform" in x.lower() else "RECOMMENDED"
)
comp_df.to_csv(OUT / "compliance_checklist.csv", index=False)

total_setup_cost = comp_df["cost_£"].sum()
legal_cost = comp_df[comp_df["urgency_category"] == "LEGAL"]["cost_£"].sum()
print(f"  Total estimated setup cost   : £{total_setup_cost:,.0f}")
print(f"  Legal/compliance cost        : £{legal_cost:,.0f}  (registration is free)")
print(f"  Items requiring action       : {len(comp_df)}")
print(f"  Legal MUST items             : {len(comp_df[comp_df['urgency_category']=='LEGAL'])}")

# Chart 4: Compliance & cost breakdown
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Workstream 4: Compliance & Setup Requirements\n"
             "Sources: FSA (food.gov.uk) · GOV.UK · Deliveroo (Delta Digital 2025) · Uber Eats (Deliverect 2025)",
             fontsize=12, fontweight="bold", color=DGREY, y=1.01)

ax1 = axes[0]
cats = comp_df["urgency_category"].value_counts()
cat_colors = {"LEGAL": CORAL, "PLATFORM": AMBER, "RECOMMENDED": SKY}
wedges, texts, autotexts = ax1.pie(
    cats.values, labels=cats.index, colors=[cat_colors.get(c, SILVER) for c in cats.index],
    autopct="%1.0f%%", startangle=90, pctdistance=0.6,
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
for at in autotexts:
    at.set_fontsize(12); at.set_fontweight("bold"); at.set_color("white")
ax1.set_title("Compliance Items by Category\n(LEGAL = must complete before any trading)", fontsize=11)

ax2 = axes[1]
cost_items = comp_df[comp_df["cost_£"] > 0].sort_values("cost_£", ascending=True)
bar_colors_c = [cat_colors.get(c, SILVER) for c in cost_items["urgency_category"]]
short_labels = [item[:35] + "..." if len(item) > 35 else item
                for item in cost_items["item"]]
bars = ax2.barh(short_labels, cost_items["cost_£"], color=bar_colors_c, height=0.55, zorder=2)
for bar, val in zip(bars, cost_items["cost_£"]):
    ax2.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
             f"£{val:.0f}", va="center", fontsize=10, fontweight="bold")
ax2.set_xlabel("Estimated Cost (£)")
ax2.set_title(f"One-Off Setup Costs by Item\nTotal: £{total_setup_cost:,.0f} (most items are free)", fontsize=11)
ax2.set_xlim(0, 650)
ax2.grid(axis="x", alpha=0.2, zorder=1)

legend_handles = [mpatches.Patch(color=CORAL, label="Legal requirement"),
                  mpatches.Patch(color=AMBER, label="Platform requirement"),
                  mpatches.Patch(color=SKY,   label="Recommended")]
ax2.legend(handles=legend_handles, loc="lower right", fontsize=9)
plt.tight_layout()
save(fig, "04_compliance_setup.png")


# ══════════════════════════════════════════════════════════════════════════════
# WORKSTREAM 5 — 90-DAY IMPLEMENTATION ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
print("\n── WS5: 90-Day Implementation Roadmap ────────────────────────")

# Phased roadmap: Phase 1 (legal first), Phase 2 (platform), Phase 3 (scale)
roadmap = [
    # Phase, Week, Task, Owner, Cost, Dependency
    (1, "Week 1-2", "Register food business with local authority (28 days notice required)", "Founder", 0,    "NONE — do this first"),
    (1, "Week 1",   "Register as self-employed with HMRC",                                   "Founder", 0,    "None"),
    (1, "Week 1",   "Complete Level 2 Food Hygiene Certificate (online, 1 day)",             "Founder", 25,   "None"),
    (1, "Week 1-2", "Document allergen information for all 6 menu items",                    "Founder", 0,    "Menu standardisation done"),
    (1, "Week 2",   "Write HACCP-lite food safety management system (use FSA template)",     "Founder", 0,    "Food hygiene cert done"),
    (1, "Week 2-3", "Standardise menu to 6 permanent items with descriptions & weights",     "Founder", 0,    "None"),
    (1, "Week 3",   "Get public liability insurance quote and purchase",                     "Founder", 150,  "Business registered"),
    (1, "Week 3-4", "Source food-grade packaging with allergen labelling",                   "Founder", 100,  "Menu standardised"),
    (2, "Week 4-5", "Environmental Health kitchen inspection (council arranges post-reg)",   "Council", 0,    "Registration done"),
    (2, "Week 5",   "Professional product photography (6 items)",                            "Photographer", 200, "Menu standardised"),
    (2, "Week 5-6", "Apply to Deliveroo — upload menu, photos, pricing",                    "Founder", 510,  "5-star hygiene rating"),
    (2, "Week 5-6", "Apply to Uber Eats — faster onboarding than Deliveroo",                "Founder", 0,    "Food hygiene cert + photos"),
    (2, "Week 6-7", "Build simple website (Squarespace/Wix) with online ordering link",     "Founder", 200,  "None — run in parallel"),
    (2, "Week 7",   "Set up Google Business profile with photos and menu",                   "Founder", 0,    "Website live"),
    (2, "Week 7-8", "Soft launch: WhatsApp customers → ask for Deliveroo reviews",          "Founder", 0,    "Platform listings live"),
    (3, "Week 8-10","Monitor platform performance: accept rate, rating, cancellations",      "Founder", 0,    "Listed on platforms"),
    (3, "Week 9-10","Introduce 'Today's Special' as rotating daily item on platforms",       "Founder", 0,    "Stable base menu performing"),
    (3, "Week 10-12","Instagram page: post food photos, behind-scenes, daily special",       "Founder", 0,    "Photos available"),
    (3, "Week 11-12","Target 75 orders/day — review kitchen capacity and prep workflow",     "Founder", 0,    "Volume data from platforms"),
    (3, "Week 12",  "Review P&L: direct vs platform channel mix, adjust pricing if needed", "Founder", 0,    "Full month of data"),
]

roadmap_df = pd.DataFrame(roadmap, columns=["phase", "timing", "task", "owner", "cost_£", "dependency"])
roadmap_df.to_csv(OUT / "implementation_roadmap.csv", index=False)

total_cost_all = roadmap_df["cost_£"].sum()
print(f"  Total 90-day setup cost      : £{total_cost_all:,.0f}")
print(f"  Phase 1 tasks (legal first)  : {len(roadmap_df[roadmap_df['phase']==1])}")
print(f"  Phase 2 tasks (platform)     : {len(roadmap_df[roadmap_df['phase']==2])}")
print(f"  Phase 3 tasks (scale)        : {len(roadmap_df[roadmap_df['phase']==3])}")

# Chart 5: Revenue projection across 90 days + scenario
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle("Workstream 5: 90-Day Implementation Roadmap & Revenue Projection\n"
             "Phase 1: Legal setup (weeks 1-4) · Phase 2: Platform launch (weeks 5-8) · Phase 3: Scale (weeks 8-12)",
             fontsize=12, fontweight="bold", color=DGREY, y=1.01)

ax1 = axes[0]
weeks = np.arange(0, 13)
# Orders: stays at 30 through Phase 1, ramps once on platforms
orders_projected = [30,30,30,30,30, 35,45,55,65,75,85,95,100]
weekly_revenues  = [o * weighted_aov * 5 * (0.70 if o > 30 else 1.0) for o in orders_projected]

phase_colors = {1: CORAL, 2: AMBER, 3: GREEN}
for i, (week, revenue) in enumerate(zip(weeks, weekly_revenues)):
    phase = 1 if week < 4 else 2 if week < 8 else 3
    ax1.bar(week, revenue, color=phase_colors[phase], zorder=2, alpha=0.85, width=0.7)

ax1.axvline(4, color=CORAL, ls="--", lw=1.5, alpha=0.7)
ax1.axvline(8, color=AMBER, ls="--", lw=1.5, alpha=0.7)
ax1.text(2, max(weekly_revenues)*0.95, "Phase 1\nLegal Setup", ha="center", fontsize=9, color=CORAL, fontweight="bold")
ax1.text(6, max(weekly_revenues)*0.95, "Phase 2\nPlatform Launch", ha="center", fontsize=9, color=AMBER, fontweight="bold")
ax1.text(10, max(weekly_revenues)*0.95, "Phase 3\nScale", ha="center", fontsize=9, color=GREEN, fontweight="bold")
ax1.set_xlabel("Week")
ax1.set_ylabel("Weekly Revenue (£)")
ax1.set_title("Projected Weekly Revenue (Net After Commission)\nRevenue held flat in Phase 1 — all legal work", fontsize=11)
ax1.grid(axis="y", alpha=0.2, zorder=1)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:.0f}"))

ax2 = axes[1]
phases = ["Phase 1\n(Weeks 1-4)\nLegal & Setup", "Phase 2\n(Weeks 5-8)\nPlatform Launch", "Phase 3\n(Weeks 9-12)\nScale"]
costs  = [
    roadmap_df[roadmap_df["phase"]==1]["cost_£"].sum(),
    roadmap_df[roadmap_df["phase"]==2]["cost_£"].sum(),
    roadmap_df[roadmap_df["phase"]==3]["cost_£"].sum(),
]
focus  = ["Legal compliance,\nmenu standardisation,\nallergen docs",
          "Platform listing,\nphotography,\nwebsite",
          "Growth, reviews,\nInstagram,\ncapacity review"]
bars = ax2.bar(phases, costs, color=[CORAL, AMBER, GREEN], width=0.5, zorder=2)
for bar, cost, foc in zip(bars, costs, focus):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
             f"£{cost:.0f}", ha="center", fontsize=13, fontweight="bold")
    ax2.text(bar.get_x()+bar.get_width()/2, 20,
             foc, ha="center", fontsize=8, color="white" if cost > 100 else DGREY,
             va="bottom", style="italic")
ax2.set_ylabel("Setup Cost (£)")
ax2.set_title(f"Setup Cost by Phase\nTotal: £{sum(costs):,.0f}  |  Most costs are free admin tasks", fontsize=11)
ax2.grid(axis="y", alpha=0.2, zorder=1)
ax2.set_ylim(0, 850)

plt.tight_layout()
save(fig, "05_roadmap_and_revenue.png")

# ── CHART 6: Channel strategy — direct vs platform ────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle("Channel Strategy: Direct (WhatsApp) vs Platform vs Own Website\n"
             "Recommended hybrid: use platforms for discovery, convert repeat customers to direct ordering",
             fontsize=12, fontweight="bold", color=DGREY, y=1.01)

ax1 = axes[0]
channels = ["WhatsApp\n(current)", "Deliveroo\n(30%)", "Uber Eats\n(25%)", "Own Website\n(~3%)"]
prices   = [weighted_aov, PLATFORM_AOV, PLATFORM_AOV, weighted_aov * 1.10]
commissions = [0, 0.30, 0.25, 0.029]
receives = [p * (1-c) for p, c in zip(prices, commissions)]
cogs_all = [weighted_aov * COGS_PCT] * 4  # COGS stays same in £
gps      = [r - c for r, c in zip(receives, cogs_all)]
bar_cols = [NAVY, CORAL, AMBER, GREEN]

x = np.arange(4)
ax1.bar(x, receives, color=bar_cols, alpha=0.5, label="Restaurant receives", width=0.5, zorder=2)
ax1.bar(x, gps, color=bar_cols, alpha=0.95, label="Gross profit", width=0.5, zorder=3,
        bottom=[0]*4)
for i, (rec, gp, price) in enumerate(zip(receives, gps, prices)):
    ax1.text(i, rec + 0.1, f"Receives\n£{rec:.2f}", ha="center", fontsize=8)
    ax1.text(i, gp/2, f"GP\n£{gp:.2f}", ha="center", fontsize=8, fontweight="bold", color="white")

ax1.set_xticks(x); ax1.set_xticklabels(channels)
ax1.set_ylabel("£ per Order")
ax1.set_title("Channel Economics on Comparable Order\n(Platform orders priced 30% higher to absorb commission)", fontsize=11)
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.2, zorder=1)

ax2 = axes[1]
# Recommended long-term channel mix
mix_labels = ["Direct / WhatsApp\n(loyal customers)", "Deliveroo\n(discovery)", "Uber Eats\n(discovery)", "Own Website\n(target)"]
mix_current = [100, 0, 0, 0]
mix_month3  = [20, 40, 30, 10]
mix_month6  = [15, 30, 25, 30]

width = 0.25
x2 = np.arange(4)
ax2.bar(x2 - width, mix_current, width, color=CORAL,  label="Now (current state)", alpha=0.85)
ax2.bar(x2,         mix_month3,  width, color=AMBER,  label="Month 3 target",       alpha=0.85)
ax2.bar(x2 + width, mix_month6,  width, color=GREEN,  label="Month 6 target",       alpha=0.85)

ax2.set_xticks(x2); ax2.set_xticklabels(mix_labels, fontsize=9)
ax2.set_ylabel("% of Orders from Channel")
ax2.set_title("Recommended Channel Mix Evolution\nConvert platform customers to own website over time", fontsize=11)
ax2.legend(fontsize=9)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter())
ax2.grid(axis="y", alpha=0.2, zorder=1)
ax2.set_ylim(0, 115)
plt.tight_layout()
save(fig, "06_channel_strategy.png")

print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║  SUMMARY: TIFFIN BUSINESS TRANSFORMATION                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║  CRITICAL FIRST STEP: Register as food business (FSA). Cannot list on   ║
║  ANY platform without this. It is free and takes 28 days minimum.       ║
║                                                                          ║
║  PRICING: Current £6-8 WhatsApp prices CANNOT go on platforms as-is.   ║
║  Recommended platform price: ~30% higher (£7 → £9, £8 → £10.50)       ║
║  This absorbs the 30% commission while maintaining ~30% gross margin.   ║
║                                                                          ║
║  MENU: Consolidate from 8 daily options to 6 permanent platform items.  ║
║  Add allergen info (legal requirement). Get product photos (conversion). ║
║                                                                          ║
║  SETUP COST: £1,215 total one-off cost.                                 ║
║  ~£275 genuinely optional (photography + website) — everything else     ║
║  is either free (registration) or legally required.                     ║
║                                                                          ║
║  REVENUE POTENTIAL: At 100 orders/day (50 direct + 50 platform)         ║
║  the business generates ~£130K annual net revenue vs ~£58K today.       ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
