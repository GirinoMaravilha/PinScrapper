"""
Módulo responsável por disponibilizar parsers de páginas HTML para diferentes sites.

Atualmente, este módulo fornece a classe `ParserImagensPinterest`, que implementa
as funcionalidades necessárias para realizar a requisição da pagina HTML dos links 
que contem as imagens dos pins, e a retirada de todo os links das imagens, que são colocados
em um dicionário, que leva como chave para cada lista de links, o prompt que a gerou. 

Dependências:
    - bs4
    - aiohttp
    - utils.py (módulo interno desta aplicação)

Exemplo:
    

Notas:
    Este módulo não deve ser executado diretamente, utilize ele apenas via 'import'.

"""


from bs4 import BeautifulSoup
import aiohttp
import asyncio
from abc import ABC,abstractmethod
import logging
from utils import configurando_logger, salva_pagina_html
from crawler import CrawlerPinterest
from selenium import webdriver
from traceback import format_exc


#Classe Abstrata

class ParserHTML(ABC):

    """
    Classe base abstrata para parsers de diferentes sites.

    Esta classe define a interface mínima que todo parser deve implementar,
    garantindo um comportamento consistente entre diversas plataformas.
    Subclasses devem sobrescrever os métodos abstratos para fornecer a
    lógica específica de cada site.
    """

    @abstractmethod
    async def parsing(self):
        pass
    
    @abstractmethod
    async def _bot_requisicao(self):
        pass
    
    @abstractmethod
    async def _bot_parser(self):
        pass


#Sub-Classes da Abstrata

