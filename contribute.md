# Commands usefull

# First thing to do after cloning 
- uv sync 
# Init with uv 
- uv venv venv --python=3.10
# Activate venv 
- .venv\Scripts\activate
# UV pip freeze 
- uv pip freeze > requirements.txt
# UV pip install 
- uv pip install -r requirements.txt

# pipreqs
- python -m pipreqs.pipreqs C:\SRC\FinBot --encoding=utf-8 --force --ignore .venv

# Remove all docker files not used 
- sudo docker system prune -a --volumes -f
