from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
import pytest
import time


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
    #options.add_argument("--headless")
    d = webdriver.Chrome(options=options)
    
    #Retornando driver configurado para os workers
    yield d

    #Fazendo limpeza e encerrando o programa
    d.quit()






