"""
Módulo responsável por disponibilizar crawlers para diferentes sites.

Atualmente, este módulo fornece a classe `CrawlerPinterest`, que implementa
as funcionalidades necessárias para realizar o crawling no site do Pinterest,
coletando links de pins a partir de uma lista de prompts fornecida pelo usuário.

Dependências:
    - selenium
    - utils.py (módulo interno desta aplicação)

Exemplo:
    from src.crawler import CrawlerPinterest
    from src.utils import salva_links_pin, configurando_logger
    from selenium import webdriver

    lista_prompts = ["Lucy Heartfilia", "Android 18", "Nami", "Mimi Digimon", "Princess Zelda"]
    logger = configurando_logger(debug_mode=False)
    driver = webdriver.Chrome()

    crawler = CrawlerPinterest(driver, logger, lista_prompts)
    dict_links = crawler.bot_crawler()

    salva_links_pin(dict_links)

Notas:
    Este módulo não deve ser executado diretamente, utilize ele apenas via 'import'.
"""


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

import logging
from utils import configurando_logger
from utils import salva_links_pin
import time
from traceback import format_exc
from abc import ABC,abstractmethod


#Classe Abstrata
class Crawler(ABC):

    """
    Classe base abstrata para crawlers de diferentes sites.

    Esta classe define a interface mínima que todo crawler deve implementar,
    garantindo um comportamento consistente entre diversas plataformas.
    Subclasses devem sobrescrever os métodos abstratos para fornecer a
    lógica específica de cada site.
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def bot_crawler(self):

        """
        Executa o processo principal de crawling.

        Retorna os dados extraídos do site, como links, metadados ou objetos
        estruturados, dependendo da implementação da subclasse.

        """

        pass


#Sub-Classes

class CrawlerPinterest(Crawler):

    """
    Implementação do crawler para o site Pinterest.

    Esta classe executa buscas com base em prompts definidos pelo usuário, coleta links de pins 
    encontrados e retorna os resultados organizados em um dicionário.

    Atributos:
        driver (WebDriver): Navegador controlado pelo Selenium.
        logger (Logger): Logger usado para registrar mensagens e exceções.
        lista_prompt (list[str]): Lista de termos de busca que vão ser uutilizados no Pinterest.
    """

    def __init__(self,driver:WebDriver,logger:logging.Logger,lista_prompt:list[str]):

        self._driver = driver
        self.lista_prompt = lista_prompt
        self.logger = logger

        #Verificando se a lista passada pelo usuário contem algum valor, se nao tiver, levanta uma exceção
        self.logger.debug(f"\n[BOT-CRAWLER] Verificando se o valor passado para o atributo 'logger' não é vazio. ")
        if not self.lista_prompt:
            self.logger.debug("[BOT-CRAWLER] A lista fornecida pelo usuário esta em branco. Levantando exceção e encerrando o programa.")
            self.logger.info("\nNão existe nenhum prompt na lista fornecida!")
            raise ValueError ("\nO valor do argumento 'lista_prompt' não pode ser vazio!")
        
    @property
    def driver(self):
        return self._driver
    
    @driver.setter
    def driver(self, valor):
        raise AttributeError("\nO atributo self._driver não pode ter seu valor modificado diretamente!")

    def bot_crawler(self,max_img:int=10) -> dict[str:list]:

        """
        Método que executa o 'crawling' pelo site do Pinterest.

        O 'bot_crawler' ira interagir com o site do Pinterest, enviando os prompts fornecidos
        pelo usuário, e esperando o retorno dos resultados da pesquisa.

        Dessa forma, ele vai "rolando" a página para baixo, fazendo com que o javascript va revelando
        novos pins de imagens referentes ao prompt, sendo que o link de cada um é coletado e armazenado
        em uma lista que por fim sera armazenada em um dicionário, tendo como chave dela, o prompt que a gerou.

        Args:
            max_img(int): Número máximo de imagens que o usuário quer que o crawler colete.
        
        Returns:
            dict(list): Dicionário que armazena listas contendo os links de cada pin coletado de 
                        um respectivo prompt. Prompt este que entra como chave da lista coletada.
        
        Raises:
            WebDriverException: Exceção levantada caso a conexão falhe durante a requisição da página ao servidor.
            
            TimeoutException: Exceção levantada quando demora demais para realizar a captura de elementos contendo
                              os links de pin da página.
            
            StaleElementReferenceException: Exceção levantada quando, ao tentar capturar os WebElements contendos os pins
                                            o elementos fica na condição de 'Stale' ou seja, ele existia, porem na hora da captura
                                            foi modificado, e não existe mais.
        """
        
        ### Variáveis ###

        #Instancia WebDriverWait
        wait = WebDriverWait(self.driver, 10)

        #Lista que armazena os links de pins que vao ser salvos no 'dict_lista_link'
        lista_pin_final= []

        #Lista que armazena WebElements, mais especificamente tag <a> onde estão os links dos pins
        lista_pin_req = []

        #Dicionario que armazena listas de links dos pins com a chave sendo seu respectivo prompt
        dict_lista_link = {}

        #Variávei que mede tentativas de capturar os elementos depois de um StaleElementReference
        stale_n = 0

        #Variável que mede tentativas de realizar a requisição ao servidor do site Pinterest
        request_n = 0
        
        ### Código ###

        #Iniciando iteração dos prompts

        self.logger.info("Crawler Iniciado!")
        self.logger.debug("[BOT-CRAWLER] Iniciando método 'bot_crawler' para retornar paginas HTML com links de PIN's disponíveis.")

        self.logger.info("Entrando no site do Pinterest....")
        self.logger.debug("[BOT-CRAWLER] Método 'bot_crawler' iniciado. Iniciando a iteração dos valores da lista" \
        " 'self.lista_prompt'")

        for prompt in self.lista_prompt:

            #Formatando a 'lista_pin_final' e 'stale_n' para uma nova requisição de links dos pins da pagina.
            lista_pin_final = []
            stale_n = 0

            #Entrando no site e achando o input de pesquisa
            self.logger.info(f"\nComeçando a procurar imagens do prompt => {prompt}")
            self.logger.debug(f"[BOT-CRAWLER] Entrando no link do pinterest => https://br.pinterest.com/search/pins/?q={prompt}&rs=typed'")

            #Aqui iniciamos um bloco try para tentar reconexões caso a primeira requisição falhe
            while True:
                try:
                    self.logger.debug(f"\n[BOT-CRAWLER] Entrando no link do pinterest => https://br.pinterest.com/search/pins/?q={prompt}&rs=typed'")
                    self.logger.info(f"Realizando a requisição para o o Pinterest com o prompt => {prompt}")

                    self.driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
                    break
                
                except WebDriverException as error:
                    request_n += 1
                    if request_n != 3:
                        self.logger.debug(f"[BOT-CRAWLER] {request_n}ª de 3 tentativas de requisição falhou! Tentando mais uma vez...")
                        self.logger.info(f"{request_n}ª de 3 tentativas - Ocorreu um problema ao tentar conexão com o site do Pinterest.... Vamos tentar mais uma vez!")
                        continue
                    else:
                        #Subindo o método para fora do 'bot_crawler' para a exceção ser tratada
                        self.logger.debug(f"[BOT-CRAWLER] Limite de tentativas alcançado! Fazendo limpeza e encerrando o programa!")
                        self.logger.info("Limite de tentativas alcançado! Problema com a conexão!")
                        raise
                    
            #DEBUG
            time.sleep(4)

            #Inciando iteração para verificar se a quantidade de imagens no HTML Estático corresponde ao valor de 'max_img'.
            self.logger.debug("[BOT-CRAWLER] Verificando a quantidade de elementos contendo as imagens na página " \
            "e se correspondem com o argumento 'max_img'.")
            while True:
                #Tentando encontrar os elementos contendo as imagens na pagina
                try:
                    
                    #Aqui tentamos pegar todos os links de PIN dos cards da tela
                    lista_pin_req = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[@data-test-id='pinWrapper'] //a")))

                    #Vamos chamar o método 'verifica_link_pin' para adicionar apenas pins diferentes a lista de links final 'lista_pin_final'
                    self.verifica_link_pin(lista_pin_final,lista_pin_req)

                    #DEBUG
                    self.logger.debug(f"[BOT-CRAWLER] Valores dentro da 'lista_pin_final' => {lista_pin_final}")

                    #Veririfcando se a quantidade bate com a que foi requisitada
                    if len(lista_pin_final) < max_img:
                        self.logger.info(f"\nAchamos apenas {len(lista_pin_final)} imagens para o prompt => {prompt}")
                        self.logger.info("Vamos procurar mais....")

                        #DEBUG
                        time.sleep(4)
                        
                        #Vamos realizar o rolamento, e ao mesmo tempo, verificar se a página chegou ao fim.
                        if self.verifica_chegou_no_fim():
                            self.logger.debug(f"\n[BOT-CRAWLER] A página chegou ao fim com o prompt {prompt}. Armazenando as imagens do dicionario, encerrando as iterações e seguindo para o próximo prompt.")
                            self.logger.info(f"A página do prompt => {prompt} chegou ao fim! Vamos entao encerrar a captura com {len(lista_pin_final)} imagens!")
                            
                            #Armazenando as imagens do dicionario independente de terem chegado ao max_img definido pelo usuário, e encerrando a iteração
                            dict_lista_link[prompt] = lista_pin_final[0:max_img]
                            break
                    
                    else:
                        #Salvando o HTML estatico no dicionario 'dict_pagina_html' tendo a chave como prompt
                        self.logger.debug(f"\n[BOT-CRAWLER] Achamos {len(lista_pin_final)} imagens da requisição de {max_img} imagens.")
                        self.logger.info(f"Achamos todas as imagens! Salvando os links das imagens do prompt => {prompt}")
                        
                        #Fazemos o slice da lista, limitando o numero de elementos a quantidade que o usuário pediu
                        dict_lista_link[prompt] = lista_pin_final[0:max_img]
                        break
                
                except TimeoutException as error:
                    #Tratando o problema do bloco de login "congelando" a página
                    self.logger.debug(f"\n[BOT-CRAWLER] Exceção 'TimeoutException' levantada com o prompt => {prompt}")
                    self.logger.info(f"Alguma interrupção aconteceu no prompt => {prompt}")
                    self.logger.info(f"Lidando com ela para continuar com o fluxo...")

                    time.sleep(4)
                    self.logger.debug(f"\n[BOT-CRAWLER] Chamando o método 'self.verifica_interrupcao' para lidar com a interrupção no 'crawling' do site.")
                    
                    #Caso a interrupção for por falta de imagens seja "NSFW" ou "prompt sem imagens" não tem porque continuar a iteração. 
                    #Quebramos o ciclo 'while' e seguimos para o próximo prompt.
                    if not self.verifica_interrupcao(prompt):
                        break
                
                except StaleElementReferenceException as error:
                    stale_n += 1
                    self.logger.debug("[BOT-CRAWLER] Exceção 'StaleElementReference' foi levantada. Tentando realizar a captura novamente dos elementos.")
                    self.logger.debug(f"[BOT-CRAWLER] {stale_n}ª Tentativa de capturar novamente os links dos pins...")
                    if stale_n != 3:
                        continue
                    else:
                        self.logger.debug("Quantidade maxima de tentativas de encontrar os elementos alcançada! Encerrando o programa!")
                        #Saindo para fora do método 'bot_crawler' para a exceção ser registrada!
                        raise

        
        #Retornando dicionario com as paginas HTML
        self.logger.debug("\n[BOT-CRAWLER] Iteração de todos os prompts terminada, retornando o dicionario 'dict_pagina_html'.")
        self.logger.info("Captura das páginas terminada!")
        return dict_lista_link
    
    def verifica_link_pin(self, lista_pin_final:list[str], lista_pin_req:list[WebElement]) -> None:

        """
        Método utilizado para verificar quais os links de 'pins' da listad de requisição 'lista_pins_req'
        existem dentro da lista de links de 'pins' final que é a que vai ficar atribuida ao prompt no dicionario
        devolvido pelo método 'bot_crawler'

        Esse método foi criado pois o Pinterest tem uma abordagem de, com o javascript, ir 'desativando' os cards de pin que esta fora da
        tela e 'ativando' os cards novos a cada rolamento da tela. Ele faz isso provavelmente para nao deixar todos os cards
        revelados, o que faria o navegador ficar muito lento.

        Portanto a cada rolamento do "execute_script" os cards antigos "somem" e os cards posteriores que estavam escondidos pelo javascript
        "aparecem". Dessa forma não tem como, por exemplo, revelar todos os cards com o "rolamento" e capturar a pagina inteira. O crawling
        tem que acontecer de maneira "segmentada", capturando links dos pins que esta na tela, rolando a tela para baixo, e realizando a captura
        de novo. 
        
        O problema é que muitas vezes o rolamento não é o suficiente para capturar apenas links de pins novos, ou seja, que ja não foram capturados.
        Muitas vezes alem de links novos, links antigos tambem são capturados.
        
        Dessa forma esse método foi criado para resolver isso. A cada requisição, cada link da lista de links capturados dos pins é utilizado em uma
        verificação onde é checado se ele ja existe na lista de links final 'lista_pin_final', se ja existir nada acontece, agora se não existir
        ele é adicionado a ela.

        Args:
            lista_pin_final (list[str]): Lista contendo todos os links ja salvos e filtrados. Corresponde ao mesmo local
                                         de memória da lista em 'bot_crawler'.

            lista_pin_req(list[WebElement]): Lista contendo os links da ultima requisição que precisam ser filtrados.
        
        """
        
        ### Variáveis ###

        #Variável que extrai o link do WebElement da 'lista_pin_req'
        link = ""

        ### Código ###

        #Vamor iterar cada item da lista final para comparar com a nova requisição
        for link_r in lista_pin_req:
            #Retirando link em formato string
            link = link_r.get_attribute('href')
            if not link in lista_pin_final:
                lista_pin_final.append(link)
          
    def verifica_interrupcao(self, prompt:str) -> bool:
        
        """
        Método que verifica qual tipo de interrupção que ocorreu no fluxo do crawling dentro do 
        'Pinterest'.

        3 casos especificos são checados:

        1º - Se o prompt não devolveu nenhuma 'pin' de imagem.

        2º - Se o prompt contém alguma palavra 'NSFW'

        3º - Se o bloco de 'login' apareceu, bloqueando o SELENIUM de verificar os 'pins' das imagens.

        Caso nenhum dos 3 casos for averiguado, algo que o PinScrapper.py não consegue lidar esta
        bloqueando a ação do 'crawler'. Nesse caso o problema é "grave", e precisa da averiguação do
        desenvolvedor. Nessa situação a exceção 'InvalidSelectorException' é levantada, e um relatório
        sobre o erro é gerado.

        PS: A lista é escolhida propositalmente como objeto para armazenar o WebElement representante das 
            interrupções de falta de imagem e NSFW justamente porque, caso nenhum elemento for encontrado,
            o "find_elements" devolve uma lista vazia, e não levanta uma Exceção como o caso do "find_element".

        Args:
            prompt (str): A string do prompt que esta sendo usado no momento para o 'crawling' de 'pins'.
        
        Raises:
            InvalidSelectorException: Exceção 'levantada' quando nenhum dos 3 casos de interrupção é encontrado.

        """

        ### Variáveis ###

        #Variavel que armazena um WebElement
        bloco_login = None

        #Botão fechar
        botao_fechar = None

        #Lista que vai verificar elemento de bloqueio relacionado a "nudez" no prompt
        nsfw = []

        #Lista que vai verificar elemnto de bloqueio a "nenhuma imagem encontrada"
        no_img = []

        ### Código ###

        self.logger.debug("\nIniciando método 'verifica_interrupção'")
        
        #Verificando se a interrupção é causada pelo prompt não retornar nenhuma imagem.
        self.logger.debug(f"\n[BOT-CRAWLER] Verificando se o problema é não ter retornado nenhum pin do prompt => {prompt}")
        no_img = self.driver.find_elements(By.XPATH,"//div[text()='Não foi possível encontrar Pins para esta pesquisa.']")
        
        #Ação caso for encontrado o texto para o problema de nenhum pin retornado pelo prompt
        if no_img:
            self.logger.debug(f"\n[BOT-CRAWLER] O problema da interrupção foi que nenhum pin retornou pelo prompt => {prompt}")
            self.logger.info(f"Achamos o problema! Nenhuma imagem foi retornada para o prompt => {prompt}")
            self.logger.info("Seguindo com o a pesquisa de 'pins' para próximo prompt....")
            return False
        
        #Verificando se a interrupção é causada pelo prompt insinuar conteúdo NSFW
        self.logger.debug(f"\n[BOT-CRAWLER] Verificando se o problema é possivel conteudo NSFW retornado pelo prompt => {prompt}")
        nsfw = self.driver.find_elements(By.XPATH,"//span[text()='Pins sobre esse interesse costumam violar as ' or text()='Nudez é permitida no Pinterest, mas com ressalvas. Certifique-se de que entendeu ']")

        #Ação caso encontrado mensagem sobre bloqueio da requisição por conteudo NSFW
        if nsfw:
            self.logger.debug(f"\n[BOT-CRAWLER] O problema da interrupção foi o prompt insinuar conteúdo NSFW => {prompt}")
            self.logger.info(f"Achamos o problema! Nenhuma imagem foi retornada para o prompt por ele insinuar NSFW => {prompt}")
            self.logger.info("Seguindo com o a pesquisa de 'pins' para próximo prompt....")
            return False
        
        #Caso não for problemas com o prompt fornecido, verificamos se o bloco de 'login' de bloqueando o acesso do crawler ao site
        try:
            bloco_login = self.driver.find_element(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
            if bloco_login:
                botao_fechar = bloco_login.find_element(By.XPATH,"//button[@aria-label='fechar']")
                botao_fechar.click()
                return True
        
        except (InvalidSelectorException,NoSuchElementException) as error:

            #Problema grave. Algo esta interrompendo o fluxo e que o PinScrapper não consegue lidar
            #Fazendo limpeza e levantando exceção para sair do método e a mesma ser tratada fora.
            self.driver.quit()

            self.logger.info("Bloco Login e textos não encontrados! Erro grave no programa! De uma olhada no log de erro 'Error.log'!")
            self.logger.error(f"[BOT-CRAWLER] Bloco login e textos não encontrados. Outra coisa não esta deixando o CrawlerPinterest encontrar as imagens.")
            
            raise 
    
    def verifica_chegou_no_fim(self) -> bool:

        """
        Método para verificar se a página com os pins chegou no seu rodapé, indicando que não
        existe mais pins para retirar links.

        Para realizar essa verificação, capturamos o eixo Y da DOM atual, realizamos o rolamento
        e depois capturamos novamente o eixo Y para comparar com o primeiro. Se der diferente, o valor
        retornado sera 'False', indicando que ainda existe imagens mais abaixo. Caso seja 'True', indica
        que a página chegou ao fim, não tem mais nada.

        Returns:
            bool: Retorna um booleano indicando se a página chegou ao fim ou não.
        """

        ### Variáveis ###

        #Medida do eixo Y antes do "rolamento"
        scroll_anterior = 0

        #Medida do eixo Y depois do "rolamento"
        scroll_atual = 0

        ### Código ###

        #Capturando eixo Y antes do rolamento
        scroll_anterior = self.driver.execute_script("return window.pageYOffset;")

        #Vamos "rolar" a tela para baixo e tentar fazer o javascript revelar mais imagens
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #Capturando o eixo Y atual
        scroll_atual = self.driver.execute_script("return window.pageYOffset;")

        #Retornando booleana da comparação entre as duas
        return scroll_anterior == scroll_atual


#Função Main para DEBUG

def main():

    ### Variáveis ###

    #Testando instancia do CrawlerImagens na captura de páginas HTML
    mock_lista_prompt = ["Lucy Heartfilia","Android 18", "Nami","Digimon 1 Mimi adult","Princess Zelda"] 
    mock_lista_prompt_vazia = []
    logger = configurando_logger(debug_mode=False)
    driver = webdriver.Chrome()
    dict_links = {}
    c = None

    ### Código ###

    try:
        #Crawler com lista normal
        c = CrawlerPinterest(driver,logger,mock_lista_prompt)

        #Crawler com lista vazia
        #c = CrawlerPinterest(driver,logger,mock_lista_prompt_vazia)
        dict_links = c.bot_crawler()

        #Verificando páginas capturadas em arquivo
        salva_links_pin(dict_links)
    
    except Exception as error:
        logger.info("Uma Exceção foi levantada! Verifique o relatório 'Error.log' para mais informações.")
        print("\n\n")
        logger.error(f"Exceção => {error}\n\nTraceback => {format_exc()}")
    
    except KeyboardInterrupt as error:
        logger.info("\nInterrupção pelo teclado detectada!")
        logger.info("\nEncerrando o programa....")
    
    finally:
        if isinstance(c,CrawlerPinterest):
            c.driver.quit()


if __name__ == "__main__":
    main()
