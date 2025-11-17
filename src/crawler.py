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
import logging
from utils import configurando_logger


#Classes

class CrawlerImagens:

    def __init__(self,logger:logging.Logger, lista_prompt:list[str]):

        self._driver = webdriver.Chrome()
        self._lista_prompt = lista_prompt
        self.logger = logger
    
    @property
    def driver(self):
        raise AttributeError("O atributo self._driver não pode ser acessado diretamente!")
    
    @driver.setter
    def driver(self, valor):
        raise AttributeError("O atributo self._driver não pode ter seu valor modificado!")
    
    async def bot_crawler(self, max_bots:int=3):
        
        ### Variáveis ###


        
        ### Código ###
        pass

        
        
#Função Main para DEBUG

def main():
    
    logger = configurando_logger()
    crawler = CrawlerImagens()



if __name__ == "__main__":
    main()
