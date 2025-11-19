from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSelectorException

import logging
from utils import configurando_logger
from utils import salva_html
import time
from traceback import print_exc

#Classes

class CrawlerPinterest:

    def __init__(self,driver:WebDriver,logger:logging.Logger,lista_prompt:list[str]):

        self._driver = driver
        self.lista_prompt = lista_prompt
        self.logger = logger
        
    @property
    def driver(self):
        return self._driver
    
    @driver.setter
    def driver(self, valor):
        raise AttributeError("O atributo self._driver não pode ter seu valor modificado diretamente!")

    def bot_crawler(self,max_img:int=10) -> dict[str:str]:

        #TODO - Ainda não foi tratado o problema de um prompt que não possui imagens nele! - Ok! :D
        #TODO - Ainda não foi tratado o prblema de um prompt que insinua nudez ou sexo! - Ok! :D
        
        #TODO - Lidar com a falha na comexão ao servidor pelo método 'get' do driver!
        #BUG -  Crawler verificando mais elementos que apenas os 'pins' de imagem
        #FIXME - Resolver problema caso o usuário pessa muitas imagens, alem dos que existem no retorno do pinterest.
        #TODO - Temos que testar como o programa lida com bloco de 'login' interrompendo o fluxo.
        #FIXME - O pinterest no 'lazy_loading', quando tem muita imagens na tela, ele vai apagando as
        #       imagens de tras e adiconando mais a frente. A ideia provavelmente é usar o 'extend' do objeto lista para somar uma nova
        #       lista de pins capturados a antiga.
         
        
        ### Variáveis ###

        #Instancia WebDriverWait
        wait = WebDriverWait(self.driver, 10)

        #Lista que armazena os links de pins que vao ser salvos no 'dict_lista_link'
        lista_pin_final= []

        #Lista que armazena os links de pins de cada requisição 'find_elements'
        lista_pin_req = []

        #Dicionario que armazena cada pagina HTML com a chave sendo seu respectivo prompt
        dict_lista_link = {}
        
        ### Código ###

        #Iniciando iteração dos prompts

        self.logger.info("Crawler Iniciado!")
        self.logger.debug("[BOT-CRAWLER] Iniciando método 'bot_crawler' para retornar paginas HTML com links de PIN's disponíveis.")

        self.logger.info("Entrando no site do Pinterest....")
        self.logger.debug("[BOT-CRAWLER] Método 'bot_crawler' iniciado. Iniciando a iteração dos valores da lista" \
        " 'self.lista_prompt'")

        for prompt in self.lista_prompt:
            #Entrando no site e achando o input de pesquisa
            self.logger.info(f"\nComeçando a procurar imagens do prompt => {prompt}")
            self.logger.debug(f"[BOT-CRAWLER] Entrando no link do pinterest => https://br.pinterest.com/search/pins/?q={prompt}&rs=typed'")

            self.driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")

            #DEBUG
            time.sleep(4)

            #Inciando iteração para verificar se a quantidade de imagens no HTML Estático corresponde ao valor de 'max_img'.
            self.logger.debug("[BOT-CRAWLER] Verificando a quantidade de elementos contendo as imagens na página " \
            "e se correspondem com o argumento 'max_img'.")
            while True:
                #Tentando encontrar os elementos contendo as imagens na pagina
                try:
                    
                    #Aqui tentamos pegar todos os links de PIN dos cards da tela
                    lista_div_img = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[@data-test-id='pinWrapper']/a")))

                    #Veririfcando se a quantidade bate com a que foi requisitada
                    if len(lista_div_img) < max_img:
                        self.logger.info(f"\nAchamos apenas {len(lista_div_img)} imagens para o prompt => {prompt}")
                        self.logger.info("Vamos procurar mais....")

                        #DEBUG
                        time.sleep(4)
                        
                        #Vamos "rolar" a tela para baixo e tentar fazer o javascript revelar mais imagens
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    else:
                        #Salvando o HTML estatico no dicionario 'dict_pagina_html' tendo a chave como prompt
                        self.logger.debug(f"\n[BOT-CRAWLER] Achamos {len(lista_div_img)} imagens da requisição de {max_img} imagens.")
                        self.logger.info(f"Achamos todas as imagens! Salvando a pagina do prompt => {prompt}")
                        dict_lista_link[prompt] = self.driver.page_source
                        break
                
                except TimeoutException as error:
                    #TODO Modificar essa parte para tratar os dois bugs de "Não encontrado imagens"
                    #Tratando o problema do bloco de login "congelando" a página
                    self.logger.debug(f"\n[BOT-CRAWLER] Exceção 'TimeoutException' levantada com o prompt => {prompt}")
                    self.logger.info(f"Alguma interrupção aconteceu no prompt => {prompt}")
                    self.logger.info(f"Lidando com ela para continuar com o fluxo...")

                    time.sleep(4)
                    self.logger.debug(f"\n[BOT-CRAWLER] Chamando o método 'self.verifica_interrupcao' para lidar com a interrupção no 'crawling' do site.")
                    
                    #Caso a interrupção for por falta de imagens seja "NSFW" ou "prompt sem imagens" não tem porque continuar a iteração. 
                    #Quebramos o ciclo 'while' e seguimos para o próximo prompt.
                    if not self.verifica_interrupcao(prompt):
                        break
        
        #Retornando dicionario com as paginas HTML
        self.logger.debug("\n[BOT-CRAWLER] Iteração de todos os prompts terminada, retornando o dicionario 'dict_pagina_html'.")
        self.logger.info("Captura das páginas terminada!")
        return dict_lista_link
    
    def verifica_pin(self, lista_pin_final:list[str], lista_pin_req:list[str]) -> None:

        """
        Método utilizado para verificar quais os links de 'pins' da listad de requisição 'lista_pins_req'
        existem dentro da lista de links de 'pins' final que é a que vai ficar atribuida ao prompt no dicionario
        devolvido pelo método 'bot_crawler'

        Esse método foi criado pois o Pinterest tem uma abordagem de, com o javascript, ir 'desativando' os cards de pin que esta fora da
        tela e 'ativando' os cards novos a cada rolamento da tela. Ele faz isso provavelmente para nao deixar todos os cards
        revelados, o que faria o navegador ficar muito lento.

        Portanto a cada rolamento do "execute_script" os cards antigos "somem" e os cards posteriores que estavam escondidos pelo javascript
        "aparecem". Dessa forma não tem como, por exemplo, revelar todos os cards com o "rolamento" e capturar a pagina inteira. O crawling
        tem que acontecer de maneira "segmentada", capturando links dos pins que esta na tela, rolando a tela para baixo, e realizando a captura
        de novo. 
        
        O problema é que muitas vezes o rolamento não é o suficiente para capturar apenas links de pins novos, ou seja, que ja não foram capturados.
        Muitas vezes alem de links novos, links antigos tambem são capturados.
        
        Dessa forma esse método foi criado para resolver isso. A cada requisição, cada link da lista de links capturados dos pins é utilizado em uma
        verificação onde é checado se ele ja existe na lista de links final 'lista_pin_final', se ja existir nada acontece, agora se não existir
        ele é adicionado a ela.

        Args:
            lista_pin_final (list[str]): Lista contendo todos os links ja salvos e filtrados.

            lista_pin_req(list[str]): Lista contendo os links da ultima requisição que precisam ser filtrados.
        
        """
        
        #Vamor iterar cada item da lista final para comparar com a nova requisição
        for link_r in lista_pin_req:
            if not link_r in lista_pin_final:
                lista_pin_final.append(link_r)
          

                        
    def verifica_interrupcao(self, prompt:str) -> bool:
        
        """
        Método que verifica qual tipo de interrupção que ocorreu no fluxo do crawling dentro do 
        'Pinterest'.

        3 casos especificos são checados:

        1º - Se o prompt não devolveu nenhuma 'pin' de imagem.

        2º - Se o prompt contém alguma palavra 'NSFW'

        3º - Se o bloco de 'login' apareceu, bloqueando o SELENIUM de verificar os 'pins' das imagens.

        Caso nenhum dos 3 casos for averiguado, algo que o PinScrapper.py não consegue lidar esta
        bloqueando a ação do 'crawler'. Nesse caso o problema é "grave", e precisa da averiguação do
        desenvolvedor. Nessa situação a exceção 'InvalidSelectorException' é levantada, e um relatório
        sobre o erro é gerado.

        PS: A lista é escolhida propositalmente como objeto para armazenar o WebElement representante das 
            interrupções de falta de imagem e NSFW justamente porque, caso nenhum elemento for encontrado,
            o "find_elements" devolve uma lista vazia, e não levanta uma Exceção como o caso do "find_element".

        Args:
            prompt (str): A string do prompt que esta sendo usado no momento para o 'crawling' de 'pins'.
        
        Raises:
            InvalidSelectorException: Exceção 'levantada' quando nenhum dos 3 casos de interrupção é encontrado.

        """

        ### Variáveis ###

        #Variavel que armazena um WebElement
        bloco_login = None

        #Botão fechar
        botao_fechar = None

        #Lista que vai verificar elemento de bloqueio relacionado a "nudez" no prompt
        nsfw = []

        #Lista que vai verificar elemnto de bloqueio a "nenhuma imagem encontrada"
        no_img = []

        ### Código ###

        self.logger.debug("\nIniciando método 'verifica_interrupção'")
        
        #Verificando se a interrupção é causada pelo prompt não retornar nenhuma imagem.
        self.logger.debug(f"\n[BOT-CRAWLER] Verificando se o problema é não ter retornado nenhum pin do prompt => {prompt}")
        no_img = self.driver.find_elements(By.XPATH,"//div[text()='Não foi possível encontrar Pins para esta pesquisa.']")
        
        #Ação caso for encontrado o texto para o problema de nenhum pin retornado pelo prompt
        if no_img:
            self.logger.debug(f"\n[BOT-CRAWLER] O problema da interrupção foi que nenhum pin retornou pelo prompt => {prompt}")
            self.logger.info(f"Achamos o problema! Nenhuma imagem foi retornada para o prompt => {prompt}")
            self.logger.info("Seguindo com o a pesquisa de 'pins' para próximo prompt....")
            return False
        
        #Verificando se a interrupção é causada pelo prompt insinuar conteúdo NSFW
        self.logger.debug(f"\n[BOT-CRAWLER] Verificando se o problema é possivel conteudo NSFW retornado pelo prompt => {prompt}")
        nsfw = self.driver.find_elements(By.XPATH,"//span[text()='Pins sobre esse interesse costumam violar as ' or text()='Nudez é permitida no Pinterest, mas com ressalvas. Certifique-se de que entendeu ']")

        #Ação caso encontrado mensagem sobre bloqueio da requisição por conteudo NSFW
        if nsfw:
            self.logger.debug(f"\n[BOT-CRAWLER] O problema da interrupção foi o prompt insinuar conteúdo NSFW => {prompt}")
            self.logger.info(f"Achamos o problema! Nenhuma imagem foi retornada para o prompt por ele insinuar NSFW => {prompt}")
            self.logger.info("Seguindo com o a pesquisa de 'pins' para próximo prompt....")
            return False
        
        #Caso não for problemas com o prompt fornecido, verificamos se o bloco de 'login' de bloqueando o acesso do crawler ao site
        try:
            bloco_login = self.driver.find_element(By.XPATH, "div//[@data-test-id='login-modal-default' and @class='ADXRXN']")
            if bloco_login:
                botao_fechar = bloco_login.find_element(By.XPATH,"button//[@aria-label='fechar']")
                botao_fechar.click()
                return True
        
        except InvalidSelectorException as error:

            #Problema grave. Algo esta interrompendo o fluxo e que o PinScrapper não consegue lidar
            #Fazendo limpeza e encerrando programa
            self.driver.quit()

            self.logger.info("Bloco Login e textos não encontrados! Erro grave no programa! De uma olhada no log de erro 'Error.log'!")
            self.logger.error(f"[BOT-CRAWLER] Bloco login e textos não encontrados. Outra coisa não esta deixando o CrawlerPinterest encontrar as imagens. => {error}\n{print_exc()}")
            
            raise InvalidSelectorException
        

#Função Main para DEBUG

def main():

    #Testando instancia do CrawlerImagens na captura de páginas HTML
    mock_lista_prompt = ["Lucy Heartfilia","Android 18", "Nami","Digimon 1 Mimi adult","Princess Zelda"] 
    logger = configurando_logger(debug_mode=True)
    driver = webdriver.Chrome()
    dict_html = {}

    crawler = CrawlerPinterest(driver,logger,mock_lista_prompt)
    dict_html = crawler.bot_crawler()
    crawler.driver.quit()

    #Verificando páginas capturadas em arquivo
    salva_html(dict_html)


if __name__ == "__main__":
    main()
