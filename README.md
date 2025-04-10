# TextEvalScore

An application based on GPTScore that provides an intuitive graphical interface for automated analysis and evaluation of textual datasets.


![alt text](<documentation/Home.png>)

## 📌 Description

**TextEvalScore** TextEvalScore is an interactive application based on the GPTScore framework, designed for the automated evaluation of textual datasets. It features an intuitive graphical interface that allows users to select evaluation prompts and reference datasets, providing detailed quality scores for generated texts. By leveraging advanced language models, TextEvalScore enables flexible and adaptable analysis of text quality, making it a valuable tool for researchers and developers working with natural language generation.

## 🛠️ Technologies Used

- **Python**: 3.11 
- **LLama**: Llama-3-70b

## 📁 Project Structure

- **datasets/** → Contains the datasets available for analysis and those generated through interaction with the model.
- **utils/** → Contains utility scripts and the JSON file with the keys.
- **results/** → Contains the results of the evaluations.
- **main.py** → File to start the command-line application.
- **ui_main.py** → File to start the application with the graphical interface.

## 🚀 Installation and Setup

### 1️⃣ Clone the repository

```sh
git clone https://github.com/firewolf98/TextEvalScore.git
cd TextEvalScore
```

### 2️⃣ Set Up the Conda Environment

Make sure you have Anaconda installed and running.

Create a new environment with the following command:

```sh
conda env create -n "env_name"
```

After doing this, you will have the environment ready to use.

To activate the environment, run:

```sh
conda activate "env_name"
```

Make sure you are in the project directory and have the environment activated, then run the following command:

```sh
pip install -r requirements.txt
```

### 3️⃣ Start the application

Before starting the application, insert the generated key(s) from gpt4all into the _keys.json_ file.

From the terminal, run

```sh
python main.py
```

if you want to start the application from the command line, or 

```sh
python ui_main.py
```

if you want to start it with a graphical interface.

## 📜 Authors

The authors of this project are:
- Luca Esposito (https://github.com/firewolf98) (https://www.linkedin.com/in/lucaesposito98/)
- Onelia Sara Cataldo (https://github.com/cataldosara98) (https://www.linkedin.com/in/onelia-sara-cataldo-6257861b0/)

Both are students of Data Science & Machine Learning at the University of Salerno.