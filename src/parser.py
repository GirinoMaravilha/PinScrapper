from bs4 import BeautifulSoup
import requests
from abc import ABC,abstractmethod


#Classe Abstrata

class ParserImagens(ABC):
    
    @abstractmethod
    async def bot_requisicao(self):
        pass
    
    @abstractmethod
    async def bot_parser(self):
        pass


#Sub-Classes da Abstrata

class ParserImagensPinterest(ParserImagens):

    def __init__(self):
        pass

    def bot_requisicao(self):
        pass

    def bot_parser(self):
        pass


#Função Main

def main():
    pass


if __name__ == "__main__":
    main()


