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

#TODO Tarefas que ainda faltam:
#- Fazer a documentação do módulo
#- Fazer a documentação dos métodos e classes
#- Fazer o encapsulamento dos atributos
#- Verificar se existem mais exceções para serem tratadas

import asyncio
import aiohttp
from pathlib import Path
import logging
from utils import configurando_logger
from utils import salva_imagem
from pathlib import Path
import time


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
        lista_task_salva_imagens = [asyncio.create_task(self._bot_salva_imagens(n+1,fila,evento)) for n in range(len(self._dict_lista_links))]

        #Chamando o método 'join' para esperar fim da pipeline antes de seguir com o fluxo
        self.logger.debug("\n[DOWNLOADING] - Método 'join' chamado para 'travar' o método 'downloading' até o fluxo da pipeline ser finalizado.")
        await fila.join()

        #Chamando a função 'gather' para esperar o fim das tarefas
        self.logger.debug("\n[DOWNLOADING] - Função 'gather' chamada para aguardar as tarefas que ainda estão finalizando")
        await asyncio.gather(*lista_task_salva_imagens,*lista_task_requisicao)

        self.logger.debug("[DOWNLOADING] - Bots de requisição e salvar imagens finalizados! Encerrando o programa!")

    async def _bot_requisicao(self,numero_id:int,prompt:str,lista_links_img:list[str],fila:asyncio.Queue,evento:asyncio.Event, semaforo:asyncio.Semaphore, lock:asyncio.Lock) -> None:

        ### Variáveis ###

        #Bytes de imagem armazenados
        img_io = ""

        #Lista de imagens em formato bytes de cada prompt
        lista_img_bytes = []

        #Número limite de requisições
        n_req = 0

        ### Código ###

        self.logger.debug(f"[BOT_REQUISICAO - {numero_id}] Bot inicializado!")
        self.logger.info(f"Fazendo o download das imagens do prompt => {prompt}")

        #Abrimos um bloco 'Semaphore' para limitar o numero de interações por 'task'
        async with semaforo:
            async with aiohttp.ClientSession() as session:
                #Iterando em cada link e tentando requisição dos bytes da imagem
                for link in lista_links_img:

                    #Reiniciando o numero de tentativas de requisição
                    n_req = 0

                    self.logger.debug(f"[BOT_REQUISICAO - {numero_id}] Tentando fazer a requisição do link => {link}")
                    while True:
                        async with session.get(link) as resp:
                            #Verificando status da resposta
                            if resp.status == 200:
                                
                                #Retirando bytes da imagem da requisição
                                img_io = await resp.read()

                                #DEBUG para testar se estamos pegando bytes das imagens corretamente
                                #salva_imagem(img_io)

                                self.logger.debug(f"[BOT_REQUISICAO - {numero_id}] Requisição bem sucedida! Armazenando bytes do link => {link} - na lista 'lista_img_bytes'")

                                #Atribuindo bytes da imagem a lista de bytes e passando para o proximo link
                                lista_img_bytes.append(img_io)
                                break
                            
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
        self.logger.debug(f"[BOT_REQUISICAO - {numero_id}] Inserindo tupla com o prompt e a lista de bytes 'lista_img_bytes' na pipeline")
        await fila.put((prompt, lista_img_bytes)) 

        self.logger.info(f"\nDownload das imagens do prompt => {prompt} - Finalizado!")

        #Sinalizando introdução na pipeline e verificando se pode ativar a flag do 'Event'
        self.logger.debug(f"[BOT_REQUISICAO - {numero_id}] Sinalizando fim da produção e verificando o numero de produtores ativos, caso não haja nenhum, ativando flag do 'Event'")
        async with lock:
            self._numero_produtores -= 1
            if not self._numero_produtores:
                self.logger.debug(f"[BOT_REQUISICAO - {numero_id}] Todos os produtores terminaram! Ativando a flag do 'Event'.")
                evento.set()

    async def _bot_salva_imagens(self, numero_id:int, fila:asyncio.Queue, evento:asyncio.Event) -> None:
        
        ### Variáveis ###

        #Valor do prompt e lista de bytes de imagens do mesmo
        prompt = ""
        lista_bytes_img = []

        ### Código ###

        self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Bot Iniciado!")
 
        #Iniciando a iteração de produção
        while True:
            #Verificando se a produção esta finalizada
            if fila.empty() and evento.is_set():
                self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Pipeline vazia! Flag do 'Event' esta ativada! Produção finalizada, encerrando o bot...")
                break
            
            #Retirando e processando valor da pipeline
            self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Tentando retirar valor da pipeline")
            try:
                prompt,lista_bytes_img = await asyncio.wait_for(fila.get(),5)
                self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Valor retirado com sucesso!")

                #Salvando list de imagens em um diretório que leva o nome do prompt
                self.logger.info(f"Salvando imagens do prompt => {prompt} - no computador....")
                self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Criando diretório com o nome do prompt => {prompt} e salvando imagens nele")
                self._salva_imagens(prompt,lista_bytes_img)

                #Sinalizando que um item da pipeline ja foi processado
                self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Imagens dos prompt '{prompt}' salvas! Sinalizando para a pipeline que um item ja foi processado")
                self.logger.info(f"Registro no computador das Imagens do prompt => '{prompt}' - finalizados!")
                fila.task_done()

            except asyncio.TimeoutError as error:
                self.logger.debug(f"[BOT_SALVA_IMG - {numero_id}] Bot demorou demais para retirar valor da pipeline! Seguindo o fluxo...")
                continue
    
    def _salva_imagens(self, prompt:str, lista_bytes_img:list[str]) -> None:

        ### Variáveis ###

        #Instancia Path
        path = None

        #Valor do tempo atual duranto a execução do programa
        data = ""
        hora = ""

        #Número da imagem
        n_img = 0

        ### Código ###

        #Capturando tempo atual
        data = time.strftime(fr"%d %m %Y",time.localtime())
        hora = time.strftime(fr"%H %M %S",time.localtime())

        #Iniciando instancia Path e criando diretório Principal
        path = Path(f"Imagens_Pinterest - {data}")
        path = path / prompt
        
        #Tentando criar um diretório com o valor de 'prompt'
        try:
            path.mkdir(exist_ok=True, parents=True)
        
        except (ValueError,OSError) as error:
            path = Path(f"Imagens_Pinterest - {data}")
            path = path / f"Captura de Imagens {hora}"
            path.mkdir(exist_ok=True, parents=True)
        
        #Iterando valores da 'lista_bytes_img' para salvar as imagens
        for img_bytes in lista_bytes_img:
            n_img += 1
            with open(f"{path}/img{n_img}.jpg","wb") as img:
                img.write(img_bytes)


