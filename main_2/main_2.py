import os
import json
import tiktoken
from dotenv import load_dotenv
import groq

# === Charger .env ===
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLAMA_MODEL = os.getenv("LLAMA_MODEL")

if not GROQ_API_KEY or not LLAMA_MODEL:
    raise ValueError("GROQ_API_KEY ou LLAMA_MODEL manquant dans le .env")

FOLDER_PATH = "output_2"
OUTPUT_JSON = "entretiens_structures.json"
MAX_TOKENS = 5000  # On prend une marge sous la limite de 6000

client = groq.Groq(api_key=GROQ_API_KEY)

# === Compteur de tokens ===
enc = tiktoken.encoding_for_model("gpt-4")  # Pas grave si on met gpt-4, ça compte correctement

def count_tokens(text):
    return len(enc.encode(text))

def split_text_by_tokens(text, max_tokens):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if count_tokens(" ".join(current_chunk)) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# === Fonction IA ===
def extraire_themes_verbatims(texte):
    prompt = f"""
Voici un extrait d'entretien sociologique. 
Il peut contenir des thématiques et des verbatims.

Ta tâche est de :
1.⁠ ⁠Identifier les *thématiques*.
2.⁠ ⁠Identifier les *verbatims*.

Format réponse :

Thématiques:
•⁠  ⁠thématique 1
•⁠  ⁠thématique 2

Verbatims:
•⁠  ⁠"verbatim 1"
•⁠  ⁠"verbatim 2"

Contenu :

{texte}
"""

    response = client.chat.completions.create(
        model=LLAMA_MODEL,
        messages=[
            {"role": "system", "content": "Tu es un expert en analyse qualitative."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# === Traitement ===
data = []

for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".txt"):
        file_path = os.path.join(FOLDER_PATH, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            contenu = f.read()

        print(f"[INFO] Traitement de : {filename}")

        all_thematiques = []
        all_verbatims = []

        # Découpe par tokens
        chunks = split_text_by_tokens(contenu, MAX_TOKENS)

        for chunk in chunks:
            result = extraire_themes_verbatims(chunk)

            thematiques = []
            verbatims = []

            lines = result.splitlines()
            current_section = None

            for line in lines:
                line = line.strip()

                if line.lower().startswith("thématiques:"):
                    current_section = "thematiques"
                    continue
                elif line.lower().startswith("verbatims:"):
                    current_section = "verbatims"
                    continue

                if current_section == "thematiques" and line.startswith("-"):
                    thematiques.append(line[1:].strip())
                elif current_section == "verbatims" and line.startswith("-"):
                    verbatims.append(line[1:].strip().strip('"'))

            all_thematiques.extend(thematiques)
            all_verbatims.extend(verbatims)

        data.append({
            "entretien": filename,
            "thématiques": list(set(all_thematiques)),
            "verbatims": list(set(all_verbatims))
        })

# === Sauvegarde JSON ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"[OK] JSON structuré créé → {OUTPUT_JSON}")