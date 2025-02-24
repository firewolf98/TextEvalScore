import openai
import numpy as np
import json
from scipy.stats import spearmanr, pearsonr, kendalltau
from sklearn.metrics import cohen_kappa_score

# Configurazione del modello OpenAI GPT-3
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY


def generate_prompt(text, aspect):
    """
    Crea un prompt per valutare un testo su un aspetto specifico.
    """
    return f"Valuta il seguente testo in base a {aspect}:\n{text}\nRisposta:"


def compute_gptscore(text, aspect):
    """
    Calcola GPTScore per un dato testo e aspetto utilizzando GPT-3.
    """
    prompt = generate_prompt(text, aspect)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=10
    )
    score = float(response["choices"][0]["message"]["content"].strip())
    return score




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

    texts = [" ".join(context) for context in data["contexts"]]  # Unisce le conversazioni in un unico testo
    human_scores = np.random.uniform(0, 1, len(texts)).tolist()  # Simula punteggi umani (se non disponibili nel dataset)
    return texts, human_scores


# Esegue il calcolo di GPTScore e la valutazione finale
def main():
    dataset_path = "dstc9_data.json"
    test_texts, human_scores = load_dataset(dataset_path)

    gpt_scores = [compute_gptscore(text, "coerenza") for text in test_texts]
    evaluation_results = evaluate_scores(gpt_scores, human_scores)

    print("GPT Scores:", gpt_scores)
    print("Valutazione rispetto ai giudizi umani:", evaluation_results)


if __name__ == "__main__":
    main()
