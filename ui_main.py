import tkinter as tk
from PIL import Image, ImageTk
import webbrowser
from tkinter import ttk,filedialog
from utils.eval_score import *


# Mostra il menu iniziale
def show_menu():
    clear_frame()
    show_image()

    # Messaggio di benvenuto
    label = tk.Label(frame,
                     text="Benvenuto su TextEvalScore! \nUn'applicazione per valutare la qualità dei testi generati dall'IA.",
                     font=("Arial", 14, "bold"),
                     fg="#f0ebd8",
                     bg="#1d2d44",
                     wraplength=500)
    label.pack(pady=(10, 10), anchor="center")

    # Bottoni del menu
    evaluate_button = create_rounded_button(frame, "Valuta un Testo", evaluate_text)
    view_results_button = create_rounded_button(frame, "Visualizza risultati precedenti", view_results)
    credits_button = create_rounded_button(frame, "Crediti", credits)
    exit_button = create_rounded_button(frame, "Esci", exit_app)


# Frame della scelta di valutazione del testo
def evaluate_text():
    clear_frame()
    show_image()

    # Messaggio informativo
    text_label = tk.Label(frame,
                          text="Utilizza TextEvalScore per effettuare la valutazione di un testo generato da un'Intelligenza Artificiale. "
                               "Puoi selezionare un dataset contenente i testi da analizzare (Se non effettui la scelta viene usato quello di default) "
                               "oppure interagire con l'applicativo per generare un nuovo testo da far valutare.\n\n"
                               "NB. Il dataset deve essere strutturato con le informazioni: contexts, responses, references, scores e models.",
                          font=("Arial", 12),
                          fg="#f0ebd8",
                          bg="#1d2d44",
                          wraplength=500)
    text_label.pack(pady=(20, 10), anchor="center")

    # Bottone per effettuare una nuova valutazione
    new_evaluation_button = create_rounded_button(frame, "Effettua una nuova valutazione", select_prompt)
    new_textToEvaluate_button = create_rounded_button(frame, "Genera del nuovo testo da valutare", perform_new_evaluation)
    back_button = create_rounded_button(frame, "Torna al menu", show_menu)


