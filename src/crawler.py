from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


import asyncio
import logging
from utils import configurando_logger
from utils import mock_parser


#Classes

class CrawlerImagens:

    def __init__(self,logger:logging.Logger, lista_prompt:list[str]):

        self._driver = webdriver.Chrome()
        self.lista_prompt = lista_prompt
        self.logger = logger
        self._lista_cache= []
        #TODO Corrigir, ou apagar o cacheamento!
        
    @property
    def driver(self):
        return self._driver
    
    @driver.setter
    def driver(self, valor):
        raise AttributeError("O atributo self._driver não pode ter seu valor modificado diretamente!")
    
    @property
    def lista_cache(self):
        return self._lista_cache
    
    @lista_cache.setter
    def lista_cache(self,valor):
        raise AttributeError("O atributo self._lista_cache não pode ter seu valor modificado diretamente!")

    def bot_crawler(self,max_img:int=10) -> dict[str:str]:
        
        ### Variáveis ###

        #Instancia WebDriverWait
        wait = WebDriverWait(self.driver, 5)

        #Lista que armazena quantidade de elementos contendo imagens
        lista_div_img = []

        #Dicionario que armazena cada pagina HTML com a chave sendo seu respectivo prompt
        dict_pagina_html = {}
        
        ### Código ###

        #Iniciando iteração dos prompts

        self.logger.info("Crawler Iniciado!\n")
        self.logger.debug("[BOT-CRAWLER] Iniciando método 'bot_crawler' para retornar paginas HTML com links de PIN's disponíveis.")

        self.logger.info("Entrando no site do Pinterest....")
        self.logger.debug("[BOT-CRAWLER] Método 'crawler_main' iniciado, iniciando itereção de valores da lista" \
        "'self.lista_prompt'")

        for prompt in self.lista_prompt:
            #Entrando no site e achando o input de pesquisa
            self.logger.info(f"Começando a procurar imagens do prompt => {prompt}")
            self.logger.debug(f"[BOT-CRAWLER] Entrando no link do pinterest => https://br.pinterest.com/search/pins/?q={prompt}&rs=typed'")

            self.driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")

            #Inciando iteração para verificar se a quantidade de imagens no HTML Estático corresponde ao valor de 'max_img'.
            self.logger.debug("[BOT-CRAWLER] Verificando a quantidade de elementos contendo as imagens na página " \
            "e se correspondem com o argumento 'max_img'.")
            while True:
                #Tentando encontrar os elementos contendo as imagens na pagina
                try:
                    lista_div_img = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='V3gVHw' and @role='listitem']")))

                    #Veririfcando se a quantidade bate com a que foi requisitada
                    if len(lista_div_img) < max_img:
                        self.logger.info(f"Achamos apenas {len(lista_div_img)} imagens para o prompt => {prompt}")
                        self.logger.info("Vamos procurar mais....")
                        
                        #Vamos "rolar" a tela para baixo e tentar fazer o javascript revelar mais imagens
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    else:
                        #Salvando o HTML estatico no dicionario 'dict_pagina_html' tendo a chave como prompt
                        self.logger.debug(f"[BOT-CRAWLER] Achamos {len(lista_div_img)} imagens da requisição de {max_img} imagens.")
                        self.logger.info(f"Achamos todas as imagens! Salvando a pagina do prompt => {prompt}")
                        dict_pagina_html[prompt] = self.driver.page_source
                        break
                
                except TimeoutException as error:
                    #Tratando o problema do bloco de login "congelando" a página
                    self.logger.debug(f"[BOT-CRAWLER] Exceção 'TimeoutException' levantada com o prompt => {prompt}")
                    self.logger.info(f"Bloco de login apareceu no prompt => {prompt}")
                    self.logger.info(f"Fechando ele para continuar com o fluxo...")

                    self.verifica_bloco_login()
        
        #Retornando dicionario com as paginas HTML
        self.logger.debug("[BOT-CRAWLER] Iteração de todos os prompts terminada, retornando o dicionario 'dict_pagina_html'.")
        self.logger.info("Captura das páginas terminada!")
        return dict_pagina_html
                        
    def verifica_bloco_login(self) -> bool:
        
        """
        Método que verifica se o bloco de 'login' apareceu durante o 'crawling' da página.
        Caso tenha aparecido, faz o tratamento correto do problema e segue com o 'crawling'.
        """

        ### Variáveis ###

        #Variavel que armazena um WebElement
        bloco_login = None

        #Botão fechar
        botao_fechar = None

        ### Código ###

        try:
            bloco_login = self.driver.find_element(By.XPATH, "div//[@data-test-id='login-modal-default' and @class='ADXRXN']")
            if bloco_login:
                botao_fechar = bloco_login.find_element(By.XPATH,"button//[@aria-label='fechar']")
                botao_fechar.click()
                return True
        
        except NoSuchElementException as error:
            return False


#Função Main para DEBUG

def main():

    #Testando instancia do CrawlerImagens e geração de bots com uma Queue
    mock_lista_prompt = ["Lucy Heartfilia", "Nami", "Zelda"] 
    logger = configurando_logger()
    crawler = CrawlerImagens(logger,mock_lista_prompt)
    crawler.driver.quit()



if __name__ == "__main__":
    main()
