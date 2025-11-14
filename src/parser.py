from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

import asyncio
from utils import configurando_logger


#Classes

class ParserImagens:

    def __init__(self, lista_prompt:list[str]):

        self._webdriver = webdriver.Chrome()
        self._lista_prompt = lista_prompt
    
    @property
    def webdriver(self):
        raise AttributeError("O atributo self._webdriver não pode ser acessado diretamente!")
    
    @webdriver.setter
    def webdriver(self):
        raise AttributeError("O atributo self._webdriver não pode ter seu valor modificado.")
    
    def parsing(self):
        pass

        
        
#Função Main

def main():
    
    parser = ParserImagens()
    print(parser.ola)
    parser.ola = "oi"
    parser.ola = 2
    print(parser.ola)


if __name__ == "__main__":
    main()