class ParserHTMLPinterest(ParserHTML):

    def __init__(self, dict_links_html:dict[str:str], logger:logging.Logger):

        self._dict_links_html = dict_links_html
        self._dict_links_result = []
        self.logger = logger
        self.contador_de_acoes = 0

        #A quantidade de produtores que tera que ser criada para lidar com a requisição
        self._numero_produtores = len(dict_links_html)

        #Verificando ser o argumento 'dict_links_html' esta vazio
        self.logger.debug(f"[INIT - ParserPinterest] Verificando se o dicionário passado para 'dict_links_html' esta vazio.")
        if not self._dict_links_html:
            self.logger.debug(f"[INIT - ParserPinterest] O dicionário fornecido esta vazio! Levantando exceção e encerrando o programa!")
            raise ValueError("O valor do argumento 'dict_links_html' não pode estar vazio!")
    
    async def parsing(self):

        ### Variáveis ###

        #Instancia assincrona Queue
        fila = None

        #Instancia assincrona Event
        evento = None

        #Lista de tasks para bots de requisição
        lista_task_req = []

        #Lista de tasks para bots de parsing
        lista_task_parse = []

        #Numero de cada bot req criado
        n_req = 0

        #Instancia 'Semaphore' para limitar o numero de conexões
        semaforo = None

        ### Código ###

        self.logger.debug(f"\n[PARSING] Método 'parsing' da classe 'ParserHTMLPinterest' iniciado!")
        self.logger.info(f"Iniciando a coleta dos links das imagens!")

        #Iniciando instancias que seram utilizadas
        fila = asyncio.Queue()
        evento = asyncio.Event()
        semaforo = asyncio.Semaphore(3)

        #Iniciando tarefas de requisição e parsing
        self.logger.debug("\n[PARSING] Iniciando tarefas de requisição e parsing das paginas html coletadas!")
        self.logger.debug(f"\n[PARSING] Valor da quantidade de produtores no atributo 'self._numero_produtores' => {self._numero_produtores}")
        for prompt,lista in self._dict_links_html.items():
            n_req += 1
            lista_task_req.append(asyncio.create_task(self._bot_requisicao(n_req,prompt,lista,fila,evento,semaforo)))
        
        lista_task_parse = [asyncio.create_task(self._bot_parser(n+1, fila, evento)) for n in range(len(self._dict_links_html))]

        #Iniciando método 'join' da 'Queue' para interromper a execução do método até o fluxo da pipeline terminar
        await fila.join()

        #Método 'asyncio.gather' para esperar todas as tarefas terminarem
        await asyncio.gather(*lista_task_req,*lista_task_parse)

        self.logger.debug("[PARSING] Bots de requisição e parsing finalizados! Encerrando o programa e retornando dicionario contendo as listas com todos os links de imagens")
        return dict(self._dict_links_result)
        
        #DEBUG
        #print(f"Quantidade de ações realizadas pelo bots => {self.contador_de_acoes}")

    async def _bot_requisicao(self,numero:int, prompt:str, lista_links_pin:list[str], fila:asyncio.Queue, evento:asyncio.Event, semaforo:asyncio.Semaphore) -> None:

        ### Variáveis ###

        #Numero de tentativas de requisição
        n_req = 0

        #Instancia 'Lock' para verificaçao filtrada do valor de 'self.numero_produtores'
        lock = asyncio.Lock()

        #Lista de páginas html contendo o link de cada imagem
        lista_html_img = []

        #Variável que armazena Página html capturada em formato de string
        html = ""

        ### Código ###

        self.logger.debug(f"[BOT_REQ - {numero}] Bot iniciado com o prompt => {prompt}")
        self.logger.info(f"Prompt => {prompt} - Começando a coleta dos links de imagem...")

        #Iniciando a iteração dos links de cada pin para realizar a requisição da pagina HTML
        for link in lista_links_pin:
            
            #Reiniciando contador 'r_req' para uma nova tentativa de requisição
            n_req = 0

            #Iniciando bloco de requisição com limite de 3 'tasks' por vez
            self.logger.debug(f"[BOT_REQ - {numero}] Iniciando requisição do link => {link}")
            async with semaforo:
                async with aiohttp.ClientSession() as session:
                    #Iniciando as tentativas de requisição
                    while True:

                        #Incrementando valor do contador, indicando mais uma tentativa de requisição
                        n_req +=1 

                        #Começando requisição
                        self.logger.debug(f"[BOT_REQ - {numero}] {n_req}ª tentativa de requisição...")
                        async with session.get(link, max_field_size=16384) as resp:
                            if resp.status == 200:
                                self.logger.debug(f"[BOT_REQ - {numero}] Requisição do link => {link} - bem sucedida! Capturando página HTML do link => {link}")
                                html = await resp.text()

                                
                                #DEBUG
                                #Salvando pagina requisitada para verificar se existe o link nela
                                #async with lock:
                                #    salva_pagina_html(html)
                                #    self.contador_de_acoes += 1
                                

                                lista_html_img.append(html)
                                self.logger.debug(f"[BOT_REQ - {numero}] - Página HTML do link => {link} capturada! encerrando loop de requisição.")
                                break
                        
                            else:
                                if n_req == 3:
                                    self.logger.debug(f"[BOT_REQ - {numero}] {n_req}ª tentativa de requisição!")
                                    self.logger.debug(f"[BOT_REQ - {numero}] Limite excedido! Ignorando link => {link} e seguindo o fluxo...")
                                    break

        #Depois de capturar todas as paginas HTML de cada link dos pins colocamos a tupla dentro da Queue
        self.logger.debug(f"[BOT_REQ - {numero}] Captura de páginas HTML para o prompt {prompt} terminada!")
        self.logger.debug(f"[BOT_REQ - {numero}] Colocando tupla com valores do prompt e sua lista de paginas HTML de cada link dos pins na pipeline...")
        await fila.put((prompt,lista_html_img))

        #Sinalizando o fim da produção e verificando o numero de produtores ativos para a ativação da flag no 'Event', sinalizando o fim da pipeline
        self.logger.debug(f"[BOT_REQ - {numero}] Sinalizando o fim da produção e verificando a quantidade de produtores ativos....")
        async with lock:
            self._numero_produtores -= 1
            if not self._numero_produtores:
                self.logger.debug(f"[BOT_REQ - {numero}] Todos os produtores terminaram! Ativando a flag 'set' da instância 'Event'! Fim de produção na pipeline!")
                evento.set()
    
    async def _bot_parser(self, numero:int, fila:asyncio.Queue, evento:asyncio.Event) -> None:
        
        ### Variáveis ###

        #Lista de links de imagem coletados das paginas HTML fornecidas na PIPELINE pelos tasks '_bot_requisicao'
        lista_links_img = []

        #Variável que armazena valores retirados da Queue, contendo o prompt e uma lista de páginas HTML
        prompt = ""
        lista_paginas_html = []

        #Numero de paginas onde foi realizado o 'Parsing'
        n_parser = 0

        #Link retirado da pagina HTML
        link = ""

        ### Código ###

        self.logger.debug(f"[BOT_PARSER - {numero}] Bot de Parsing Iniciado!")
        
        #Iniciando fluxo de coleta de valores da pipeline
        while True:
            
            #Reiniciando variáveis para uma nova execução
            n_parser = 0
            lista_links_img = []

            #Verificando se a produção terminou para o encerramento do bot
            if fila.empty() and evento.is_set():
                self.logger.debug(f"[BOT_PARSER - {numero}] A pipeline esta vazia! Flag da instancia 'Event' ativada! Produção terminou, encerrando o bot...")
                break
            
            #Tentando retirar valor da pipeline
            self.logger.debug(f"[BOT_PARSER - {numero}] Retirando valor da pipeline...")
            try:
                prompt,lista_paginas_html = await asyncio.wait_for(fila.get(),5)
                
                #Iniciando a iteração para a retirada do link de cada página HTML
                self.logger.debug(f"[BOT_PARSER - {numero}] Iniciando Parsing das paginas do prompt => {prompt}")
                for pagina_html in lista_paginas_html:
                    n_parser += 1
                    self.logger.debug(f"[BOT_PARSER - {numero}] Realizando o parsing da {n_parser}ª pagina....")
                    link = self._parsing_link(pagina_html)
                    lista_links_img.append(link)
            
            except asyncio.TimeoutError as error:
                self.logger.debug(f"\n[BOT_PARSER - {numero}] Bot demorou demais para retirar valor da pipeline! Seguindo o fluxo...")
                continue
            
            #Sinalizando que um item da pipeline foi processado e armazenando resultados
            self.logger.debug(f"\n[BOT_PARSER - {numero}] Parsing de todas as páginas do prompt => {prompt} realizado! Atribuindo tupla com o prompt e lista de links ao atributo 'self._dict_links_result'")
            self._dict_links_result.append((prompt,lista_links_img))
            fila.task_done()
    
    def _parsing_link(self,pagina_html:str) -> str:

        ### Variáveis ###

        #Instancia do BeautifulSoup
        soup = None

        #Tag <div> que contem a tag <img>
        div = None

        #Tag <img> que contem o link da imagem
        img = None

        ### Código ###

        #Iniciando instancia do BeautifulSoup com a página HTML
        soup = BeautifulSoup(pagina_html,"html.parser")

        #Retirando o div que contem a tag '<img>' com o link da imagem
        div = soup.find("div",attrs={"data-test-id":"pin-closeup-image"})

        #Retirando a tag <img>
        img = div.find("img")

        #Retornando link
        return img['src']
                

