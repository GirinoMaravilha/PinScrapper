from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException

import time


#Testes

def test_verifica_interrupcao_bloco_login(driver:WebDriver) -> None:
        
    ### Variáveis ###

    #Instancias WebElement
    bloco_login = None
    botao_fechar = None

    #Lista com prompts
    lista_prompt = ["Cat","Dog","Mouse"]
        
    ### Código ###

    #Vamos forçar o bloco de login a aparecer fazendo varias requisições
    for prompt in lista_prompt:
        driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
        time.sleep(2)

    #Vamos tentar encontrar o bloco de login e fecha-lo
    bloco_login = driver.find_elements(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
    assert bloco_login
        
    if bloco_login:
        botao_fechar = bloco_login[0].find_element(By.XPATH,"//button[@aria-label='fechar']")
        botao_fechar.click()

        #Tentando capturar de novo para verificar se fechou
        bloco_login = driver.find_elements(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
        assert not bloco_login
