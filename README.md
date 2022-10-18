uvicorn main:app --reload
ngrok http 8000
lt --port 8000

git add .
git commit -m "Fix requirements"
git push -u origin main

# Generate requirements.txt
pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
pip list --outdated

pip3 freeze > requirements.txt

# On lab pc
If PowerShell: Set-ExecutionPolicy Unrestricted -Scope Process
python -m pip install --upgrade pip
python -m venv .venv
[Ubuntu] source .venv/bin/activate
cd .venv
Scripts\activate
cd ..
pip install -r requirements.txt --upgrade
uvicorn main:app

tmux new -slocaltunnel
ctrl-b d
tmux new -suvicorn

tmux a -tlocaltunnel
ctrl-b w