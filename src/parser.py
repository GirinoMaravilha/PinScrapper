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

        #A quantidade de produtores que tera que ser criada para lidar com a requisição
        self.numero_produtores = len(dict_links_html)

        #Verificando ser o argumento 'dict_links_html' esta vazio
        self.logger.debug(f"[INIT - ParserPinterest] Verificando se o dicionário passado para 'dict_links_html' esta vazio.")
        if not self.dict_links_html:
            self.logger.debug(f"[INIT - ParserPinterest] O dicionário fornecido esta vazio! Levantando exceção e encerrando o programa!")
            raise ValueError("O valor do argumento 'dict_links_html' não pode estar vazio!")
    
    @property
    def dict_links_html(self):
        return self._dict_links_html
    
    @property
    def dict_links_result(self):
        return self._dict_links_result

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

        #Numero de tentativas de requisição
        n_req = 0

        #Instancia 'Lock' para verificaçao filtrada do valor de 'self.numero_produtores'
        lock = asyncio.Lock()

        #Lista de páginas html contendo os links de cada imagem dos pins.
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
                        self.logger.debug(f"[BOT_REQ - {numero}] {n_req}ª tentativa de requisição...")
                        async with session.get(link) as resp:
                            if resp.status == 200:
                                self.logger.debug(f"[BOT_REQ - {numero}] Requisição do link => {link} - bem sucedida! Capturando página HTML do link => {link}")
                                html = await resp.text()
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
        fila.task_done()

        #Sinalizando o fim da produção e verificando o numero de produtores ativos para a ativação da flag no 'Event', sinalizando o fim da pipeline
        self.logger.debug(f"[BOT_REQ - {numero}] Sinalizando o fim da produção e verificando a quantidade de produtores ativos....")
        async with lock:
            self.numero_produtores -= 1
            if not self.numero_produtores:
                self.logger.debug(f"[BOT_REQ - {numero}] Todos os produtores terminaram! Ativando a flag 'set' da instância 'Event'! Fim de produção na pipeline!")
                evento.set()
    
    async def _bot_parser(self, numero:int, fila:asyncio.Queue, evento:asyncio.Event) -> None:
        pass


#Função Main

def main():
    pass


if __name__ == "__main__":
    main()


