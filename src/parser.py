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
    async def bot_requisicao(self):
        pass
    
    @abstractmethod
    async def bot_parser(self):
        pass


#Sub-Classes da Abstrata

class ParserHTMLPinterest(ParserHTML):

    def __init__(self, dict_links_html:dict[str:str], logger:logging.Logger):

        self._dict_links_html = dict_links_html
        self._dict_links_result = {}
        self.logger = logger

        self.logger.debug(f"[INIT - ParserPinterest] Verificando se o dicionário passado para 'dict_links_html' esta vazio.")
        if not self.dict_links_html:
            self.logger.debug(f"[INIT - ParserPinterest] O dicionário fornecido esta vazio! Levantando exceção e encerrando o programa!")
            raise ValueError("O valor do argumento 'dict_links_html' não pode estar vazio!")
        
    @property
    def dict_links_html(self):
        return self._dict_links_html
    
    @dict_links_html.setter
    def dict_links_result(self,valor):
        raise AttributeError(f"O valor do atributo 'dict_links_html' não pode ser modificado diretamente! A unica maneira de modificar o valor é criando uma nova instancia!")
    
    @property
    def dict_links_result(self):
        return self._dict_links_result
    
    @dict_links_result.setter
    def dict_links_result(self,valor):
        raise AttributeError(f"O valor do atributo 'dict_links_result' não pode ser modificado diretamente!")
    
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
        for prompt,lista in self.dict_links_html.items():
            n_req += 1
            lista_task_req.append(asyncio.create_task(self._bot_requisicao(n_req,prompt,lista,fila,evento)))
        
        lista_task_parse = [asyncio.create_task(self._bot_parser(n+1, fila, evento)) for n in range(len(self.dict_links_html))]

        #Iniciando método 'join' da 'Queue' para interromper a execução do método até o fluxo da pipeline terminar
        await fila.join()

        #Método 'asyncio.gather' para esperar todas as tarefas terminarem
        await asyncio.gather(*lista_task_req,*lista_task_parse)

        #TODO #* ------------ Continua.... ------------*#

    async def _bot_requisicao(self,numero:int, prompt:str, lista_links_pin:list[str], fila:asyncio.Queue, evento:asyncio.Event, semaforo:asyncio.Semaphore) -> None:

        ### Variáveis ###


        ### Código ###

        self.logger.debug()

    
    async def _bot_parser(self, numero:int, fila:asyncio.Queue, evento:asyncio.Event) -> None:
        pass


#Função Main

def main():
    pass


if __name__ == "__main__":
    main()


