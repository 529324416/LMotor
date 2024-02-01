


import requests


result = requests.post("http://localhost:8000/api/spider/ehentai", json={"url": "https://e-hentai.org/g/2815913/9054097b9e/"})
print(result.text)


