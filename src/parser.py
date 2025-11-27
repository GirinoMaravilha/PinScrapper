"""
Módulo responsável por disponibilizar parsers de páginas HTML para diferentes sites.

Atualmente, este módulo fornece a classe `ParserImagensPinterest`, que implementa
as funcionalidades necessárias para realizar a requisição da pagina HTML dos links 
que contem as imagens dos pins, e a retirada de todo os links das imagens, que são colocados
em um dicionários, que leva como chave para cada lista de links, o prompt que a gerou. 

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
from abc import ABC,abstractmethod
import logging


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
    async def bot_requisicao(self):
        pass
    
    @abstractmethod
    async def bot_parser(self):
        pass


#Sub-Classes da Abstrata

class ParserHTMLPinterest(ParserHTML):

    def __init__(self, dict_links_html:dict[str:str], logger:logging.Logger):

        self.dict_links_html = dict_links_html
        self.logger = logger

        self.logger.debug(f"[INIT - ParserPinterest] Verificando se o dicionário passado para 'dict_links_html' esta vazio.")
        if not self.dict_links_html:
            self.logger.debug(f"[INIT - ParserPinterest] O dicionário fornecido esta vazio! Levantando exceção e encerrando o programa!")
            raise ValueError("O valor do argumento 'dict_links_html' não pode estar vazio!")

    async def bot_requisicao(self):
        pass

    async def bot_parser(self):
        pass


#Função Main

def main():
    pass


if __name__ == "__main__":
    main()


