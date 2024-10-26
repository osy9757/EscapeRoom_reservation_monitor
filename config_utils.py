import json
from models import SiteConfig

def load_config(filename='config.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return [SiteConfig(**site) for site in data]