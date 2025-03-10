import time
import openai
import numpy as np
import json
import re
import os
from openai import OpenAI
from scipy.stats import spearmanr, pearsonr, kendalltau
from sklearn.metrics import cohen_kappa_score

# Configurazione del modello OpenAI GPT-3
OPENAI_API_KEY = "" #os.getenv("OPENAI_API_KEY") # $env:OPENAI_API_KEY="tuachiavequi"
MODEL_NAME = "gpt-3.5-turbo"
current_key = 0
keys = []

def extract_keys():
    global keys
    global OPENAI_API_KEY
    file_path = "utils/keys.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    keys = data.get("keys", [])
    OPENAI_API_KEY = keys[current_key]

def generate_prompt(text, aspect):
    """
    Crea un prompt specifico per la valutazione del testo basato sulla traccia.
    """
    return (
        f"Valuta il seguente testo in base a {aspect}:\n"
        f"{text}\n"
        "Rispondi SOLO con un numero tra 0 e 1 che rappresenta la probabilità condizionata."
    )


def extract_score(response_text):
    """
    Estrae il primo numero valido dalla risposta del modello.
    """
    match = re.search(r"\d+\.\d+", response_text)
    if match:
        return float(match.group(0))
    else:
        print(f"⚠️ Nessun numero trovato nella risposta: {response_text}")
        return 0.0

def compute_gptscore(text, aspect, max_retries=5):
    """
    Calcola GPTScore per un dato testo e aspetto utilizzando GPT-3.
    """
    global current_key
    global OPENAI_API_KEY
    openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.gpt4-all.xyz/v1")
    prompt = generate_prompt(text, aspect)
    print(f"\n▶️  Elaborazione testo: {text}...")

    wait_time = 5
    for attempt in range(max_retries):
        try:
            time.sleep(wait_time)
            response = openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )
            response_text = response.choices[0].message.content.strip()
            print(f"📝 Risposta {MODEL_NAME}: {response_text}")
            score = extract_score(response_text)
            print(f"✅ Punteggio estratto: {score}\n")
            return score
        except openai.RateLimitError:
            wait_time = 2 ** attempt
            print(f"⚠️ Rate Limit raggiunto. Attendo {wait_time} secondi prima di riprovare...")
            time.sleep(wait_time)
            current_key = current_key + 1
            OPENAI_API_KEY = keys[current_key]
        except Exception as e:
            print(f"❌ Errore durante la richiesta: {e}")
            return 0.0

    print("❌ Numero massimo di tentativi raggiunto. Assegno punteggio 0.0.")
    return 0.0


def evaluate_scores(gpt_scores, human_scores):
    """
    Confronta GPTScore con giudizi umani usando metriche statistiche.
    """
    spearman_corr, _ = spearmanr(gpt_scores, human_scores)
    pearson_corr, _ = pearsonr(gpt_scores, human_scores)
    kendall_corr, _ = kendalltau(gpt_scores, human_scores)
    kappa = cohen_kappa_score(np.round(gpt_scores), np.round(human_scores))
    return {
        "Spearman": spearman_corr,
        "Pearson": pearson_corr,
        "Kendall-Tau": kendall_corr,
        "Cohen's Kappa": kappa
    }


# Carica il dataset locale
def load_dataset(file_path):
    """
    Carica il dataset JSON e restituisce i testi e i punteggi umani.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    texts = [" ".join(context) for context in data["contexts"]]
    references = data.get("references", [])
    human_scores = data.get("scores", [])
    models = data.get("models", [])
    human_scores_float = [float(score) for score in human_scores]
    return texts, references, human_scores_float, models

# Stampa l'interfaccia grafica iniziale
def ui_interface():
    # Messaggio di benvenuto
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;34m" + "*" * 30 + "\033[0m")
    print("\033[1;32m" + "     TextEvalScore     \033[0m")
    print("\033[1;34m" + "*" * 30 + "\033[0m")
    print("\n\033[1;33m" + "Benvenuto su TextEvalScore!" + "\033[0m")
    print("\033[1;33m" + "Un'applicazione per valutare la qualità dei testi generati dall'IA." + "\033[0m")
    menu()


# Definisce il menu iniziale
def menu():
    print("\n\033[1;36m" + "Scegli un'opzione dal menu per iniziare:" + "\033[0m")  # Ciano
    print("1. Valuta un testo")
    print("2. Visualizza risultati precedenti")
    print("3. Esci")


# Salva risultati su file json
def save_results(models, human_scores, scores):
    file_path = "results.json"

    # Creiamo una lista di dizionari con chiavi fisse
    results = [
        {
            "model": models[i],
            "human_score": human_scores[i],
            **scores  # Inserisce tutte le metriche di evaluate_scores nel dizionario
        }
        for i in range(len(models))
    ]

    # Scriviamo la lista su file JSON
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


# Esegue il calcolo di GPTScore e la valutazione finale
def main():
    ui_interface()
    """
    extract_keys()

    dataset_path = "dstc9_data.json"
    test_texts, references, human_scores, models = load_dataset(dataset_path)

    gpt_scores = []
    for text in test_texts:
        score = compute_gptscore(text, "coerenza")
        gpt_scores.append(score)
        time.sleep(20)
    evaluation_results = evaluate_scores(gpt_scores, human_scores)

    save_results(models, human_scores, evaluation_results)
    """

if __name__ == "__main__":
    main()
