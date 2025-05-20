import json
from collections import Counter

# === Charger le fichier JSON existant ===
with open("entretiens_structures.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# === Compter toutes les thématiques ===
all_themes = []

for entretien in data:
    all_themes.extend(entretien.get("thématiques", []))

theme_counts = Counter(all_themes)

# === Calculer le TOP 10 des thématiques ===
top_10 = theme_counts.most_common(10)

# === Collecter les verbatims associés à chaque thématique ===
result_top_10 = []

for theme, count in top_10:
    verbatims_associes = []

    for entretien in data:
        if theme in entretien.get("thématiques", []):
            verbatims_associes.extend(entretien.get("verbatims", []))

    result_top_10.append({
        "thématique": theme,
        "occurrences": count,
        "verbatims": list(set(verbatims_associes))  # enlever doublons
    })

# === Sauvegarder le résultat dans un fichier JSON à part ===
with open("json10top.json", "w", encoding="utf-8") as f:
    json.dump(result_top_10, f, ensure_ascii=False, indent=4)

print("[OK] Fichier json10top.json créé avec TOP 10 et verbatims associés.")