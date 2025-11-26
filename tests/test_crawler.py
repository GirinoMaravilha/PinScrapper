"""
Testes para o módulo 'crawler.py'.

Este script verifica:

- Conexão bem-sucedida com URL especifica para pesquisa de imagens no Pinterest.

- Localização e captura do bloco 'login', que pode interromper o fluxo do crawler.

- Captura de tags '<a>' de cards da pagina retornada de pesquisa.

"""


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

import time


#Testes

def test_testando_url_pinterest(driver:WebDriver) -> None:

    ### Variáveis ###

    #Prompt de teste
    prompt = "Dog"

    ### Código ###

    driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
    assert "Pinterest" in driver.title
    driver.quit()


def test_verifica_interrupcao_bloco_login(driver:WebDriver) -> None:
        
    ### Variáveis ###

    #Instancias WebElement
    bloco_login = None
    botao_fechar = None

    #Lista com prompts
    lista_prompt = ["Cat","Dog","Mouse"]
        
    ### Código ###

    #Forçando o bloco de login a aparecer fazendo varias requisições
    for prompt in lista_prompt:
        driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
        time.sleep(2)

    #Tentando encontrar o bloco de login 
    bloco_login = driver.find_elements(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
    assert bloco_login
    
    #Fechando o bloco login
    if bloco_login:
        botao_fechar = bloco_login[0].find_element(By.XPATH,"//button[@aria-label='fechar']")
        botao_fechar.click()

        #Tentando capturar de novo para verificar se fechou
        bloco_login = driver.find_elements(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
        assert not bloco_login
        driver.quit()


def test_verifica_captura_pins(driver:WebDriver) -> None:

    ### Variáveis ###

    #Instancia WebDriverWait
    wait = WebDriverWait(driver,10)

    #Prompt para teste
    prompt = "Dog"

    #Numero de pins para capturar
    max_img = 20

    #Lista de WebElements capturados
    lista_pins = []

    ### Código ###

    #Entrando no site e tentando pegar as tags '<a>' de cada pin referente a quantidade estabelecida
    driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
    assert "Pinterest" in driver.title

    while True:
        lista_pins = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[@data-test-id='pinWrapper'] //a")))
        assert lista_pins

        if len(lista_pins) < max_img:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        else:
            break
    
    assert len(lista_pins[0:max_img]) == max_img






