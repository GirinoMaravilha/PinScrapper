"""
Docstring for PinScrapper
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
#from selenium.webdriver.firefox.options import Options as FirefoxOptions
#from selenium.webdriver.edge.options import Options as EdgeOptions
#from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.remote.webdriver import WebDriver

from src.crawler import CrawlerPinterest
from src.parser import ParserHTMLPinterest
from src.downloader import Downloader
from src.utils import configurando_logger
import argparse
import logging
import asyncio


# Classes
class PinScrapper:

    def __init__(self, logger:logging.Logger, lista_prompt:list[str], driver:WebDriver, max_img:int):

        self.logger = logger
        self.lista_prompt = lista_prompt
        self.driver = driver
        self.max_img = max_img

    def principal(self):
        
        ### Variáveis ###

        #Instancia da classe 'CrawlerPinterest'
        crawler = None

        #Instancia da classe 'ParserHTMLPinterest
        parser = None

        #Instancia da classe 'Downloader'
        download = None

        #Dicionário contendo listas de links de pins gerados por prompts especificos
        dict_lista_links_pin = {}

        #Dicionario contendo listas de links de imagem para serem requisitadas e salvas no SO
        dict_lista_links_img = {}

        ### Código ###

        self.logger.debug("[PRINCIPAL] Método principal iniciado!")

        #Iniciando instancia do crawler e chamando método para conseguir os links de cada pin
        crawler = CrawlerPinterest(self.driver,self.logger,self.lista_prompt)
        dict_lista_links_pin = crawler.bot_crawler(max_img=self.max_img)

        #Iniciando instancia do parser e chamando métodos assíncrono para conseguir os links de cada imagem
        parser = ParserHTMLPinterest(dict_lista_links_pin,self.logger)
        dict_lista_links_img = asyncio.run(parser.parsing())

        #Iniciando instancio do downloades e chamando método assincrono para baixar todas as imagens e salva-las no SO
        download = Downloader(self.logger, dict_lista_links_img)
        asyncio.run(download.downloading())


#Função Main

def main():
    pass


if __name__ == "__main__":
    main()