# Metodo che gestisce la finestra della nuova elaborazione
def perform_new_evaluation(selected_category, selected_prompt):
    # Crea una finestra di dialogo personalizzata
    dialog = tk.Toplevel(root)
    dialog.title("Nuova Valutazione")
    dialog_width = 400
    dialog_height = 200
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x_coordinate = (screen_width // 2) - (dialog_width // 2)
    y_coordinate = (screen_height // 2) - (dialog_height // 2)
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x_coordinate}+{y_coordinate}")
    dialog.configure(bg="#1d2d44")

    # Messaggio di richiesta
    label = tk.Label(dialog,
                     text="Vuoi selezionare il dataset o usare quello di default?",
                     font=("Arial", 12),
                     fg="#f0ebd8",
                     bg="#1d2d44",
                     wraplength=300)
    label.pack(pady=(20, 10))

    # Funzione per gestire la selezione del dataset
    def select_dataset():
        # Finestra di dialogo per aprire un file
        file_path = filedialog.askopenfilename(title="Seleziona un file JSON",
                                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                dataset = load_dataset(file_path)
                dialog.destroy()
                start_elaboration(dataset,selected_category, selected_prompt)
            except Exception as e:
                tk.messagebox.showerror("Errore", "Impossibile caricare il file JSON. Verifica il formato.")
        dialog.destroy()

    def use_default_dataset():
        print("Hai scelto di utilizzare il dataset di default.")
        # Logica per utilizzare il dataset di default (da implementare)
        dialog.destroy()

    # Bottoni per la selezione del dataset
    select_button = tk.Button(dialog, text="Seleziona Dataset", command=select_dataset,
                              font=("Arial", 12), bg="#748cab", fg="#000000")
    select_button.pack(pady=(10, 5))
    default_button = tk.Button(dialog, text="Dataset di default", command=use_default_dataset,
                               font=("Arial", 12), bg="#748cab", fg="#000000")
    default_button.pack(pady=(5, 10))


# Metodo che gestisce la scelta dei prompt da usare
def select_prompt():
    with open("utils/prompt.json", "r", encoding="utf-8") as file:
        prompt_data = json.load(file)

    # Crea una finestra di dialogo personalizzata
    dialog = tk.Toplevel(root)
    dialog.title("Seleziona prompt")
    dialog_width = 500
    dialog_height = 300
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x_coordinate = (screen_width // 2) - (dialog_width // 2)
    y_coordinate = (screen_height // 2) - (dialog_height // 2)
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x_coordinate}+{y_coordinate}")
    dialog.configure(bg="#1d2d44")

    # Messaggio di richiesta
    label = tk.Label(dialog,
                     text="Quale prompt vuoi usare?",
                     font=("Arial", 12),
                     fg="#f0ebd8",
                     bg="#1d2d44",
                     wraplength=300)
    label.pack(pady=(20, 10))

    # Dropdown per selezionare la categoria
    categories = list(prompt_data.keys())
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(dialog, textvariable=category_var, values=categories, state="readonly")
    category_dropdown.pack(pady=5)
    category_dropdown.set("Scegli una categoria")

    # Dropdown per selezionare il prompt
    prompt_var = tk.StringVar()
    prompt_dropdown = ttk.Combobox(dialog, textvariable=prompt_var, state="readonly")
    prompt_dropdown.pack(pady=5)
    prompt_dropdown.set("Scegli un prompt")

    # Label per mostrare il prompt selezionato
    prompt_label = tk.Label(dialog, text="", font=("Arial", 10), fg="white", bg="#1d2d44", wraplength=400,
                            justify="left")
    prompt_label.pack(pady=10)

    def update_prompts(event):
        """Aggiorna il menu dei prompt in base alla categoria selezionata."""
        selected_category = category_var.get()
        if selected_category in prompt_data:
            prompts = list(prompt_data[selected_category].keys())
            prompt_dropdown["values"] = prompts
            prompt_dropdown.set(prompts[0])
            show_prompt()

    def show_prompt(*args):
        """Mostra il prompt selezionato sotto il menu a discesa."""
        selected_category = category_var.get()
        selected_prompt = prompt_var.get()
        if selected_category and selected_prompt:
            prompt_text = prompt_data[selected_category].get(selected_prompt, {}).get("prompt",
                                                                                      "Nessun prompt trovato.")
            prompt_label.config(text=f"Prompt:\n{prompt_text}")

    def confirm_selection():
        """Passa la selezione a function() e chiude la finestra."""
        selected_category = category_var.get()
        selected_prompt = prompt_var.get()

        if selected_category and selected_prompt:
            perform_new_evaluation(selected_category, selected_prompt)
            dialog.destroy()

    # Associa la funzione di aggiornamento alla selezione della categoria
    category_dropdown.bind("<<ComboboxSelected>>", update_prompts)
    prompt_dropdown.bind("<<ComboboxSelected>>", show_prompt)

    # Bottone di conferma selezione
    confirm_button = tk.Button(dialog, text="Conferma", font=("Arial", 12),
                               bg="#748cab", fg="#000000",
                               command=confirm_selection)
    confirm_button.pack(pady=10)


# Metodo che gestisce la finestra di avanzamento dell'elaborazione
def start_elaboration(dataset,selected_category, selected_prompt):
    clear_frame()
    show_image()

    # Creazione della barra di avanzamento
    progress_label = tk.Label(frame, text="Elaborazione in corso...", font=("Arial", 12))
    progress_label.pack(pady=10)
    progress = ttk.Progressbar(frame, length=300, mode="determinate")
    progress.pack(pady=10)
    total = len(dataset["contexts"])
    progress["maximum"] = total

    for i in range(total):
        dialog = " ".join(dataset["contexts"][i])
        dialog = f"{dialog} Response: {dataset['responses'][i]}"
        prompt = prepare_prompt(dialog, selected_category, selected_prompt)
        score = start_new_evaluation(prompt)
        print(score)
        progress["value"] = i + 1
        root.update_idletasks()

    progress_label.config(text="Elaborazione completata!")

# Frame della scelta di visualizzazione dei risultati delle varie valutazioni effettuate
def view_results():
    # Logica per visualizzare i risultati precedenti (da implementare)
    pass


# Frame dei crediti dell'applicazione
def credits():
    clear_frame()

    title_label = tk.Label(frame, text="Autori:", font=("Arial", 16, "bold"), fg="#f0ebd8", bg="#1d2d44")
    title_label.pack(pady=(10, 5))

    # Immagini degli autori
    luca_image = Image.open("images/luca.png")
    luca_image = luca_image.resize((100, 100))
    luca_logo = ImageTk.PhotoImage(luca_image)
    sara_image = Image.open("images/sara.png")
    sara_image = sara_image.resize((100, 100))
    sara_logo = ImageTk.PhotoImage(sara_image)

    # Crea un frame per le immagini
    authors_frame = tk.Frame(frame, bg="#1d2d44")
    authors_frame.pack(pady=10)
    luca_label = tk.Label(authors_frame, image=luca_logo, bg="#1d2d44")
    luca_label.image = luca_logo  # Mantieni riferimento all'immagine
    luca_label.pack(side=tk.LEFT, padx=(10, 20))
    luca_name = tk.Label(authors_frame, text="Luca Esposito", font=("Arial", 12), fg="#f0ebd8", bg="#1d2d44")
    luca_name.pack(side=tk.LEFT)
    sara_label = tk.Label(authors_frame, image=sara_logo, bg="#1d2d44")
    sara_label.image = sara_logo  # Mantieni riferimento all'immagine
    sara_label.pack(side=tk.LEFT, padx=(20, 10))
    sara_name = tk.Label(authors_frame, text="Onelia Sara Cataldo", font=("Arial", 12), fg="#f0ebd8", bg="#1d2d44")
    sara_name.pack(side=tk.LEFT)

    # Descrizione del progetto
    project_label = tk.Label(frame,
                             text="Il progetto è stato sviluppato per l'esame di Intelligenza Artificiale dell'indirizzo di Data Science & Machine Learning dell'Università degli Studi di Salerno.",
                             font=("Arial", 12),
                             fg="#f0ebd8",
                             bg="#1d2d44",
                             wraplength=500)
    project_label.pack(pady=(10, 10))
    github_button = create_rounded_button(frame, "Apri su GitHub", open_github)
    back_button = create_rounded_button(frame, "Torna al menu", show_menu)


# Funzione che apre sul browser la repository del progetto su GitHub
def open_github():
    webbrowser.open("https://github.com/firewolf98/TextEvalScore")


# Funzione per chiudere l'applicazione
def exit_app():
    root.quit()


# Pulisce il contenuto attuale della finestra
def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()


# Crea un bottone con lo stile definito
def create_rounded_button(parent, text, command):
    button = tk.Button(parent, text=text, command=command, font=("Arial", 12),
                       bg="#748cab", fg="#000000", relief="flat", borderwidth=0)
    button.pack(pady=10, ipadx=10, ipady=5)
    return button


# Metodo per mostrare l'immagine del logo nella finestra
def show_image():
    clear_frame()
    logo_image = Image.open("images/logo.png")
    logo_image = logo_image.resize((100, 100))
    logo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(frame, image=logo, bg="#1d2d44")
    logo_label.image = logo
    logo_label.pack(pady=(10, 0))


def main():
    global root,frame
    # Crea la finestra principale
    root = tk.Tk()
    root.title("TextEvalScore")
    root.iconbitmap("images/logo.ico")
    window_width = 600
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    root.configure(bg="#1d2d44")

    frame = tk.Frame(root, bg="#1d2d44")
    frame.pack(expand=True)

    show_menu()

    # Avvia l'interfaccia grafica
    root.mainloop()


if __name__ == "__main__":
    main()
