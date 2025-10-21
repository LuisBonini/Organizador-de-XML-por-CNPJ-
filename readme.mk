# 🚀 Organizador Fiscal de XMLs

Uma aplicação de desktop (feita em Python e Streamlit) que processa lotes de arquivos XML de NF-e, organiza os dados por CNPJ e gera relatórios gerenciais detalhados em Excel automaticamente.

Este projeto foi criado para automatizar a tediosa tarefa de consolidação fiscal para empresas ou escritórios de contabilidade que gerenciam múltiplos CNPJs, transformando um trabalho de horas em segundos.

![GIF da Aplicação](httpsData/app-demo.gif)
*(Dica: Grave um GIF curto da tela do Streamlit e coloque aqui. É muito profissional!)*

---

## ✨ Features (Funcionalidades)

* **Interface Gráfica Amigável:** Construído com Streamlit para ser uma aplicação web local fácil de usar.
* **Gerenciamento Multi-CNPJ:** Permite cadastrar múltiplos CNPJs (matriz e filiais) e processa os XMLs de forma inteligente, separando os relatórios.
* **Cadastro de CNPJs:** Uma tela de configuração permite ao usuário adicionar ou remover CNPJs sem precisar mexer no código (salvos em `cnpjs_config.json`).
* **Relatórios Detalhados:** Gera arquivos Excel com 6 abas, incluindo:
    * Resumo de Vendas por Cliente
    * Resumo de Compras por Fornecedor
    * Listagem de Notas de Saída (1 linha por nota)
    * Listagem de Notas de Entrada (1 linha por nota)
    * Detalhe de Itens de Saída (1 linha por item)
    * Detalhe de Itens de Entrada (1 linha por item)
* **Download em .ZIP:** Se o processamento gerar relatórios para mais de um CNPJ, a aplicação os compacta automaticamente em um único arquivo `.zip`.
* **Formatação Automática:** Os arquivos Excel gerados têm formatação (Arial 10) e ajuste automático da largura das colunas.

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **Streamlit:** Para a criação da interface gráfica (GUI).
* **Pandas:** Para manipulação e agregação dos dados.
* **XlsxWriter:** Para a criação e formatação dos arquivos Excel.
* **Poetry:** Para gerenciamento de dependências e do ambiente virtual.
* **PyInstaller:** Para compilar o projeto em um arquivo executável (`.exe`) para distribuição no Windows.

---

## 🚀 Como Usar (Para Usuários)

Para usuários que não são desenvolvedores, uma versão compilada (`.exe`) está disponível [link para a página de Releases, se você criar uma].

Basta baixar a pasta, seguir as instruções do `leia-me.txt` (basicamente, cadastrar os CNPJs no arquivo `cnpjs_config.json` e clicar no `.exe`).

## 💻 Como Rodar (Para Desenvolvedores)

Se você quiser rodar o projeto a partir do código-fonte:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/organizador-fiscal.git](https://github.com/SEU-USUARIO/organizador-fiscal.git)
    cd organizador-fiscal
    ```

2.  **Instale as dependências com Poetry:**
    ```bash
    poetry install
    ```

3.  **Execute a aplicação Streamlit:**
    ```bash
    poetry run streamlit run app.py
    ```
    A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`.

## 📦 Como Compilar (Gerar o `.exe`)

Para gerar o arquivo executável para distribuição no Windows:

```bash
poetry run pyinstaller --onefile --windowed --add-data "app.py;." run.py
```
O `.exe` final estará na pasta `dist/`.