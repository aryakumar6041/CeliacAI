# gluten_rules.py
import re

HIGH_RISK_KEYWORDS = ['wheat', 'barley', 'rye', 'malt', 'brewer',
                       'semolina', 'farina', 'durum', 'triticale', 'spelt']

MEDIUM_RISK_KEYWORDS = ['modified food starch', 'natural flavoring',
                         'maltodextrin', 'hydrolyzed vegetable protein',
                         'caramel color', 'dextrin', 'yeast extract', 'soy sauce', 'vinegar', 'starch', 'flour']


def _find_matches(keywords, text):
    matches = []
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text):
            matches.append(kw)
    return matches


def scan_ingredients(ingredient_text: str) -> dict:
    text = ingredient_text.lower()
    matched_high = _find_matches(HIGH_RISK_KEYWORDS, text)
    matched_medium = _find_matches(MEDIUM_RISK_KEYWORDS, text)

    if matched_high:
        status = "Contains Gluten"
        confidence = min(95, 70 + len(matched_high) * 10)
        recommendation = "Avoid"
        explanation = (
            "Flagged as likely containing gluten because the ingredient list "
            f"includes: {', '.join(matched_high)}."
        )
    elif matched_medium:
        status = "Possible Gluten Risk"
        confidence = min(75, 45 + len(matched_medium) * 10)
        recommendation = "Check further"
        explanation = (
            "This product contains ingredients that are sometimes derived from "
            f"gluten sources: {', '.join(matched_medium)}. Check with the "
            "manufacturer or look for a certified gluten-free label."
        )
    else:
        status = "No Obvious Gluten Found"
        confidence = 60
        recommendation = "Safe to consider"
        explanation = (
            "No known high-risk or medium-risk gluten keywords were found in "
            "the ingredient list you entered. This is not a guarantee — always "
            "check the full label for hidden gluten sources."
        )

    return {
        "status": status,
        "confidence": confidence,
        "matched_ingredients": matched_high + matched_medium,
        "explanation": explanation,
        "recommendation": recommendation,
    }
