"""
Módulo: utils.py

Módulo que contém todas as funções e classes utilitárias da aplicação.

Dentre elas:

Função: configurando_logger() 

=> Função que retorna uma instancia da classe Logger configurada, do módulo logging.

Essa instancia é utilizada para realizar todos os logs de informação para o usuário, 
logs de depuração e logs em arquivo de possiveis exceções.que possam ocorrer durante 
a utilização do programa.

"""

import logging
import time


def configurando_logger() -> logging.Logger:

    ### Variáveis ###

    #Instancia do Logger
    logger = None

    #Tempo atual
    tempo = ""

    #Handler da instancia Logger
    stream_handler = None
    file_handler = None

    ### Código ###

    #Capturando o tempo atual
    tempo = time.strftime(fr"%d %m %Y - %H %M %S",time.localtime())

    #Iniciando instancia do Logger
    logger = logging.Logger("PinScrapper.py")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    #Configurando Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.addFilter(MaxFilter(logging.ERROR))
    stream_handler.setFormatter(logging.Formatter(fr"%(message)s - %(asctime)s",datefmt="%H:%M:S"))

    #Configurando File Handler
    file_handler = logging.FileHandler(f"Error {tempo}.log",delay=True)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(fr"%(message)s - %(levelname)s - %(asctime)s",datefmt=fr"%d %m %Y - %H %M %S"))

    #Adiconando handlers a instancia do Logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    #Retornando instancia configurada
    return logger


#Classes

class MaxFilter(logging.Filter):

    def __init__(self, level):
        
        self.level = level
    
    def filter(self, record):
        
        return record.levelno < self.level
    

#Função Main

def main():
    
    #DEBUG
    #Testando função "configurando_logger"
    logger = configurando_logger()
    logger.info("Testando a função 'configurando_logger()'!")


if __name__ == "__main__":

    main()