#Função Main para depuração

def main():

    logger = configurando_logger(debug_mode=True)
    dict_links = {
        'Nami One Piece': ['https://br.pinterest.com/pin/41799102786179161/', 'https://br.pinterest.com/pin/2040762327287919/', 'https://br.pinterest.com/pin/32580797302853515/', 'https://br.pinterest.com/pin/1125968650715952/', 'https://br.pinterest.com/pin/14355292555640003/', 'https://br.pinterest.com/pin/2040762327232209/', 'https://br.pinterest.com/pin/7881368093174342/', 'https://br.pinterest.com/pin/4292562138627762/', 'https://br.pinterest.com/pin/19351473394862096/', 'https://br.pinterest.com/pin/152066924913960274/'], 
        'Lucy Heatfilia': ['https://br.pinterest.com/pin/283586107781129519/', 'https://br.pinterest.com/pin/128774870592476656/', 'https://br.pinterest.com/pin/7529524372889663/', 'https://br.pinterest.com/pin/45387908740319673/', 'https://br.pinterest.com/pin/62557882318282315/', 'https://br.pinterest.com/pin/20407004557347201/', 'https://br.pinterest.com/pin/42854633949068353/', 'https://br.pinterest.com/pin/45387908740319667/', 'https://br.pinterest.com/pin/313070611616883732/', 'https://br.pinterest.com/pin/113153009394037713/'], 
        'Mimi Digimon Adult': ['https://br.pinterest.com/pin/59391288832866781/', 'https://br.pinterest.com/pin/209839663883493938/', 'https://br.pinterest.com/pin/415738609349071096/', 'https://br.pinterest.com/pin/48343395986948828/', 'https://br.pinterest.com/pin/145381894219596196/', 'https://br.pinterest.com/pin/109071622221470085/', 'https://br.pinterest.com/pin/408490628716239437/', 'https://br.pinterest.com/pin/176484879144154072/', 'https://br.pinterest.com/pin/426997608397750499/', 'https://br.pinterest.com/pin/15973773657761385/']}

    try:
        parser = ParserHTMLPinterest(dict_links,logger)
        asyncio.run(parser.parsing())
    
    except KeyboardInterrupt as error:
        logger.debug(f"[MAIN] Interrupção do teclado detectada! Interrompendo programa....")
    
    except Exception as error:
        logger.debug("[MAIN] Uma exceçao ocorreu! Verifique o relatório de erro 'Error.log'!")
        logger.error(f"[MAIN] Exceção => {error}\n\nTraceback =>{format_exc()}")


if __name__ == "__main__":
    main()


