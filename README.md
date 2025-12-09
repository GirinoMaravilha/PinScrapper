# 🚀 PinScrapper - Scrapper de imagens do Pinterest

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Build](https://img.shields.io/badge/build-passing-success)

---

# 📘 O que é o "Pinscrapper"?

O "Pinscrapper" é um **Scrapper completo de imagens do Pinterest** desenvolvido em **Python**, com o foco de facilitar a pesquisa, coleta, e registro de imagens do Pinterest no Sistema Operacional do usuário.


## ⚙️ Como instalar o "Pinscrapper"

```bash
# Clone o repositório
git clone https://github.com/GirinoMaravilha/Pinscrapper.git

# Entre na pasta do projeto
cd Pinscrapper

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente (Linux)
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```
E pronto! Você ja pode utilizar o "Pinscrapper!"


### Sobre a utilização

Utilizar o "Pinscrapper" é muito simples. Na linha de comando você vai ter as seguintes opções para configurar o "scrapping" das imagens do Pinterest:

+ **--monitor**: O modo "monitor" faz com que o navegador fique visível durante o 'crawling' do  site. O modo padrão é ele ficar desativado (headless).

+ **--debug**: O modo "debug" faz com que todos os "logs" de depuração sejam mostrados no console. Bom para entender o que esta acontecendo nos "bastidores" durante o "scrapping".

+ **prompts**: Argumento obrigatório. O endereço absoluto de um arquivo ".txt" no Sistema Operacional onde os prompts que serão utilizados nas pesquisas estão localizados.

+ **--img_q**: A quantidade de imagens que o usuário deseja que sejam coletadas.


### Configuração dos prompts para a pesquisa

Em um arquivo **".txt"**, o usuário devera escrever os prompts que ele quer utilizar **um por linha**. Exemplo:

```text

Gato
Cachorro
Bolo de cenoura

```

Após isso, basta entrar na pasta **src/** e executar o "Pinscrapper.py" na linha de comando!

#### Exemplo:

```bash

python13.3 Pynscrapper.py lista_prompts.txt --img_quant 20 --monitor

```
E pronto! O programa ira entrar no site do Pinterest e realizar toda a pesquisa e download de imagems para você!


### Onde as imagens ficam salvas?

As imagens são salvas em diretórios que levam como nome o "prompt" que as geraram, que ficam localizados em um diretório de nome "Pinscrapper", que leva a data do momento da execução do script. 

No caso, se o script foi executado no dia **08/04/2026** todas as imagens do "prompt" de nome **"gato"**, ficaram salvas em um diretório com o nome **"gato"**, dentro de um diretório chamando **"Pinscrapper 08 04 2026"**, por exemplo.

---


## 🧩 Estrutura do Projeto

```
📦 task_manager
 ┣ 📂 src
 ┃ ┣ 📜 crawler.py
 ┃ ┣ 📜 downloader.py
 ┃ ┣ 📜 parser.py.py
 ┃ ┣ 📜 utils.py
 ┃ ┗ 📜 Pinscrapper.py
 ┣ 📂 tests
 ┃ ┣ 📜 conftest.py
 ┃ ┣ 📜 test_crawler.py
 ┃ ┗ 📜 test_parser.py
 ┣ 📜 README.md
 ┣ 📜 requirements.txt
 ┗ 📜 LICENSE
```

## 🧰 Tecnologias Utilizadas

| Tecnologia | Descrição |
|-------------|------------|
| **Python 3.11** | Linguagem principal do projeto |
| **BeautifulSoup** | Framework de para "Parsing" de páginas HTML |
| **PyTest** | Framework de testes automatizados |
| **Aiohttp** | Ferramenta para realizar requisições assíncronas a servidores |
| **Selenium** | Framework que realiza o "Crawling" do site, com o foco no Javascript do front-end |

---


## 🧪 Testes

```bash
pytest tests/
```

---

## 📄 Licença

Este projeto está sob a licença [MIT](https://github.com/GirinoMaravilha/PinScrapper?tab=MIT-1-ov-file).  
Sinta-se livre para usar, modificar e distribuir este código.

---

## 💬 Contato

📧 **Autor:** Girino Maravilha
🌐 [GitHub](https://github.com/GirinoMaravilha) 

---

> Feito por Girino Maravilha - Estudo e prática de boas práticas em Python.
