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
        self.lista_prompt = lista_prompt
        self.logger = logger
    
    @property
    def driver(self):
        return self._driver
    
    @driver.setter
    def driver(self, valor):
        raise AttributeError("O atributo self._driver não pode ter seu valor modificado!")

    async def crawler_main(self):
        
        ### Variáveis ###


        #Instancia do asyncio.Task que recebe como argumento o método 'bot_crawler'
        bot_c = None

        ### Código ###

        #Iniciando iteração dos prompts
        self.logger.info("Crawler Iniciado!\n")
        self.logger.debug("Método 'crawler_main' iniciado, iniciando task 'bot_crawler' para" \
        "depositar, paginas HTML com imagens disponiveis, na pipeline")
        task = asyncio.create_task(self.bot_crawler)


    async def bot_crawler(self,max_img:int=10):
        
        ### Variáveis ###

        #Instancia WebDriverWait
        wait = WebDriverWait(self.driver, 5)

        #Lista que armazena quantidade de elementos contendo imagens
        lista_div_img = []
        
        ### Código ###

        #Iniciando iteração dos prompts
        self.logger.info("Entrando no site do Pinterest....")
        self.logger.debug("Método 'crawler_main' iniciado, iniciando itereção de valores da lista" \
        "'self.lista_prompt'")
        for prompt in self.lista_prompt:
            #Entrando no site e achando o input de pesquisa
            self.logger.info("Começando a procurar imagens")
            self.driver.get("https://br.pinterest.com/ideas")

        
        
#Função Main para DEBUG

def main():

    #Testando instancia do CrawlerImagens e geração de bots com uma Queue
    mock_lista_prompt = ["Lucy Heartfilia", "Nami", "Zelda"] 
    logger = configurando_logger()
    crawler = CrawlerImagens(logger,mock_lista_prompt)
    crawler.driver.quit()



if __name__ == "__main__":
    main()
