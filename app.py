# app.py (Versão Streamlit V4 - Sem Formatação de Excel)

import streamlit as st
import pandas as pd
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import io
import zipfile
# A importação de 'openpyxl.styles' foi REMOVIDA

# --- Configuração de CNPJs ---
CONFIG_FILE = 'cnpjs_config.json'

def carregar_cnpjs():
    """Lê a lista de CNPJs do arquivo de configuração."""
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def salvar_cnpjs(lista_cnpjs):
    """Salva a lista de CNPJs no arquivo de configuração."""
    cnpjs_limpos = []
    for cnpj in lista_cnpjs:
        cnpj_numeros = "".join(filter(str.isdigit, cnpj))
        if len(cnpj_numeros) == 14:
            cnpjs_limpos.append(cnpj_numeros)
        
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cnpjs_limpos, f, indent=4)

# --- Lógica de Processamento de XML ---

def processar_xml(file_object, nome_arquivo):
    """
    Processa um único arquivo XML (lido do upload do Streamlit).
    Removemos a lógica de ICMS/IPI Creditável.
    """
    try:
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        tree = ET.parse(file_object)
        root = tree.getroot()

        infNFe = root.find('.//nfe:infNFe', ns)
        if infNFe is None:
            return [] 

        dados_capa = {
            'Arquivo': nome_arquivo,
            'Numero NF': infNFe.find('.//nfe:ide/nfe:nNF', ns).text,
            'Data Emissao': infNFe.find('.//nfe:ide/nfe:dhEmi', ns).text.split('T')[0],
            'CNPJ Emitente': infNFe.find('.//nfe:emit/nfe:CNPJ', ns).text,
            'Nome Emitente': infNFe.find('.//nfe:emit/nfe:xNome', ns).text,
        }
        try:
            dados_capa['CNPJ Destinatario'] = infNFe.find('.//nfe:dest/nfe:CNPJ', ns).text
        except AttributeError:
            try:
                dados_capa['CNPJ Destinatario'] = infNFe.find('.//nfe:dest/nfe:CPF', ns).text
            except AttributeError:
                dados_capa['CNPJ Destinatario'] = ""
        
        dados_capa['Nome Destinatario'] = infNFe.find('.//nfe:dest/nfe:xNome', ns).text
        dados_capa['Valor Total da Nota'] = float(infNFe.find('.//nfe:total/nfe:ICMSTot/nfe:vNF', ns).text)
        
        lista_de_itens = []

        for item in root.findall('.//nfe:det', ns):
            
            vICMS = item.find('.//nfe:imposto/nfe:ICMS//nfe:vICMS', ns)
            vIPI = item.find('.//nfe:imposto/nfe:IPI//nfe:vIPI', ns)
            vPIS = item.find('.//nfe:imposto/nfe:PIS//nfe:vPIS', ns)
            vCOFINS = item.find('.//nfe:imposto/nfe:COFINS//nfe:vCOFINS', ns)
            
            dados_item = {
                'SKU': item.find('.//nfe:prod/nfe:cProd', ns).text,
                'Produto': item.find('.//nfe:prod/nfe:xProd', ns).text,
                'NCM': item.find('.//nfe:prod/nfe:NCM', ns).text,
                'CFOP': item.find('.//nfe:prod/nfe:CFOP', ns).text,
                'Quantidade': float(item.find('.//nfe:prod/nfe:qCom', ns).text),
                'Valor Unitario': float(item.find('.//nfe:prod/nfe:vUnCom', ns).text),
                'Valor Produto': float(item.find('.//nfe:prod/nfe:vProd', ns).text),
                
                'Base ICMS': float(item.find('.//nfe:imposto/nfe:ICMS//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:ICMS//nfe:vBC', ns) is not None else 0,
                'Aliq ICMS': float(item.find('.//nfe:imposto/nfe:ICMS//nfe:pICMS', ns).text) if item.find('.//nfe:imposto/nfe:ICMS//nfe:pICMS', ns) is not None else 0,
                'Base IPI': float(item.find('.//nfe:imposto/nfe:IPI//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:IPI//nfe:vBC', ns) is not None else 0,
                'Aliq IPI': float(item.find('.//nfe:imposto/nfe:IPI//nfe:pIPI', ns).text) if item.find('.//nfe:imposto/nfe:IPI//nfe:pIPI', ns) is not None else 0,
                'Base PIS': float(item.find('.//nfe:imposto/nfe:PIS//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:PIS//nfe:vBC', ns) is not None else 0,
                'Aliq PIS': float(item.find('.//nfe:imposto/nfe:PIS//nfe:pPIS', ns).text) if item.find('.//nfe:imposto/nfe:PIS//nfe:pPIS', ns) is not None else 0,
                'Base COFINS': float(item.find('.//nfe:imposto/nfe:COFINS//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:COFINS//nfe:vBC', ns) is not None else 0,
                'Aliq COFINS': float(item.find('.//nfe:imposto/nfe:COFINS//nfe:pCOFINS', ns).text) if item.find('.//nfe:imposto/nfe:COFINS//nfe:pCOFINS', ns) is not None else 0,

                'Valor ICMS Total': float(vICMS.text) if vICMS is not None else 0,
                'Valor IPI Total': float(vIPI.text) if vIPI is not None else 0,
                'Valor PIS Total': float(vPIS.text) if vPIS is not None else 0,
                'Valor COFINS Total': float(vCOFINS.text) if vCOFINS is not None else 0,
            }
            
            linha_completa = {**dados_capa, **dados_item}
            lista_de_itens.append(linha_completa)
        
        return lista_de_itens

    except Exception as e:
        st.error(f"Erro ao processar o arquivo {nome_arquivo}: {e}")
        return []

# --- Geração de Relatórios (Sem Formatação) ---

def gerar_excel_para_cnpj(todos_os_itens, cnpj_empresa):
    """
    Gera um arquivo Excel em memória (BytesIO) para um CNPJ específico.
    Estrutura de abas corrigida e SEM formatação de fonte ou coluna.
    """
    
    output_excel = io.BytesIO()
    
    df_geral_itens = pd.DataFrame(todos_os_itens)
    df_geral_itens['Data Emissao'] = pd.to_datetime(df_geral_itens['Data Emissao'])
    df_geral_itens = df_geral_itens.sort_values(by=['Data Emissao', 'Numero NF']) 

    # --- DataFrames de ITENS (para Abas 5 e 6) ---
    df_saidas_detalhe = df_geral_itens[df_geral_itens['Tipo'] == 'Saída (Venda)'].copy()
    df_entradas_detalhe = df_geral_itens[df_geral_itens['Tipo'] == 'Entrada (Compra)'].copy()

    # --- DataFrames de RESUMO (para Abas 1 e 2) ---
    df_resumo_clientes = df_saidas_detalhe.groupby('Nome Destinatario').agg(
        Qtd_Linhas_Itens=('Produto', 'count'),
        Valor_Total_Vendido=('Valor Produto', 'sum')
    ).sort_values(by='Valor_Total_Vendido', ascending=False)
    
    df_resumo_fornecedores = df_entradas_detalhe.groupby('Nome Emitente').agg(
        Qtd_Linhas_Itens=('Produto', 'count'),
        Valor_Total_Comprado=('Valor Produto', 'sum'),
    ).sort_values(by='Valor_Total_Comprado', ascending=False)
    
    # --- DataFrames de NOTAS (para Abas 3 e 4) ---
    chave_nota = ['Numero NF', 'CNPJ Emitente', 'Data Emissao']
    
    agregacoes = {
        'Tipo': 'first',
        'Nome Emitente': 'first',
        'Nome Destinatario': 'first',
        'CNPJ Destinatario': 'first',
        'Valor Total da Nota': 'first', 
        
        'Valor Produto': 'sum',
        'Valor ICMS Total': 'sum',
        'Valor IPI Total': 'sum',
        'Valor PIS Total': 'sum',
        'Valor COFINS Total': 'sum'
    }

    df_geral_notas = df_geral_itens.groupby(chave_nota).agg(agregacoes).reset_index()
    df_geral_notas = df_geral_notas.sort_values(by='Data Emissao')
    
    df_saidas_notas = df_geral_notas[df_geral_notas['Tipo'] == 'Saída (Venda)'].copy()
    df_entradas_notas = df_geral_notas[df_geral_notas['Tipo'] == 'Entrada (Compra)'].copy()
    
    
    # --- Geração do Excel (Ordem das Abas Corrigida) ---
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        
        # Escreve os dados em cada aba
        df_resumo_clientes.to_excel(writer, sheet_name='1. Vendas por Cliente') 
        df_resumo_fornecedores.to_excel(writer, sheet_name='2. Compras por Fornecedor') 

        colunas_notas = [col for col in df_saidas_notas.columns if 'Creditavel' not in col]
        df_saidas_notas.to_excel(writer, sheet_name='3. Total Saídas (Notas)', index=False, columns=colunas_notas)
        
        colunas_notas_ent = [col for col in df_entradas_notas.columns if 'Creditavel' not in col]
        df_entradas_notas.to_excel(writer, sheet_name='4. Total Entradas (Notas)', index=False, columns=colunas_notas_ent)

        colunas_itens = [col for col in df_saidas_detalhe.columns if 'Creditavel' not in col]
        df_saidas_detalhe.to_excel(writer, sheet_name='5. Detalhe Saídas (Itens)', index=False, columns=colunas_itens)
        
        colunas_itens_ent = [col for col in df_entradas_detalhe.columns if 'Creditavel' not in col]
        df_entradas_detalhe.to_excel(writer, sheet_name='6. Detalhe Entradas (Itens)', index=False, columns=colunas_itens_ent)
    
        # *** NENHUMA FORMATAÇÃO É APLICADA ***

    output_excel.seek(0)
    return output_excel

def criar_zip_dos_relatorios(relatorios_excel):
    """Cria um arquivo ZIP em memória a partir de múltiplos relatórios Excel."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nome_arquivo, data_bytes in relatorios_excel.items():
            zip_file.writestr(nome_arquivo, data_bytes.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer

# --- Interface Principal do Streamlit ---

def main():
    
    st.set_page_config(layout="wide", page_title="Organizador Fiscal de XMLs")
    st.title("🚀 Organizador Fiscal de XMLs")
    st.markdown("Uma aplicação para processar lotes de XMLs, organizar por CNPJ e gerar relatórios em Excel.")

    # Define as abas da aplicação
    tab_processar, tab_config = st.tabs(["📄 Processar XMLs", "⚙️ Configurações"])

    # --- Aba de Configurações ---
    with tab_config:
        st.subheader("Gerenciar CNPJs da Empresa")
        st.markdown("Cadastre aqui todos os CNPJs (matriz e filiais) da sua empresa. Eles ficarão salvos no arquivo `cnpjs_config.json`.")
        
        cnpjs_atuais_lista = carregar_cnpjs()
        cnpjs_texto = st.text_area(
            "CNPJs (um por linha, apenas números)", 
            value="\n".join(cnpjs_atuais_lista),
            height=250
        )

        if st.button("Salvar CNPJs"):
            cnpjs_para_salvar = [cnpj.strip() for cnpj in cnpjs_texto.split('\n') if cnpj.strip()]
            salvar_cnpjs(cnpjs_para_salvar)
            st.success(f"{len(cnpjs_para_salvar)} CNPJs foram salvos com sucesso!")
            st.rerun() # Recarrega a página para atualizar a lista na outra aba

    # --- Aba de Processamento ---
    with tab_processar:
        
        # Carrega os CNPJs cadastrados
        meus_cnpjs_lista = carregar_cnpjs()
        if not meus_cnpjs_lista:
            st.warning("Atenção: Nenhum CNPJ cadastrado. Por favor, vá até a aba '⚙️ Configurações' para adicionar os CNPJs da sua empresa.")
            st.stop()
            
        st.info(f"CNPJs cadastrados para processamento: {', '.join(meus_cnpjs_lista)}")

        st.subheader("1. Carregar Arquivos XML")
        uploaded_files = st.file_uploader(
            "Selecione ou arraste para cá os arquivos XML da sua pasta",
            accept_multiple_files=True,
            type="xml"
        )

        st.subheader("2. Processar Dados")
        if st.button("Iniciar Processamento", type="primary", disabled=(not uploaded_files)):
            
            meus_cnpjs_set = set(meus_cnpjs_lista)
            dados_por_cnpj = {}
            
            progress_bar = st.progress(0, text="Iniciando...")
            total_xmls = len(uploaded_files)
            
            for i, file in enumerate(uploaded_files):
                progress_bar.progress((i + 1) / total_xmls, text=f"Processando: {file.name}")
                
                # Passa o objeto de arquivo e o nome
                lista_de_itens_da_nota = processar_xml(file, file.name) 

                if not lista_de_itens_da_nota:
                    continue
                
                item_exemplo = lista_de_itens_da_nota[0]
                cnpj_emit = item_exemplo['CNPJ Emitente']
                cnpj_dest = item_exemplo['CNPJ Destinatario']

                tipo_operacao = None
                cnpj_proprietario = None

                if cnpj_emit in meus_cnpjs_set:
                    tipo_operacao = 'Saída (Venda)'
                    cnpj_proprietario = cnpj_emit
                elif cnpj_dest in meus_cnpjs_set:
                    tipo_operacao = 'Entrada (Compra)'
                    cnpj_proprietario = cnpj_dest
                else:
                    continue 

                if cnpj_proprietario not in dados_por_cnpj:
                    dados_por_cnpj[cnpj_proprietario] = []
                
                for item in lista_de_itens_da_nota:
                    item['Tipo'] = tipo_operacao
                    dados_por_cnpj[cnpj_proprietario].append(item)

            progress_bar.empty()
            
            if not dados_por_cnpj:
                st.warning("Processamento concluído, mas nenhuma nota fiscal (Entrada ou Saída) corresponde aos CNPJs cadastrados.")
                st.stop()

            st.success(f"Processamento Concluído! Dados encontrados para {len(dados_por_cnpj)} CNPJ(s).")
            
            # --- Geração e Download dos Relatórios ---
            st.subheader("3. Baixar Relatórios")
            
            relatorios_em_memoria = {}
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with st.spinner("Gerando relatórios Excel..."):
                for cnpj_empresa, lista_itens_cnpj in dados_por_cnpj.items():
                    
                    df_cnpj_itens = pd.DataFrame(lista_itens_cnpj)
                    bytes_excel = gerar_excel_para_cnpj(df_cnpj_itens, cnpj_empresa)
                    
                    nome_arquivo_excel = f'Relatorio_Fiscal_CNPJ_{cnpj_empresa}_{timestamp}.xlsx'
                    relatorios_em_memoria[nome_arquivo_excel] = bytes_excel

            if len(relatorios_em_memoria) == 1:
                # Se for só um, baixa direto
                nome_arquivo = list(relatorios_em_memoria.keys())[0]
                dados_arquivo = list(relatorios_em_memoria.values())[0]
                
                st.download_button(
                    label=f"📥 Baixar Relatório para CNPJ {list(dados_por_cnpj.keys())[0]}",
                    data=dados_arquivo,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            elif len(relatorios_em_memoria) > 1:
                # Se for mais de um, cria o ZIP
                st.markdown(f"Relatórios gerados para {len(relatorios_em_memoria)} CNPJs. Baixe todos em um arquivo .zip.")
                
                zip_bytes = criar_zip_dos_relatorios(relatorios_em_memoria)
                nome_zip = f"Relatorios_Fiscais_{timestamp}.zip"
                
                st.download_button(
                    label=f"📥 Baixar todos os {len(relatorios_em_memoria)} relatórios (.zip)",
                    data=zip_bytes,
                    file_name=nome_zip,
                    mime="application/zip"
                )

# Ponto de entrada da aplicação
if __name__ == "__main__":
    main()