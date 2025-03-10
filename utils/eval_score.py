import json
import time
import random
import openai
from openai import OpenAI

OPENAI_API_KEY = ""
MODEL_NAME = "llama-3-70b"
current_key = 0
keys = []
KEY_STATE_FILE = "utils/keys_state.json"

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
                max_tokens=2048
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