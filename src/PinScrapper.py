"""
Docstring for PinScrapper
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
#from selenium.webdriver.firefox.options import Options as FirefoxOptions
#from selenium.webdriver.edge.options import Options as EdgeOptions
#from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.remote.webdriver import WebDriver

from crawler import CrawlerPinterest,Crawler
from parser import ParserHTMLPinterest, ParserHTML
from downloader import Downloader
from utils import configurando_logger
from traceback import format_exc
from utils import configurando_argparse
from utils import lista_prompts
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

    def principal(self, crawler:Crawler, parser:ParserHTML, downloader:Downloader):
        
        ### Variáveis ###

        #Instancia da classe 'CrawlerPinterest'
        c = None

        #Instancia da classe 'ParserHTMLPinterest
        p = None

        #Instancia da classe 'Downloader'
        d = None

        #Dicionário contendo listas de links de pins gerados por prompts especificos
        dict_lista_links_pin = {}

        #Dicionario contendo listas de links de imagem para serem requisitadas e salvas no SO
        dict_lista_links_img = {}

        ### Código ###

        self.logger.debug("[PRINCIPAL] Método principal iniciado!")

        #Iniciando instancia do crawler e chamando método para conseguir os links de cada pin
        c = crawler(self.driver,self.logger,self.lista_prompt)
        self.logger.info("\n\nPesquisando as imagens...")
        print("\n")
        dict_lista_links_pin = c.bot_crawler(max_img=self.max_img)

        #Iniciando instancia do parser e chamando métodos assíncrono para conseguir os links de cada imagem
        p = parser(dict_lista_links_pin,self.logger)
        self.logger.info("\n\nIniciando coleta do link de cada imagem!")
        print("\n")
        dict_lista_links_img = asyncio.run(p.parsing())

        #Iniciando instancio do downloades e chamando método assincrono para baixar todas as imagens e salva-las no SO
        d = downloader(self.logger, dict_lista_links_img)
        self.logger.info("\n\nFazendo o downloads das imagem...")
        print("\n")
        asyncio.run(d.downloading())

        #Finalizando programa
        self.logger.info("\nDownload de todas as imagens finalizado! Encerrando PinScrapper...")


#Função Main

def main():
    
    ### Variáveis ###

    #Instancia do 'Logger'
    logger = None

    #Instancias do 'ArgumentParser'
    argumentparser = None

    #Sub-Classe da classe abstrata 'Crawler'
    crawler = None

    #Sub-Classe da classe abstrate 'ParserHTML'
    parserhtml = None

    #Argumentos passados na linha de comando do console
    args = None

    #Classe Downloader
    downloader = None

    #Instancia da classe Options do módulo selenium.webdriver.chrome
    options = None

    #Quantidade de imagens
    img_quant = 10

    #Lista contendo os prompts passados pelo usuário
    lista_prompt = []

    #Driver utilizado pelo 'Crawler'
    driver = None

    ### Código ###

    #Iniciando instancias que vão ser utilizadas
    crawler = CrawlerPinterest
    parserhtml = ParserHTMLPinterest
    downloader = Downloader

    #Retirando argumentos passados no console pelo usuário
    argumentparser = configurando_argparse()
    args = argumentparser.parse_args()
    
    #Verificando argumentos
    #Modo depuração
    if args.debug:
        logger = configurando_logger(debug_mode=True)
    else:
        logger = configurando_logger()
    
    #Modo monitor
    if not args.monitor:
        options = ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome()

    #Quantidade de imagens
    if not args.img_q:
        img_quant = 10
    else:
        img_quant = int(args.img_q)
    
    #Prompts fornecidos
    lista_prompt = lista_prompts(args.prompts)

    #DEBUG
    #print(f"Lista de prompt => {lista_prompt}\nDebug => {args.debug}\nMonitors => {args.monitor}\nQuantidade imagens => {img_quant}\n Tipo do argumento 'img_q' => {type(args.img_q)}")
    #return

    
    try:
        pinscrapper = PinScrapper(logger,lista_prompt,driver,img_quant)
        pinscrapper.principal(crawler,parserhtml,downloader)
    
    except KeyboardInterrupt as error:
        logger.info("\nInterrupção do teclado detectada! Encerrando o programa....")
    
    except Exception as error:
        logger.info("Uma exceção ocorreu! Verifique o log dela no arquivo 'Error.log'")
        logger.error(f"Erro!\nExceção =>{error}\nTraceback => {format_exc()}")


if __name__ == "__main__":
    main()
