from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException

import time


# Classes

class MockCrawlerPinterest:

    """
    Um 'Mock' da classe 'CrawlerPinterest' localizada no modulo 'crawler' dentro do pacote 'src'.

    Classe usada para testar funcionalidades da classe de quem foi baseada.
    """

    def __init__(self, driver:WebDriver):
        
        self.driver = driver
 
    def test_bot_crawler_stale_exception(self):

        #TODO Não esta funcionando!
        #Não realiza testes de tratamento do StaleElementReference!

        """
        Método teste para verificar se parte do código do método orginal consegue lidar com exceções
        'StaleElementReferenceException'.
        """

        ### Variáveis ###

        #Variável que armazena o numero de tentativas de captura do elemento
        stale_n = 0

        #Código HTML contendo o Javscript que modifica a DOM uma vez
        html = """
        <div class="pin">Original</div>

        <script>
        requestAnimationFrame(() => {
            const original = document.querySelector('.pin');
            original.remove();

            requestAnimationFrame(() => {
                const novo = document.createElement('div');
                novo.className = 'pin';
                novo.textContent = 'Novo elemento';
                document.body.appendChild(novo);
            });
        });
        </script>
        """

        #Variável que armazena elemento coletado
        pin = None

        ### Código ###

        self.driver.get(f"data:text/html," + html)
        time.sleep(10)
        while True:
            #Aqui emulamos a tentativa de capturar um PIN
            try:
                pin = self.driver.find_element(By.CSS_SELECTOR,".pin")
                print(f"Retornando texto do elemento coletado => {pin.text}")
                #Caso conseguirmos capturar o elemento, quebramos o ciclo e encerramos o método
                break

            #Caso a exceção seja levantada, tentamos de novo até esgotar as tentivas
            except StaleElementReferenceException as error:
                stale_n += 1

                if stale_n < 3:
                    print(f"\nExceção StaleElementeReferenceException levantada! Tentando capturar o elemento novamente!")
                    time.sleep(2)

                else:
                    print(f"Número máximo de tentativas alcançado! Realizando limpeza e levantando exceção!")
                    self.driver.quit()
                    raise StaleElementReferenceException

    def test_verifica_interrupcao(self,lista_prompt:list[str]) -> None:
        
        """
        Método teste para verificar se o código do método original esta conseguindo encontrar e
        fechar o bloco de login, que é uma das interrupções que podem ocorrer durante o crawling
        do Pinterest.
        """
        #Vamos forçar o bloco de login a aparecer fazendo varias requisições

        for prompt in lista_prompt:
            self.driver.get(f"https://br.pinterest.com/search/pins/?q={prompt}&rs=typed")
            time.sleep(2)

        #Vamos tentar encontrar o bloco de login e fecha-lo
        try:
            bloco_login = self.driver.find_element(By.XPATH, "//div[@data-test-id='login-modal-default' and @class='ADXRXN']")
            if bloco_login:
                botao_fechar = bloco_login.find_element(By.XPATH,"//button[@aria-label='fechar']")
                botao_fechar.click()

                #Tempo para verificar se a pagian de Login fechou
                time.sleep(5)

                return True
        
        #Caso não encontrar fazemos limpe-za e levantamos uma exceção
        except InvalidSelectorException as error:

            self.driver.quit()
            
            raise InvalidSelectorException
        
        except NoSuchElementException as error:

            self.driver.quit()
            
            raise NoSuchElementException


#Função Main para DEBUG direto sem o 'pytests'

def main():
    
    driver = webdriver.Chrome()
    lista_prompt = ['Lucy Heartfilia hot', 'Androi 18', 'Digimon 1 Mimi Adult']
    

    mockc = MockCrawlerPinterest(driver)
    #mockc.test_verifica_interrupcao(lista_prompt)
    mockc.test_bot_crawler_stale_exception()
    mockc.driver.quit()


if __name__ == "__main__":
    main()