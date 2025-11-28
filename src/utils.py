"""
Módulo: utils.py

Módulo que contém todas as funções e classes utilitárias da aplicação.

Dentre elas:

Função: configurando_logger() 

=> Função que retorna uma instancia da classe Logger configurada, do módulo logging.

Função: mock_parser()

=> Função 'Mock' que emula um "Parser" para testar o método 'bot_crawler'.

Função: salva_html()

=> Função que recebe um dicionario contendo paginas HTML, e salva elas em um arquivo texto.

Função: salva_links_pin()

=> Função que recebe um dicionario contendo listas com links de 'pin' do Pinterest, e salva eles
   em arquivo texto.

Função: salva_pagina_html()

=> Função que recebe uma página html em formato 'string', e salva ela em um arquivo texto.

Classe: MaxFilter(logging.Filter)

=> Classe que cria um filtro para uma instancia "StreamHandler".

Classe: DebugFilter(logging.Filter)

=> Classe que cria um filtro para uma instancia "StreamHandler".

"""

import logging
import time
import asyncio
from pathlib import Path


def configurando_logger(debug_mode:bool=False) -> logging.Logger:

    ### Variáveis ###

    #Instancia do Logger
    logger = None

    #Tempo atual
    tempo = ""

    #Handler da instancia Logger
    user_handler = None
    file_handler = None
    debug_handler = None

    ### Código ###

    #Capturando o tempo atual
    tempo = time.strftime(fr"%d %m %Y - %H %M %S",time.localtime())

    #Iniciando instancia do Logger
    logger = logging.Logger("PinScrapper.py")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    #Configurando Stream Handler para Usuário
    user_handler = logging.StreamHandler()
    user_handler.setLevel(logging.INFO)
    user_handler.addFilter(UserFilter(logging.ERROR))
    user_handler.setFormatter(logging.Formatter(fr"%(message)s - %(asctime)s",datefmt="%H:%M:%S"))

    #Cofigurando Stream Handler para DEBUG
    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(DebugFilter())
    debug_handler.setFormatter(logging.Formatter(fr"%(message)s - %(asctime)s",datefmt="%H:%M:%S"))


    #Configurando File Handler para Exceções
    file_handler = logging.FileHandler(f"Error {tempo}.log",delay=True)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(fr"%(message)s - %(levelname)s - %(asctime)s",datefmt=fr"%d %m %Y - %H %M %S"))

    #Adiconando handlers a instancia do Logger
    logger.addHandler(user_handler)
    logger.addHandler(file_handler)

    #Adicionando, ou não, o debug_handler a instancia
    if debug_mode:
        logger.addHandler(debug_handler)

    #Retornando instancia configurada
    return logger


#Utilitarios

async def mock_parser(numero:int,logger:logging.Logger,fila:asyncio.Queue,evento:asyncio.Event) -> str:

    """ 

    Função 'Mock' que emula um "Parser" para testar o método 'bot_crawler'.

    Função que recebe valores do método 'bot_crawler' de uma instancia da classe 'CrawlerImagens'.
    A função recebe valores e os retorna em formato de string para o console

    Args:
        numero (int): Número de identificação do 'mock_parser'.

        fila (asyncio.Queue): Uma instancia da classe 'Queue' do módulo 'asyncio'.
                              Usada para retirar valores da pipeline e retornar ao console.

        evento (asyncio.Event): Uma instancia da classe 'Event' do módulo 'asyncio'.
                                Usada para verificar a flag interna da instancia se esta igual
                                a 'True' ou 'False'.
        
        logger (logging.Logger): Uma instancia da classe 'Logger' configurada para gerar logs
                                 durante a execução do código.

    Returns:
        str: Umá pagina HTML com as imagens que queremos coletar reveladas pelo Javascript.

    Raises:
        asyncio.TimeoutError: Exceção levantada pela função 'wait_for' do módulo 'asyncio.
                              Exceção é levantada quando a tarefa demora demais para retirar
                              uma valor da pipeline.
    
    """

    ### Variáveis ###

    # Buffer que recebe páginas HTML da pipeline
    pagina_html = ""

    ### Código ###

    while True:

        logger.debug(f"[Parser - {numero}]Checando se o fluxo da pipeline ja terminou.")
        if fila.empty() and evento.set():
            logger.debug(f"[Parser - {numero}] Pipeline vazia e produção do Crawler finalizada! Encerrando parser.")
            return pagina_html

        try:
            logger.debug(f"[Parser - {numero}]Retirando página HTML da pipeline.")
            pagina_html += "\n\n\n"
            pagina_html += await asyncio.wait_for(fila.get(),4)
            logger.debug(f"[Parser - {numero}]Retirou página HTML da pipeline e adiconou ao buffer.")
            logger.debug(f"[Parser - {numero}]Chamando método 'sleep' para deixar outras tarefas seguirem.")
            await asyncio.sleep(2)
        
        except asyncio.TimeoutError as error:
            logger.debug(f"[Parser - {numero}] Demorou demais. Seguindo em frente com as tarefas.")
            continue
        
        #Chamando método 'task_done' para indicar a Queue que um valor foi processado
        fila.task_done()

