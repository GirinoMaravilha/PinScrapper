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

#TODO O que falta para finalizar esta etapa do projeto?
# - Tratamento de exceções e encapsulamento correto de atributos. - Ok! :D
# - Criação do módulo 'test_parser.py' para a criação de funções/métodos teste de todas as funcionalidades
#   mais importantes do módulo 'parser.py.
# - Documentar todos o métodos e classes. - Ok! :D
# - Output para o usuário como 'logger.info' - Ok! :D
# - Fazer o cacheamento dos valores de resultado - Ok! :D

from bs4 import BeautifulSoup
import aiohttp
import asyncio
from abc import ABC,abstractmethod
import logging
from utils import configurando_logger, salva_pagina_html
from traceback import format_exc
from types import MappingProxyType


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

    """
    Classe que implementa um 'Parser' para requisição e coleta de dados de páginas HTML do Pinterest.

    Esta classe realiza a requisição de páginas HTML do 'pins' do site do Pinterest. Depois de realizada
    a requisição, a classe retira de cada página o link da imagem do 'pin', e o armazena em uma lista
    que ira ser atribuida a um dicionario, tendo como chave da mesma, o prompt que gerou os pins.

    Attributes:
        _dict_links_html (dict[str,list[str]]): Dicionário, que tem como seu valor, listas de links de páginas HTML, e o  prompt que as geraram como chave. 
                                          O atributo é encapsulado e não deve ser modificado diretamente.

        _dict_links_result (list[str]): Lista de tuplas usada para armazenar os resultados do 'parsing' feito pelo método '_bot_parser',
                                        que adiciona ao valor da lista, uma tupla contendo o prompt e a lista de links retirados de todas
                                        as páginas HTML do atributo '_dict_links_html'. O atributo é encapsulado e não deve ser modificado 
                                        diretamente.

        logger (Logger): Logger usado para registrar mensagens e exceções.

        _numero_de_produtores (int): A quantidade de 'tasks' ou 'corroutines' que teram que ser criados para lidar como o numero de requisições.
                                    leva o mesmo valor da quantidade de valores do atributo '_dict_links_html'. O atributo é encapsulado e não deve ser modificado 
                                    diretamente.
        
    """

    def __init__(self, dict_links_html:dict[str,str], logger:logging.Logger):

        self._dict_links_html = dict_links_html
        self._dict_links_result = []
        self.logger = logger

        #A quantidade de produtores que tera que ser criada para lidar com a requisição
        self._numero_produtores = len(dict_links_html)

        #Verificando ser o argumento 'dict_links_html' esta vazio
        self.logger.debug(f"[INIT - ParserPinterest] Verificando se o dicionário passado para 'dict_links_html' esta vazio.")
        if not self._dict_links_html:
            self.logger.debug(f"[INIT - ParserPinterest] O dicionário fornecido esta vazio! Levantando exceção e encerrando o programa!")
            raise ValueError("O valor do argumento 'dict_links_html' não pode estar vazio!")
    
    #Encapsulamento do atributo '_dict_links_html'
    @property
    def dict_links_html(self):
        return MappingProxyType(self._dict_links_html)
    
    @dict_links_html.setter
    def dict_links_html(self,valor):
        raise AttributeError("Acesso Negado! O atributo '_dict_links_html' não pode ser modificado diretamente! Crie uma nova instância de 'ParserHTMLPinterest' para realizar uma nova atribuição!")

    #Encapsulamento do atributo '_dict_links_result'
    @property
    def dict_links_result(self):
        return tuple(self._dict_links_result)
    
    @dict_links_result.setter
    def dict_links_result(self,valor):
        raise AttributeError("Acesso Negado! O atributo '_dict_links_result' não pode ser modificado diretamente!")

    #Encapsulamento do atributo '_numero_produtores'
    @property
    def numero_produtores(self):
        return tuple(self._numero_produtores)
    
    @numero_produtores.setter
    def numero_produtores(self,valor):
        raise AttributeError("Acesso Negado! O atributo '_numero_produtores' não pode ser modificado diretamente!")
    
    async def parsing(self) -> dict[str,list[str]]:

        """
        Método que controla todo o fluxo de requisição/parsing dos links de 'pin' fornecidos pelo atributo 'self._dict_links_html'.

        O método 'parsing' cria 'tasks' assincronas relacionadas a quantidade de valores armazenados no dicionario
        que esta como valor do atributo 'self._dict_links_html'.

        Isso é realizado pois cada chave do dicionário é um "prompt", que leva como seu valor, uma lista de links de pins 
        que contem páginas HTML de cada pin que apareceu durante a pesquisa de imagens no Pinterest usando esse mesmo 'prompt'.

        Assim, cada 'task' tem como responsabilidade individual um "prompt" especifico e sua lista de páginas HTML. Isso
        deixa todo o processo mais organizado e limpo, e faz com que retornar os valores de resultado fique muito mais fácil.

        Essa regra de cada 'task' cuidar de um prompt especifico, junto com sua lista de links de 'pins', funciona para ambos métodos
        assincronos '_bot_requisicao' e _bot_parser' que são utilizados para criar 'tasks' pelo método 'parsing'.

        Returns:
            dict[str,list[str]]: Dicionário onde cada chave é um prompt e o valor é uma lista de links de imagens coletados.
        """

        #Verificando cacheamento antes da execução da lógica interna de 'parsing'
        if self._dict_links_result:
            return dict(self._dict_links_result)

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

    async def _bot_requisicao(self,numero:int, prompt:str, lista_links_pin:list[str], fila:asyncio.Queue, evento:asyncio.Event, semaforo:asyncio.Semaphore) -> None:

        """
        Método assíncrono que executa a requisição de paǵinas HTML.

        O método realiza a requisição das paginas HTML dos links da lista que esta atribuida ao argumento 'lista_links_pin'.
        Esssas paginas sera colocadas novamente em uma lista, e esta lista ira ser inserida em uma tupla, junto ao valor do argumento
        prompt. Essa tupla entao é inserida na pipeline do argumento 'fila'.

        O processo descrito acima é todo o fluxo de trabalho desse método assíncrono. 
        
        AVISO: O método é encapsulado, ou seja, faz parte da lógica interna da classe portanto não deve ser chamado diretamente.

        Args:
            numero (int): Número de identificação usado para referenciar cada instância 'task' do método '_bot_requsicao'.
            
            prompt (str): String que foi usada na pesquisa do Pinterest, e que gerou a lista de links de 'pins' atribuidas a ele
                          e localizadas no argumento 'lista_links_pin'.
            
            lista_links_pin (list[str]): Lista que contem todos os links de 'pins' que serão utilizados para realizar a requisição da
                                         página HTML de cada um. Esses links são dos 'pins' resultados da pesquisa no Pinterest, usando
                                         o valor do argumento 'prompt'.
            
            fila (asyncio.Queue): Instancia da classe 'Queue' do módulo 'asyncio'. Utilizada para o método interagir com a pipeline. Inserindo
                                  valores dentro dela que serão utilizados por 'tasks' do método assíncrono '_bot_parser'.
            
            evento (asyncio.Event): Instancia da classe 'Event' do módulo 'asyncio'. Utilizada para sinalizar o fim da produção, chamando o método
                                    'set' da instancia para ativar uma flag interna da mesma.
            
            semaforo (asyncio.Semaphore): Instancia da classe 'Semaphore' do módulo 'asyncio'. Utilizada para limitar a interação com um bloco de código
                                          dentro da lógica interna do método por diferentes 'tasks'. No caso o bloco limitado é o de requisição da página HTML
                                          ao servidor do Pinterest.

        """

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
                                lista_html_img.append(html)
                                self.logger.debug(f"[BOT_REQ - {numero}] - Página HTML do link => {link} capturada! encerrando loop de requisição.")
                                break
                        
                            else:
                                if n_req == 3:
                                    self.logger.debug(f"[BOT_REQ - {numero}] {n_req}ª tentativa de requisição!")
                                    self.logger.debug(f"[BOT_REQ - {numero}] Limite excedido! Ignorando link => {link} e seguindo o fluxo...")
                                    self.logger.info(f"Problema ao fazer a requisição do link => {link} - do prompt => {prompt}")
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

        """
        Método assíncrono que executa o 'parsing' de páginas HTML da tupla retirada da pipeline.

        O método executa o parsing das páginas HTML encontradas na lista da tupla que é retirada por ele da pipeline de 'fila'.
        O 'parsing' da página retira o link de imagem da página do 'pin', e insere ele em uma lista, que depois de completa, é
        colocada em uma tupla junto ao 'prompt' (Que é o primeiro valor da tupla retirada da pipeline).

        A tupla por sua vez é armazenada na lista 'dict_links_result' que é uma atributo da classe.

        AVISO: O método é encapsulado, ou seja, faz parte da lógica interna da classe portanto não deve ser chamado diretamente.

        Args:
            numero (int): Número de identificação usado para referenciar cada instância 'task' do método '_bot_parser'.

            fila (asyncio.Queue): Instancia da classe 'Queue' do módulo 'asyncio'. Utilizada para o método interagir com a pipeline, retirando
                                  valores dentro dela que serão utilizados por sua lógica interna.
            
            evento (asyncio.Event): Instancia da classe 'Event' do módulo 'asyncio'. Utilizada para verificar o fim da produção, chamando o método
                                    'is_set'.

        Raises:
            asyncio.TimeoutError: Exceção levantada quando o método, sendo uma 'task', demora demais para retirar uma valor da pipeline.
        """
        
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
            self.logger.info(f"Coleta de todos os links das imagens do prompt => {prompt} - realizada!")
            self._dict_links_result.append((prompt,lista_links_img))
            fila.task_done()
    
    def _parsing_link(self,pagina_html:str) -> str:

        """
        Método auxiliar que retira links de imagem de uma página HTML.

        Args:
            pagina_html(str): Página HTML de onde sera retirado o link.

        Returns:
            str: Link da imagem de uma página de 'pin' do 'Pinterest'.
        """

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

    logger = configurando_logger(debug_mode=False)
    dict_links = {
        'Nami One Piece': ['https://br.pinterest.com/pin/41799102786179161/', 'https://br.pinterest.com/pin/2040762327287919/', 'https://br.pinterest.com/pin/32580797302853515/', 'https://br.pinterest.com/pin/1125968650715952/', 'https://br.pinterest.com/pin/14355292555640003/', 'https://br.pinterest.com/pin/2040762327232209/', 'https://br.pinterest.com/pin/7881368093174342/', 'https://br.pinterest.com/pin/4292562138627762/', 'https://br.pinterest.com/pin/19351473394862096/', 'https://br.pinterest.com/pin/152066924913960274/'], 
        'Lucy Heatfilia': ['https://br.pinterest.com/pin/283586107781129519/', 'https://br.pinterest.com/pin/128774870592476656/', 'https://br.pinterest.com/pin/7529524372889663/', 'https://br.pinterest.com/pin/45387908740319673/', 'https://br.pinterest.com/pin/62557882318282315/', 'https://br.pinterest.com/pin/20407004557347201/', 'https://br.pinterest.com/pin/42854633949068353/', 'https://br.pinterest.com/pin/45387908740319667/', 'https://br.pinterest.com/pin/313070611616883732/', 'https://br.pinterest.com/pin/113153009394037713/'], 
        'Mimi Digimon Adult': ['https://br.pinterest.com/pin/59391288832866781/', 'https://br.pinterest.com/pin/209839663883493938/', 'https://br.pinterest.com/pin/415738609349071096/', 'https://br.pinterest.com/pin/48343395986948828/', 'https://br.pinterest.com/pin/145381894219596196/', 'https://br.pinterest.com/pin/109071622221470085/', 'https://br.pinterest.com/pin/408490628716239437/', 'https://br.pinterest.com/pin/176484879144154072/', 'https://br.pinterest.com/pin/426997608397750499/', 'https://br.pinterest.com/pin/15973773657761385/']}

    try:
        parser = ParserHTMLPinterest(dict_links,logger)
        print(asyncio.run(parser.parsing()))

        #Testando Cacheamento do valor de '_dict_links_result
        print("Chamando método 'parsing' novamente para verificar o cacheamento do valor de 'self.dict_links_result'")
        print("\n\n")
        print(asyncio.run(parser.parsing()))
        
    except KeyboardInterrupt as error:
        logger.debug(f"[MAIN] Interrupção do teclado detectada! Interrompendo programa....")
    
    except Exception as error:
        logger.debug("[MAIN] Uma exceçao ocorreu! Verifique o relatório de erro 'Error.log'!")
        logger.error(f"[MAIN] Exceção => {error}\n\nTraceback =>{format_exc()}")


if __name__ == "__main__":
    main()


