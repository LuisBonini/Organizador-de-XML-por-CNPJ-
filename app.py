# app.py (Versão 3.4 - Sem XlsxWriter, usando Openpyxl)

import streamlit as st
import pandas as pd
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import io
import zipfile
import sys # Adicionado para a função get_config_path

# --- Funções de Configuração ---

def get_config_path(filename):
    """ Obtém o caminho correto para o config, seja .py ou .exe """
    if hasattr(sys, "_MEIPASS"):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))
        return os.path.join(base_dir, filename)
    else:
        return os.path.abspath(filename)

CONFIG_FILE = get_config_path("cnpjs_config.json")

def carregar_cnpjs():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get("cnpjs", [])
    except json.JSONDecodeError:
        return []

def salvar_cnpjs(cnpjs_list):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"cnpjs": cnpjs_list}, f, indent=2)

# --- Funções de Lógica Fiscal ---

def processar_xml_from_memory(uploaded_file, nome_arquivo):
    try:
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        tree = ET.parse(uploaded_file)
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
                'Valor ICMS': float(vICMS.text) if vICMS is not None else 0,
                'Base IPI': float(item.find('.//nfe:imposto/nfe:IPI//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:IPI//nfe:vBC', ns) is not None else 0,
                'Aliq IPI': float(item.find('.//nfe:imposto/nfe:IPI//nfe:pIPI', ns).text) if item.find('.//nfe:imposto/nfe:IPI//nfe:pIPI', ns) is not None else 0,
                'Valor IPI': float(vIPI.text) if vIPI is not None else 0,
                'Base PIS': float(item.find('.//nfe:imposto/nfe:PIS//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:PIS//nfe:vBC', ns) is not None else 0,
                'Aliq PIS': float(item.find('.//nfe:imposto/nfe:PIS//nfe:pPIS', ns).text) if item.find('.//nfe:imposto/nfe:PIS//nfe:pPIS', ns) is not None else 0,
                'Valor PIS': float(vPIS.text) if vPIS is not None else 0,
                'Base COFINS': float(item.find('.//nfe:imposto/nfe:COFINS//nfe:vBC', ns).text) if item.find('.//nfe:imposto/nfe:COFINS//nfe:vBC', ns) is not None else 0,
                'Aliq COFINS': float(item.find('.//nfe:imposto/nfe:COFINS//nfe:pCOFINS', ns).text) if item.find('.//nfe:imposto/nfe:COFINS//nfe:pCOFINS', ns) is not None else 0,
                'Valor COFINS': float(vCOFINS.text) if vCOFINS is not None else 0,
            }

            linha_completa = {**dados_capa, **dados_item}
            lista_de_itens.append(linha_completa)

        return lista_de_itens

    except Exception as e:
        st.error(f"Erro ao processar o arquivo '{nome_arquivo}': {e}")
        return []

# --- Função auto_ajustar_colunas REMOVIDA ---

def criar_excel_in_memory(dfs_para_salvar):
    """Cria o arquivo Excel em memória (sem formatação XlsxWriter)."""
    output = io.BytesIO()
    # Usa o motor padrão (openpyxl) ou especifica-o
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in dfs_para_salvar.items():
            tem_indice = nome_aba in ['1. Vendas por Cliente', '2. Compras por Fornecedor']
            # A formatação agora será padrão do Excel
            df.to_excel(writer, sheet_name=nome_aba, index=tem_indice)
            # A chamada para auto_ajustar_colunas foi removida
    return output.getvalue()

def criar_zip_in_memory(lista_relatorios):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nome_arquivo, data in lista_relatorios:
            zip_file.writestr(nome_arquivo, data)
    return zip_buffer.getvalue()

# --- A APLICAÇÃO STREAMLIT (Interface) ---

st.set_page_config(page_title="Organizador Fiscal", layout="wide", initial_sidebar_state="collapsed")
st.title("🚀 Organizador Fiscal de XMLs")

if 'cnpjs' not in st.session_state:
    st.session_state.cnpjs = carregar_cnpjs()

tab_processar, tab_config = st.tabs(["Processar XMLs", "⚙️ Configurar CNPJs"])

with tab_processar:
    st.header("1. Faça o Upload dos XMLs")

    if not st.session_state.cnpjs:
        st.error("Nenhum CNPJ cadastrado. Vá para a aba '⚙️ Configurar CNPJs'.")
    else:
        st.info(f"CNPJs monitorados: {', '.join(st.session_state.cnpjs)}")

        xml_files = st.file_uploader(
            "Arraste e solte seus arquivos XML aqui",
            type=["xml"],
            accept_multiple_files=True
        )

        st.header("2. Processe e Baixe os Relatórios")

        if st.button("Processar XMLs", type="primary", disabled=(not xml_files)):
            with st.spinner("Processando..."):
                meus_cnpjs_set = set(st.session_state.cnpjs)
                dados_por_cnpj = {}
                total_xmls = 0
                total_xmls_processados = 0
                total_itens_processados = 0

                for uploaded_file in xml_files:
                    total_xmls += 1
                    uploaded_file.seek(0)
                    lista_de_itens_da_nota = processar_xml_from_memory(uploaded_file, uploaded_file.name)

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

                    total_xmls_processados += 1
                    total_itens_processados += len(lista_de_itens_da_nota)

                    if cnpj_proprietario not in dados_por_cnpj:
                        dados_por_cnpj[cnpj_proprietario] = []

                    for item in lista_de_itens_da_nota:
                        item['Tipo'] = tipo_operacao
                        dados_por_cnpj[cnpj_proprietario].append(item)

                st.success(f"Processamento Concluído! {total_xmls_processados} de {total_xmls} XMLs relevantes continham {total_itens_processados} itens.")

                if not dados_por_cnpj:
                    st.warning("Nenhuma nota fiscal válida para os CNPJs informados foi encontrada.")
                    st.session_state.relatorios = []
                else:
                    relatorios_gerados = []
                    for cnpj_empresa, todos_os_itens in dados_por_cnpj.items():
                        df_geral_itens = pd.DataFrame(todos_os_itens)
                        df_geral_itens['Data Emissao'] = pd.to_datetime(df_geral_itens['Data Emissao'])
                        df_geral_itens = df_geral_itens.sort_values(by=['Data Emissao', 'Numero NF'])

                        df_saidas_detalhe = df_geral_itens[df_geral_itens['Tipo'] == 'Saída (Venda)'].copy()
                        df_entradas_detalhe = df_geral_itens[df_geral_itens['Tipo'] == 'Entrada (Compra)'].copy()

                        df_resumo_clientes = df_saidas_detalhe.groupby('Nome Destinatario').agg(
                            Qtd_Linhas_Itens=('Produto', 'count'),
                            Valor_Total_Vendido=('Valor Produto', 'sum')
                        ).sort_values(by='Valor_Total_Vendido', ascending=False)

                        df_resumo_fornecedores = df_entradas_detalhe.groupby('Nome Emitente').agg(
                            Qtd_Linhas_Itens=('Produto', 'count'),
                            Valor_Total_Comprado=('Valor Produto', 'sum'),
                        ).sort_values(by='Valor_Total_Comprado', ascending=False)

                        chave_nota = ['Numero NF', 'CNPJ Emitente', 'Data Emissao']
                        agregacoes = {
                            'Tipo': 'first', 'Nome Emitente': 'first', 'Nome Destinatario': 'first',
                            'CNPJ Destinatario': 'first', 'Valor Total da Nota': 'first',
                            'Valor Produto': 'sum', 'Valor ICMS': 'sum', 'Valor IPI': 'sum',
                            'Valor PIS': 'sum', 'Valor COFINS': 'sum'
                        }

                        df_geral_notas = df_geral_itens.groupby(chave_nota).agg(agregacoes).reset_index()
                        df_geral_notas = df_geral_notas.sort_values(by='Data Emissao')

                        df_saidas_notas = df_geral_notas[df_geral_notas['Tipo'] == 'Saída (Venda)'].copy()
                        df_entradas_notas = df_geral_notas[df_geral_notas['Tipo'] == 'Entrada (Compra)'].copy()

                        dfs_para_salvar = {
                            '1. Vendas por Cliente': df_resumo_clientes,
                            '2. Compras por Fornecedor': df_resumo_fornecedores,
                            '3. Total Saídas (Notas)': df_saidas_notas,
                            '4. Total Entradas (Notas)': df_entradas_notas,
                            '5. Detalhe Saídas (Itens)': df_saidas_detalhe,
                            '6. Detalhe Entradas (Itens)': df_entradas_detalhe,
                        }

                        excel_data = criar_excel_in_memory(dfs_para_salvar)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nome_arquivo_excel = f'Relatorio_Fiscal_CNPJ_{cnpj_empresa}_{timestamp}.xlsx'

                        relatorios_gerados.append((nome_arquivo_excel, excel_data))

                    st.session_state.relatorios = relatorios_gerados

        if 'relatorios' in st.session_state and st.session_state.relatorios:
            st.subheader("📥 Downloads Disponíveis")

            with st.container(border=True):
                num_relatorios = len(st.session_state.relatorios)

                if num_relatorios == 1:
                    nome_arquivo, data = st.session_state.relatorios[0]
                    st.download_button(
                        label=f"Baixar Relatório (CNPJ {nome_arquivo.split('_')[2]})",
                        data=data,
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.markdown(f"**{num_relatorios} relatórios** foram gerados (um por CNPJ).")
                    zip_data = criar_zip_in_memory(st.session_state.relatorios)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label=f"Baixar Todos ({num_relatorios}) os Relatórios (.zip)",
                        data=zip_data,
                        file_name=f"Relatorios_Fiscais_{timestamp}.zip",
                        mime="application/zip",
                        type="primary"
                    )
                    with st.expander("Ver arquivos incluídos no .zip"):
                        for nome, _ in st.session_state.relatorios:
                            st.caption(f"✓ {nome}")

with tab_config:
    st.header("Gerenciar CNPJs da Sua Empresa")
    st.info("Cadastre aqui todos os CNPJs que você considera como 'seus'.")

    with st.expander("Adicionar Novo CNPJ", expanded=True):
        novo_cnpj_input = st.text_input("Digite o CNPJ:", placeholder="Ex: 12345678000199", key="cnpj_input")
        if st.button("Adicionar CNPJ", key="add_cnpj_btn"):
            cnpj_limpo = novo_cnpj_input.strip().replace('.','').replace('/','').replace('-','')
            if cnpj_limpo and cnpj_limpo.isdigit() and len(cnpj_limpo) == 14:
                if cnpj_limpo not in st.session_state.cnpjs:
                    st.session_state.cnpjs.append(cnpj_limpo)
                    salvar_cnpjs(st.session_state.cnpjs)
                    st.success(f"CNPJ {cnpj_limpo} adicionado!")
                    st.rerun()
                else:
                    st.warning("CNPJ já cadastrado.")
            else:
                st.error("CNPJ inválido.")

    with st.expander("Remover CNPJs Cadastrados", expanded=True):
        if not st.session_state.cnpjs:
            st.warning("Nenhum CNPJ cadastrado.")
        else:
            with st.form("form_remocao"):
                cnpj_para_remover = st.selectbox("Selecione para remover:", st.session_state.cnpjs)
                submitted = st.form_submit_button("Remover CNPJ Selecionado")
                if submitted:
                    st.session_state.cnpjs.remove(cnpj_para_remover)
                    salvar_cnpjs(st.session_state.cnpjs)
                    st.success(f"CNPJ {cnpj_para_remover} removido.")
                    st.rerun()