from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
import pytest
import time
import requests


# Fixtures do módulo 'test_crawler.py'

@pytest.fixture()
def driver(request):

    ### Variáveis ###

    #Instancia WebDriver
    d = None

    #Opções do driver
    options = None

    ### Código ###

    #Realizando configuração do chrome
    options = ChromeOptions()
    options.add_argument("--headless")
    d = webdriver.Chrome(options=options)
    
    #Retornando driver configurado para os workers
    yield d

    #Fazendo limpeza e encerrando o programa
    d.quit()


#Fixtures do módulo 'test_parser.py'

@pytest.fixture
def lista_url():
    yield ['https://br.pinterest.com/pin/41799102786179161/', 'https://br.pinterest.com/pin/2040762327287919/', 'https://br.pinterest.com/pin/32580797302853515/', 'https://br.pinterest.com/pin/1125968650715952/', 'https://br.pinterest.com/pin/14355292555640003/', 'https://br.pinterest.com/pin/2040762327232209/']

@pytest.fixture
def pagina_html():

    ### Variáveis ###

    #Resposta da função 'get' do módulo 'requests'
    r = None

    ### Código ###
    r = requests.get('https://br.pinterest.com/pin/41799102786179161/')
    if r.status_code == 200:
        yield r.text




