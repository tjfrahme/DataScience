import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.rithmschool.com/blog')

soup = BeautifulSoup(response.text, 'html.parser')

print(response.text)
