"""
Testes para o módulo 'parser.py'.

Este script verifica:

- Conexão bem-sucedida com URL especifica do site Pinterest.

- Se o parsing da página HTML para a retirada do link de imagem é realizado corretamente 
  utilizando os seletores corretos.

"""


import requests
from bs4 import BeautifulSoup


#Testes

def test_testando_conexao_pinterest(lista_url):

    ### Variáveis ###

    #Instancia do requests
    html = None

    ### Código ###

    for url in lista_url:

        html = requests.get(url)
        assert "Pinterest" in html.text


def test_testando_parsing_link(pagina_html):

    ### Variáveis ###

        #Instancia do BeautifulSoup
        soup = None

        #Tag <div> que contem a tag <img>
        div = None

        #Tag <img> que contem o link da imagem
        img = None

        ### Código ###

        soup = BeautifulSoup(pagina_html,"html.parser")

        #Seletores para encontrar o link da imagem
        div = soup.find("div",attrs={"data-test-id":"pin-closeup-image"})

        img = div.find("img")

        assert "i.pinimg.com" in img['src'] 
        assert ".jpg" in img['src']
       



