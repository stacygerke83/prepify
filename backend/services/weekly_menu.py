# services/weekly_menu.py
from typing import List, Dict, Any

def primary_ingredient(recipe: Dict[str, Any]) -> str:
    used = recipe.get("usedIngredients") or []
    missed = recipe.get("missedIngredients") or []
    if used:
        return used[0].lower()
    if missed:
        return missed[0].lower()
    return ""

def generate_weekly_menu(recipes: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    if not recipes:
        return []
    selected = []
    recent_primary: List[str] = []
    by_primary: Dict[str, List[Dict[str, Any]]] = {}

    for r in recipes:
        p = primary_ingredient(r)
        by_primary.setdefault(p, []).append(r)

    primaries = list(by_primary.keys())
    idx = 0

    while len(selected) < min(days, len(set([r["id"] for r in recipes]))):
        if not primaries:
            break
        p = primaries[idx % len(primaries)]
        bucket = by_primary.get(p, [])
        chosen = None
        for r in bucket:
            if any(r["id"] == sr["id"] for sr in selected):
                continue
            if p and p in recent_primary[-3:]:
                continue
            chosen = r
            break
        if chosen:
            selected.append(chosen)
            recent_primary.append(p)
        else:
            primaries.remove(p)
        idx += 1
        if idx > 1000:
            break

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    menu = []
    for i, r in enumerate(selected[:days]):
        menu.append({
            "dayIndex": i,
            "dayName": day_names[i % 7],
            "recipe": r
        })
    return menu
