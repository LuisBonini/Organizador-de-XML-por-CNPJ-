# 🚀 Organizador Fiscal de XMLs

Uma aplicação de desktop (feita em Python e Streamlit) que processa lotes de arquivos XML de NF-e, organiza os dados por CNPJ e gera relatórios gerenciais detalhados em Excel automaticamente.

Este projeto foi criado para automatizar a consolidação fiscal para empresas ou escritórios de contabilidade que gerenciam múltiplos CNPJs, transformando um trabalho de horas em segundos.

![GIF da Aplicação](httpsData/app-demo.gif)
*(Dica: Grave um GIF curto da tela do Streamlit e coloque aqui.)*

---

## ✨ Funcionalidades

* **Interface Gráfica Amigável:** Construído com Streamlit para ser uma aplicação web local fácil de usar, com upload de arquivos "arraste e solte".
* **Gerenciamento Multi-CNPJ:** Processa os XMLs de forma inteligente, identificando se a nota é de entrada ou saída com base em uma lista de CNPJs cadastrados.
* **Cadastro de CNPJs:** Uma tela de "Configurações" permite ao usuário adicionar ou remover os CNPJs da empresa sem mexer no código (salvos em `cnpjs_config.json`).
* **Relatórios Detalhados por CNPJ:** Gera um arquivo Excel separado para cada CNPJ da empresa encontrado nos XMLs.
* **Abas Organizadas:** Cada Excel gerado contém 6 abas:
    1.  `1. Vendas por Cliente` (Resumo)
    2.  `2. Compras por Fornecedor` (Resumo)
    3.  `3. Total Saídas (Notas)` (Detalhe por Nota)
    4.  `4. Total Entradas (Notas)` (Detalhe por Nota)
    5.  `5. Detalhe Saídas (Itens)` (Detalhe por Item)
    6.  `6. Detalhe Entradas (Itens)` (Detalhe por Item)
* **Download em .ZIP:** Se o processamento gerar relatórios para mais de um CNPJ, a aplicação os compacta automaticamente em um único arquivo `.zip` para download.

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **Streamlit:** Para a criação da interface gráfica (GUI).
* **Pandas:** Para manipulação e agregação dos dados.
* **Openpyxl:** Para a criação dos arquivos Excel (usado pelo Pandas).
* **Poetry:** Para gerenciamento de dependências e do ambiente virtual.
* **PyInstaller:** Para compilar o projeto em um arquivo executável (`.exe`) para distribuição no Windows.

---

## 💻 Como Rodar (Para Desenvolvedores)

Se você quiser rodar o projeto a partir do código-fonte:

1.  **Clone o repositório:**
    ```bash
    git clone [URL-DO-SEU-REPOSITORIO]
    cd [NOME-DA-PASTA-DO-PROJETO]
    ```

2.  **Instale as dependências com Poetry:**
    (Assumindo que você já tem o [Poetry](https://python-poetry.org/) instalado)
    ```bash
    poetry install
    ```

3.  **Execute a aplicação:**
    Este projeto usa um script `run.py` para iniciar o servidor Streamlit em segundo plano e abrir o navegador.
    ```bash
    poetry run python run.py
    ```
    A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`.

## 📦 Como Compilar (Gerar o `.exe`)

Para gerar o arquivo executável para distribuição no Windows, usamos o `run.py` como ponto de entrada e adicionamos o `app.py` como um dado (para que o `run.py` possa encontrá-lo).

```bash
poetry run pyinstaller --onefile --windowed --add-data "app.py;." run.py