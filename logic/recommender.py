import csv


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract_average_yield(yield_text):
    try:
        nums = yield_text.split()[0]
        low, high = nums.split("–")
        return (float(low) + float(high)) / 2
    except:
        return None


def generate_explanation(soil, season, rainfall, crop):
    reasons = []

    if season == "rabi":
        reasons.append("the temperature is suitable for Rabi season")
    else:
        reasons.append("the crop fits well in Kharif season")

    if rainfall == "low":
        reasons.append("it performs well in low rainfall")
    elif rainfall == "high":
        reasons.append("it benefits from high rainfall")

    if soil in ["black", "loamy"]:
        reasons.append(f"{soil} soil retains nutrients well")

    return f"{crop.title()} is recommended because " + ", and ".join(reasons) + "."


def recommend(soil, season, rainfall, climate_mode=False):
    soil = soil.lower()
    season = season.lower()
    rainfall = rainfall.lower()

    rules = load_csv("data/crop_rules.csv")
    fertilizers = load_csv("data/fertilizer.csv")
    yields = load_csv("data/yield.csv")
    prices = load_csv("data/market_price.csv")

    # 🌍 Climate-resilient override
    if climate_mode:
        for r in rules:
            if r["soil"] == soil and r["crop"] in ["millets", "bajra", "pulses"]:
                explanation = generate_explanation(soil, season, rainfall, r["crop"])
                return build_response(r, fertilizers, yields, prices, explanation)

    # ✅ Exact rule match
    for r in rules:
        if (
            r["soil"] == soil
            and r["season"] == season
            and r["rainfall"] == rainfall
        ):
            explanation = generate_explanation(soil, season, rainfall, r["crop"])
            return build_response(r, fertilizers, yields, prices, explanation)

    # ⚠️ Fallback: soil + season
    for r in rules:
        if r["soil"] == soil and r["season"] == season:
            explanation = generate_explanation(soil, season, rainfall, r["crop"])
            return build_response(r, fertilizers, yields, prices, explanation)

    return None


def build_response(rule, fertilizers, yields, prices, explanation):
    crop = rule["crop"]

    fert = next((f for f in fertilizers if f["crop"] == crop), None)
    yld = next((y for y in yields if y["crop"] == crop), None)
    price = next((p for p in prices if p["crop"] == crop), None)

    income = "Not available"

    if yld and price:
        avg = extract_average_yield(yld["expected_yield"])
        if avg and price["unit"] == "₹/quintal":
            income = f"₹ {int(avg * float(price['market_price'])):,} / acre"
        else:
            income = f"Market price: ₹{price['market_price']} ({price['unit']})"

    return {
        "crop": crop.title(),
        "fertilizer": fert["fertilizer"] if fert else "N/A",
        "quantity": fert["quantity"] if fert else "N/A",
        "yield": yld["expected_yield"] if yld else "N/A",
        "income": income,
        "explanation": explanation
    }
