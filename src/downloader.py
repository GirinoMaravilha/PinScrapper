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


# Classes

class Downloader:

    def __init__(self):
        pass

    async def download(self):
        pass

    async def _bot_requisicao(self):
        pass

    async def _bot_registro(self):
        pass


#Função Main para Depuração

def main():
    pass


if __name__ == "__main__":
    main()
    