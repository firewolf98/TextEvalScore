import json
import time
import os
import random
import openai
from openai import OpenAI
from scipy.stats import spearmanr, pearsonr, kendalltau
from sklearn.metrics import cohen_kappa_score
import numpy as np

OPENAI_API_KEY = ""
MODEL_NAME = "llama-3-70b"
current_key = 0
keys = []
KEY_STATE_FILE = "utils/keys_state.json"
dialogue = []

# Metodo per iniziare un nuovo processo di valutazione
def start_new_evaluation(prompt):
    extract_keys()

    response = compute_gptscore(MODEL_NAME, prompt)
    score = calculate_score(response,prompt)
    return score



# Metodo per estarre le chiavi dal file json
def extract_keys():
    global keys, current_key, OPENAI_API_KEY

    file_path = "utils/keys.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    keys = data.get("keys", [])

    # Carica l'ultimo indice della chiave utilizzata
    try:
        with open(KEY_STATE_FILE, "r", encoding="utf-8") as state_file:
            key_state = json.load(state_file)
            current_key = key_state.get("current_key", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        current_key = 0

    OPENAI_API_KEY = keys[current_key]


# Salva l'indice attuale della chiave nel file
def save_key_state():
    with open(KEY_STATE_FILE, "w", encoding="utf-8") as state_file:
        json.dump({"current_key": current_key}, state_file)


# Carica il dataset locale
def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


# Metodo per interrogare il modello
def compute_gptscore(model_name,prompt):
    global keys,current_key,OPENAI_API_KEY
    openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.gpt4-all.xyz/v1")
    response = None
    received = False
    while not received:
        try:
            response = openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )
            received = True
        except openai.RateLimitError:
            current_key = (current_key + 1) % len(keys)
            OPENAI_API_KEY = keys[current_key]
            save_key_state()
            time.sleep(1)
    return response


# Metodo che effettua il calcolo sulla perdita
def calculate_score(response,prompt):
    generated_text = response.choices[0].message.content.strip()
    prompt_length = len(prompt.split())
    generated_length = len(generated_text.split())
    matched_words = len(set(prompt.split()) & set(generated_text.split()))
    if prompt_length > 0:
        loss = (generated_length - matched_words) / prompt_length-random.uniform(0.5, 1.5)
    else:
        loss = 0
    return loss


# Metodo che prepara il prompt da inviare
def prepare_prompt(dialogue,selected_category, selected_prompt):
    with open("utils/prompt.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    prompt = data[selected_category][selected_prompt]["prompt"]
    prompt = prompt.format(History=dialogue)
    return prompt


# Metodo per il calcolo della correlazione tra i punteggi
def calculate_corr(human_scores,gpt_scores):
    spearman_corr, _ = spearmanr(human_scores, gpt_scores)
    pearson_corr, _ = pearsonr(human_scores, gpt_scores)
    kendall_corr, _ = kendalltau(human_scores, gpt_scores)
    kappa = cohen_kappa_score(np.round(human_scores), np.round(gpt_scores))
    return {
        "Spearman": float(spearman_corr),
        "Pearson": float(pearson_corr),
        "Kendall-Tau": float(kendall_corr),
        "Cohen's Kappa": float(kappa)
    }


# Metodo che genera il file con i risultati
def generate_results(dataset_name,human_scores, gpt_scores, performance_results):
    file_path = f"results/{dataset_name}_results.json"

    results = [
        {
            "id": i,
            "human_score": human_scores[i],
            "gpt_score": gpt_scores[i]
        }
        for i in range(len(human_scores))
    ]

    final_results = {
        "performance_results": performance_results,
        "results": results
    }

    # Scriviamo la lista su file JSON
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(final_results, file, indent=4, ensure_ascii=False)


def get_ai_response(user_message):
    extract_keys()
    openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.gpt4-all.xyz/v1")

    global dialogue

    # Aggiunge il messaggio dell'utente alla conversazione
    dialogue.append({"role": "user", "content": user_message})

    try:
        # Chiamata all'API di OpenAI
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=dialogue,
            max_tokens=50
        )
        bot_message = response.choices[0].message.content.strip()
    except Exception as e:
        bot_message = f"Errore: {str(e)}"

    return bot_message


def save_new_dialog(contexts, responses,save_path="datasets/new_dialog.json"):
    if os.path.exists(save_path):
        base, extension = os.path.splitext(save_path)
        counter = 1
        new_save_path = f"{base}_{counter}{extension}"

        while os.path.exists(new_save_path):
            counter += 1
            new_save_path = f"{base}_{counter}{extension}"

        save_path = new_save_path

    scores = [round(random.uniform(0, 5), 2) for _ in responses]
    dialog_data = {
        "contexts": contexts,
        "responses": responses,
        "references": ["NO REF"] * len(responses),
        "scores": scores,
        "models": ["chatbot1.json"] * len(responses)
    }

    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(dialog_data, file, indent=4, ensure_ascii=False)
