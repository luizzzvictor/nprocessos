import re
import docx2txt
import PyPDF2
import streamlit as st

# Função para autenticação simples
def autenticar():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Login"):
            if usuario == "umf" and senha == "umfers":
                st.session_state["autenticado"] = True
                
                st.rerun()  # Recarrega o aplicativo
            else:
                st.error("Usuário ou senha incorretos.")
    


# Função para extrair texto de PDFs por página
def extrair_texto_pdf(arquivo_pdf):
    leitor = PyPDF2.PdfReader(arquivo_pdf)
    texto_por_pagina = []
    for num_pagina, pagina in enumerate(leitor.pages, start=1):
        texto = pagina.extract_text()
        texto_por_pagina.append((num_pagina, texto))
    return texto_por_pagina


# Função para extrair texto de DOCX
def extrair_texto_docx(arquivo_docx):
    texto = docx2txt.process(arquivo_docx)
    return texto


# Função para buscar padrões no texto
def buscar_padroes(texto):
    padrao = r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b|\b\d{20}\b"
    resultados = re.findall(padrao, texto)
    resultados_unicos = set(resultados)  # Obter valores únicos
    return resultados_unicos


def main():
    st.title("UMFtools")

    autenticar()

    if st.session_state.get("autenticado"):
        # Cria a aba "N.Processos"
        tab_n_processos, = st.tabs(["N.Processos"])

        with tab_n_processos:
            arquivos = st.file_uploader(
                "Faça upload de PDFs ou DOCXs",
                type=["pdf", "docx"],
                accept_multiple_files=True,
            )

            if arquivos:
                for arquivo in arquivos:
                    st.subheader(f"Resultados para {arquivo.name}")
                    if arquivo.type == "application/pdf":
                        texto_por_pagina = extrair_texto_pdf(arquivo)
                        numeros_encontrados = {}
                        for num_pagina, texto in texto_por_pagina:
                            resultados = buscar_padroes(texto)
                            for numero in resultados:
                                if numero not in numeros_encontrados:
                                    numeros_encontrados[numero] = []
                                numeros_encontrados[numero].append(num_pagina)
                        if numeros_encontrados:
                            st.write("Numerações únicas encontradas:")
                            for numero, paginas in numeros_encontrados.items():
                                paginas_unicas = sorted(set(paginas))
                                paginas_str = ", ".join(map(str, paginas_unicas))
                                st.write(f"- {numero} (Página(s): {paginas_str})")
                        else:
                            st.write("Nenhuma numeração única encontrada.")
                    elif (
                        arquivo.type
                        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ):
                        texto = extrair_texto_docx(arquivo)
                        resultados = buscar_padroes(texto)
                        if resultados:
                            st.write("Numerações encontradas:")
                            for resultado in resultados:
                                st.write(f"- {resultado}")
                        else:
                            st.write("Nenhuma numeração encontrada.")
                    else:
                        st.error("Tipo de arquivo não suportado.")
                        continue
    else:
        st.warning("Por favor, faça o login para continuar.")


if __name__ == "__main__":
    main()
