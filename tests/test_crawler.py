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


# Classes

class MockCrawlerPinterest:

    """
    Um 'Mock' da classe 'CrawlerPinterest' localizada no modulo 'crawler' dentro do pacote 'src'.

    Classe usada para testar funcionalidades da classe de quem foi baseada.
    """

    def __init__(self, driver:WebDriver):
        
        self.driver = driver

    def test_verifica_interrupcao(self,lista_prompt:list[str]) -> None:
        
        """
        Método teste para verificar se o código do método original esta conseguindo encontrar e
        fechar o bloco de login, que é uma das interrupções que podem ocorrer durante o crawling
        do Pinterest.
        """
        #Vamos forçar o bloco de login a aparecer fazendo varias requisições

        for prompt in lista_prompt:
            self.driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
            time.sleep(2)

        #Vamos tentar encontrar o bloco de login e fecha-lo
        try:
            bloco_login = self.driver.find_element(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
            if bloco_login:
                botao_fechar = bloco_login.find_element(By.XPATH,"//button[@aria-label='fechar']")
                botao_fechar.click()

                #Tempo para verificar se a pagian de Login fechou
                time.sleep(5)

                return True
        
        #Caso não encontrar fazemos limpe-za e levantamos uma exceção
        except InvalidSelectorException as error:

            self.driver.quit()
            
            raise InvalidSelectorException
        
        except NoSuchElementException as error:

            self.driver.quit()
            
            raise NoSuchElementException


#Função Main para DEBUG direto sem o 'pytests'

def main():
    
    driver = webdriver.Chrome()
    lista_prompt = ['Lucy Heartfilia hot', 'Androi 18', 'Digimon 1 Mimi Adult']
    

    mockc = MockCrawlerPinterest(driver)
    mockc.test_verifica_interrupcao(lista_prompt)
    mockc.driver.quit()


if __name__ == "__main__":
    main()