def salva_pagina_html(pagina_html:str) -> None:

    """
    Função que recebe uma string, sendo esta uma página HTML, e a salva em um arquivo texto
    dentro de um diretório.

    Args:
        pagina_html(str): Página HTML em formato string.
    """

    ### Variáveis ###

    #Variável que armazena o tempo atual
    tempo_atual = ""

    #Instancia da classe Path
    path = None

    ### Código ####

    #Capturando tempo atual
    tempo_atual = time.strftime(fr"%d %m %Y - %H %M %S", time.localtime())

    #Criando um diretório para salvar as páginas HTML
    path = Path(f"./Páginas HTML")
    path.mkdir(exist_ok=True)

    #Criando o arquivo texto com a págin HTML
    with open(f"{path}/pagina_html - {tempo_atual}.txt","w",encoding="UTF-8") as arq:
        arq.write(pagina_html)


def salva_html(dict_html:dict[str:str]) -> None:

    """
    
    Função que recebe um dicionário de páginas HTML e salva elas em um diretório.

    Args:
        dict_html (dict[str:str]): Dicionario contendo as paginas HTML, tendo como chaves os prompts
                                   que as geraram.
    
    """

    ### Variáveis ###

    #Variavel que recebe uma instancia da Classe 'Path'
    p = None

    #Variável que armazena o tempo atual
    tempo = ""

    ### Código ###

    #Capturando o tempo atual
    tempo = time.strftime(fr"%d %m %Y - %H %M %S", time.localtime())

    #Criando o 'path' e o diretório onde vai ser salvas páginas
    p = Path(".") / f"Paginas_HTML {tempo}"
    p.mkdir(exist_ok=True)

    #Iterando pelas paginas e prompts para criar um arquivo texto com o HTML
    for prompt,pagina in dict_html.items():
        with open(f"{p}/{prompt}.txt", "w", encoding="UTF-8") as arq:
            arq.write(pagina)


def salva_links(dict_links:dict[str,list[str]]) -> None:

    """
    Função que recebe um dicionário contendo um lista com links de 'pins' do Pinterest e salva eles
    em um arquivo texto.

    Args:
        dict_links (dict[str,list[str]]): Dicionário contendo listas com links dos pins do Pinterest, tendo
                                          como chave, os prompts que as geraram.
    """

    ### Variáveis ###

    #Instancia da classe Path
    path = None

    #Tempo atual da execução da função
    tempo = ""

    ### Código ###

    #Capturando o valor do tempo atual
    tempo = time.strftime(fr"%d %m %Y - %H %M %Y",time.localtime())

    #Iniciando a instancia Path e criando o diretório
    path = Path(".") / f"Links Pinterest {tempo}"
    path.mkdir(exist_ok=True)

    #Iterando listas contendo os links e salvando em arquivo '.txt'
    for prompt,lista in dict_links.items():
        with open(f"{path}/{prompt}.txt","w",encoding="UTF-8") as arq:
            for link in lista:
                arq.write(link)
                arq.write("\n")
    

#Classes

class DebugFilter(logging.Filter):
    
    def filter(self, record:logging.LogRecord) -> bool:
        
        return record.levelno == logging.DEBUG


class UserFilter(logging.Filter):

    def __init__(self, level):
        
        self.level = level
    
    def filter(self, record:logging.LogRecord) -> bool:
        
        return record.levelno < self.level
    

#Função Main

def main():
    
    #DEBUG
    #Testando função "configurando_logger"
    logger = configurando_logger()
    logger.info("Testando a função 'configurando_logger()'!")
    logger.debug("Mostrando mensagem DEBUG!")

    logger = configurando_logger(debug_mode=True)
    logger.info("Mostrando mensagem ao usuário!")
    logger.debug("Mostrando mensagem ao desenvolvedor!")


    #Testando a função 'salva_links_pin'
    #dict_links = {"prompt1":["1 Link1","1 Link2","1 Link3"],"prompt2":["2 Link1","2 Link2","2 Link3"],"prompt3":["3 Link1","3 Link2","3 Link3"]}
    #salva_links(dict_links)

    #Testando função 'salva_pagina_html'
    salva_pagina_html("<p> Ola, tudo bem?</p>")


if __name__ == "__main__":

    main()