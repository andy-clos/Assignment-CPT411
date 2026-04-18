# Assignment-CPT411

## How to start the program

### 1. Clone and open project
1. Clone the repository:
	git clone https://github.com/andy-clos/Assignment-CPT411.git
2. Move into the project folder:
	cd Assignment-CPT411

### 2. Install dependencies
1. create a virtual environment:
	python -m venv .venv
2. Activate it on Windows PowerShell:
	.\.venv\Scripts\Activate.ps1
3. Install required package:
	pip install -r requirements.txt

### 3. Run the main app (Streamlit UI)
1. Start the app:
	streamlit run app.py
2. Streamlit will show a local URL in terminal (usually http://localhost:8501).
3. Open that URL in your browser.
4. Paste text (or upload .txt), then click Run DFA to see:
	- accept/reject status
	- matched names and positions
	- highlighted text
	- DFA processing log