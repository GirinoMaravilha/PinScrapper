from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pytest


@pytest.fixture(params=["chrome","firefox"])
def driver(request):

    ### Variáveis ###

    #Um dos parametros da fixture
    param = ""

    #Instancia WebDriver
    d = None

    #Opções do driver
    options = None

    ### Código ###

    #Retirando um dos parametros do decorador da fixture
    param = request.param
    
    #Comparando valores para definir o driver correro do teste
    if param == "chrome":
        options = ChromeOptions()
        options.add_argument("--headless")
        d = webdriver.Chrome(options=options)
    
    else:
        options = FirefoxOptions()
        options.add_argument("--headless")
        d = webdriver.Firefox()
    
    #Retornando driver configurado para os workers
    yield d

    #Fazendo limpeza e encerrando o programa
    d.quit()