#Função Main para Depuração

def main():

    dict_links_img = {'Mimi Digimon Adult': ['https://i.pinimg.com/736x/72/99/b3/7299b363d59eaba3ba8cccece96a2815.jpg', 'https://i.pinimg.com/736x/90/6e/c5/906ec59eb6f1dd2780eaa283db59e4fe.jpg', 
                                             'https://i.pinimg.com/736x/96/b1/34/96b134d9a605eac02a1a1693137b3974.jpg', 'https://i.pinimg.com/736x/39/c5/ac/39c5ac79e3782ff576ad3f6a6b4351f2.jpg', 
                                             'https://i.pinimg.com/736x/3f/e7/d1/3fe7d1fa3a4ad1178ead57451f7a52df.jpg', 'https://i.pinimg.com/736x/6b/72/cb/6b72cbfb5e7600b783b6b76055b803fd.jpg', 
                                             'https://i.pinimg.com/736x/14/99/c6/1499c6640b438ab19bf875fca1a96b39.jpg', 'https://i.pinimg.com/736x/e0/fb/6a/e0fb6ad2da0893929b85c51b28f79001.jpg', 
                                             'https://i.pinimg.com/736x/a0/dc/d7/a0dcd7433bf03afc4ceb9beadce63716.jpg', 'https://i.pinimg.com/736x/fb/15/f3/fb15f35b662608853cca87e2e8347d9c.jpg'],

                      'Nami One Piece': ['https://i.pinimg.com/736x/ae/60/76/ae607673ca5a12fa09c795cb5abc5451.jpg', 'https://i.pinimg.com/736x/19/b6/76/19b67645a6d0956c69dc4ceeebc8d04f.jpg', 
                                         'https://i.pinimg.com/736x/8f/23/19/8f23190beada3d1f54cc39d0515d1dc8.jpg', 'https://i.pinimg.com/736x/19/82/a6/1982a6184011e41357552a98242da639.jpg', 
                                         'https://i.pinimg.com/736x/c0/cd/c3/c0cdc34756a9a4d7459ccb2d6c3ee023.jpg', 'https://i.pinimg.com/736x/e2/9d/8e/e29d8e0b2099b748672227813d95e29f.jpg', 
                                         'https://i.pinimg.com/736x/cf/67/c5/cf67c58400be876cad95f47b687b28ea.jpg', 'https://i.pinimg.com/736x/9b/7b/46/9b7b461a259f0862c758840403bb9202.jpg', 
                                         'https://i.pinimg.com/736x/c7/e4/69/c7e46919f4f4937b9fbc000982ab913a.jpg', 'https://i.pinimg.com/736x/10/45/6a/10456a9bc13a5ca5822c45b61e5d6571.jpg'], 

                      'Lucy Heatfilia': ['https://i.pinimg.com/736x/35/63/e2/3563e2ffd807a83dff9f7a29ca78c90c.jpg', 'https://i.pinimg.com/736x/66/f8/42/66f842cd3eb5817e4c99eeaf73cdb4bf.jpg', 
                                         'https://i.pinimg.com/736x/cc/61/dd/cc61dd6dfe86ebf4a4f2f4578f7edf15.jpg', 'https://i.pinimg.com/736x/8d/18/5f/8d185fee68d0364280918b6e213e3665.jpg', 
                                         'https://i.pinimg.com/736x/fd/ec/96/fdec969f9aa0fedc5cd75e3f9415a3f0.jpg', 'https://i.pinimg.com/736x/14/ad/87/14ad87e48ba41e837511f0a4707ed109.jpg', 
                                         'https://i.pinimg.com/736x/67/77/4e/67774e9bf2f30e5197e894db3d55ec98.jpg', 'https://i.pinimg.com/736x/0b/cb/4a/0bcb4a0b80219c2cf07c4181cfdad6b1.jpg', 
                                         'https://i.pinimg.com/736x/b3/96/4b/b3964b9f9d3ca4aa41d29428e167ce5b.jpg', 'https://i.pinimg.com/736x/d7/25/72/d72572ae4a7314f5172ea194139449ac.jpg']}
    
    logger = configurando_logger(debug_mode=False)
    d = Downloader(logger,dict_links_img)

    #Testando instancia de Downloader
    asyncio.run(d.downloading())


if __name__ == "__main__":
    main()
    