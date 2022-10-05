uvicorn main:app --reload
ngrok http 8000

# Generate requirements.txt
pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
pip list --outdated

pip3 freeze > requirements.txt

# On lab pc
If PowerShell: Set-ExecutionPolicy Unrestricted -Scope Process
python -m pip install --upgrade pip
python -m venv .venv
cd .venv
Scripts\activate
cd ..
pip install -r requirements.txt --upgrade
uvicorn main:app