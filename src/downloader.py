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

import asyncio
import aiohttp
from pathlib import Path
import logging
from utils import configurando_logger


# Classes

class Downloader:

    def __init__(self,logger:logging.Logger,dict_lista_links:dict[str,list[str]]):

        self._dict_lista_links = dict_lista_links
        self.logger = logger
        self._numero_produtores = len(dict_lista_links)
        
    async def downloading(self):
        
        ### Variáveis ###

        #Instancia do asyncio.Queue para criação da pipeline
        fila = None

        #Instancia do asyncio.Event utilizando para sinalizar o fim da pipeline
        evento = None

        #Instancia do asyncio.Semaphore para limitar a quantidade de requisições aos mesmo tempo
        semaforo = None

        #Lista de 'tasks' do método '_bot_requisicao'
        lista_task_requisicao = []

        #Lista de 'tasks' do método '_bot_salva_imagens'
        lista_task_salva_imagens = []

        #Numero 'ID' para ser atribuido a cada 'task' do método '_bot_requisicao'
        n_req = 0

        #Instancia de asyncio.Lock para limitar a utilização de um bloco de codigo para um task por vez
        lock = None

        ### Código ###

        self.logger.debug(f"[DOWNLOADING] - Método 'downloading' iniciado! ")

        #Iniciando Instancias que serão utilizadas
        fila = asyncio.Queue()
        evento = asyncio.Event()
        semaforo = asyncio.Semaphore(3)
        lock = asyncio.Lock()

        #Inicializando tarefas
        self.logger.debug(f"\n[DOWNLOADING] - Inicializando lista de 'tasks' dos métodos '_bot_requisicao' e '_bot_salva_imagens'")
        self.logger.debug(f"\n[DOWNLOADING] - QUantidade de 'Produtores' criada tendo como referencia a quantidade de elementos do atributo 'self._dict_lista_links'")
        for prompt,lista_img in self._dict_lista_links.items():
            n_req += 1
            lista_task_requisicao.append(asyncio.create_task(self._bot_requisicao(n_req,prompt,lista_img,fila,evento,semaforo,lock)))
        lista_task_salva_imagens = [asyncio.create_task(self._bot_salva_imagens()) for n in range(len(self._dict_lista_links))]

        #Chamando o método 'join' para esperar fim da pipeline antes de seguir com o fluxo
        self.logger.debug("\n[DOWNLOADING] - Método 'join' chamado para 'travar' o método 'downloading' até o fluxo da pipeline ser finalizado.")
        await fila.join()

        #Chamando a função 'gather' para esperar o fim das tarefas
        self.logger.debug("\n[DOWNLOADING] - Função 'gather' chamada para aguardar as tarefas que ainda estão finalizando")
        await asyncio.gather(*lista_task_salva_imagens,*lista_task_requisicao)

        self.logger.debug("[DOWNLOADING] - Bots de requisição e salvar imagens finalizados! Encerrando o programa!")

    async def _bot_requisicao(self,numero_id:int,prompt:str,lista_links_img:list[str],fila:asyncio.Queue,evento:asyncio.Event, semaforo:asyncio.Semaphore, lock:asyncio.Lock):

        ### Variáveis ###

        #Bytes de imagem armazenados
        img_io = ""

        #Lista de imagens em formato bytes de cada prompt
        lista_img_bytes = []

        #Número limite de requisições
        n_req = 0

        ### Código ###

        #Abrimos um bloco 'Semaphore' para limitar o numero de interações por 'task'
        async with semaforo:
            async with aiohttp.ClientSession() as session:
                #Iterando em cada link e tentando requisição dos bytes da imagem
                for link in lista_links_img:

                    #Reiniciando o numero de tentativas de requisição
                    n_req = 0

                    while True:
                        async with session.get(link) as resp:
                            #Verificando status da resposta
                            if resp.status == 200:
                                
                                #Retirando bytes da imagem da requisição
                                img_io = await resp.read()

                                #Atribuindo bytes da imagem a lista de bytes
                                lista_img_bytes.append(img_io)
                            
                            else:
                                n_req += 1
                                self.logger.debug(f"\n[BOT_REQUISICAO - {numero_id}] - {n_req}ª Tentantiva de requisição do link => {link} falhou!")
                                self.logger.info(f"\n Algo deu errado na requisição do link => {link} - para o prompt '{prompt}'. Vamos tentr mais uma vez....")
                                if n_req < 3:
                                    self.logger.debug(f"\n[BOT_REQUISICAO - {numero_id}] - Tentando novamente requisição do link => {link}")
                                    continue
                                
                                else:
                                    self.logger.debug(f"\n[BOT_REQUISICAO - {numero_id}] - Número limite de tentativas alcançado! Ignorando o link => {link} - e seguindo com o fluxo....")
                                    self.logger.info(f"Limite de tentativas de requisição para o link => {link} do prompt '{prompt}' excedido! Vamos ignora-lo por enquanto e seguir em frente...")
                                    break

        #Colocando tupla de prompt com a lista de bytes na pipeline
        await fila.put((prompt, lista_img_bytes)) 

        #Sinalizando introdução na pipeline e verificando se pode ativar a flag do 'Event'
        async with lock:
            self._numero_produtores -= 1
            if not self._numero_produtores:
                evento.set()

    async def _bot_salva_imagens(self):
        pass


#Função Main para Depuração

def main():
    pass


if __name__ == "__main__":
    main()
    