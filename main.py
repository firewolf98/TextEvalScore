from utils.eval_score import *


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
    while True:
        print("\n\033[1;36m" + "Scegli un'opzione dal menu per iniziare:" + "\033[0m")
        print("1. Valuta un testo")
        print("2. Visualizza risultati precedenti")
        print("3. Esci")

        choice = input("Inserisci la tua scelta (1-3): ")

        if choice == "1":
            evaluate_text()
        elif choice == "2":
            view_results()
        elif choice == "3":
            print("Grazie per aver usato TextEvalScore")
            break
        else:
            print("\033[1;31m" + "Scelta non valida, riprova." + "\033[0m")


def evaluate_text():
    dataset = load_dataset("datasets/dstc9_data.json")
    total = len(dataset["contexts"])
    scores = []
    for i in range(total):
        dialog = " ".join(dataset["contexts"][i])
        dialog = f"{dialog} Response: {dataset['responses'][i]}"
        prompt = prepare_prompt(dialog, "FED_Turn_Level", "INT")
        score = start_new_evaluation(prompt)
        scores.append(score)
    results = calculate_corr(dataset["scores"], scores)
    generate_results("dstc9_data", dataset["scores"], scores, results)


def view_results(file_path="results/dstc9_data_results.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            # Stampa il contenuto del file
            print("\n\033[1;32m" + "Contenuto del file:" + "\033[0m")  # Verde
            print(json.dumps(data, indent=4, ensure_ascii=False))

    except FileNotFoundError:
        print("\033[1;31m" + f"Errore: Il file '{file_path}' non è stato trovato." + "\033[0m")  # Rosso
    except json.JSONDecodeError:
        print("\033[1;31m" + "Errore: Il file non è un JSON valido." + "\033[0m")  # Rosso
    except Exception as e:
        print(f"\033[1;31m" + f"Si è verificato un errore: {str(e)}" + "\033[0m")  # Rosso


def main():
    ui_interface()


if __name__ == "__main__":
    main()
