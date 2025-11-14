"""
Módulo: utils.py

Módulo que contém todas as funções e classes utilitárias da aplicação.

Dentre elas:

Função: configurando_logger() 

=> Função que retorna uma instancia da classe Logger configurada, do módulo logging.

Essa instancia é utilizada para realizar todos os logs de informação para o usuário, 
logs de depuração e logs em arquivo de possiveis exceções.que possam ocorrer durante 
a utilização do programa.


Classe: MaxFilter(logging.Filter)

=> Classe que é uma sub da metaclasse "logging.Filter".

Essa classe é utilizada para criar um filtro para um dos handlers da instancia do Logger
criada pela função "configurando_logger". No caso, ela faz com que o "StreamHandler" do "Logger"
não retorne mensangens de level "ERROR" para o console, e faça elas apenas aparecerem em um
arquivo ".log".

"""

import logging
import time


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
    debug_handler.addFilter(DebugFIlter())
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


#Classes

class DebugFIlter(logging.Filter):
    
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


if __name__ == "__main__":

    main()