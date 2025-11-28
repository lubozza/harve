import streamlit as st
import os
import shutil

# Diretório base onde as pastas serão gerenciadas
BASE_DIR = "pastas_usuarios"

# Garante que o diretório base exista
os.makedirs(BASE_DIR, exist_ok=True)

st.title("Gerenciador de Pastas via Browser")

# -------------------------
# Função para listar pastas
# -------------------------
def listar_pastas():
    return [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

# -------------------------
# Criar nova pasta
# -------------------------
st.header("Criar Nova Pasta")
nova_pasta = st.text_input("Nome da nova pasta")
if st.button("Criar Pasta"):
    caminho_novo = os.path.join(BASE_DIR, nova_pasta)
    if os.path.exists(caminho_novo):
        st.error("Pasta já existe!")
    elif nova_pasta.strip() == "":
        st.error("Digite um nome válido!")
    else:
        os.makedirs(caminho_novo)
        st.success(f"Pasta '{nova_pasta}' criada com sucesso!")

# -------------------------
# Selecionar pasta existente
# -------------------------
st.header("Gerenciar Pastas Existentes")
pastas = listar_pastas()
pasta_selecionada = st.selectbox("Selecione uma pasta", [""] + pastas)

if pasta_selecionada:
    st.write(f"Pasta selecionada: **{pasta_selecionada}**")
    
    # -------------------------
    # Renomear pasta
    # -------------------------
    novo_nome = st.text_input("Novo nome da pasta")
    if st.button("Renomear Pasta"):
        if novo_nome.strip() == "":
            st.error("Digite um nome válido!")
        else:
            caminho_antigo = os.path.join(BASE_DIR, pasta_selecionada)
            caminho_novo = os.path.join(BASE_DIR, novo_nome)
            if os.path.exists(caminho_novo):
                st.error("Já existe uma pasta com este nome!")
            else:
                os.rename(caminho_antigo, caminho_novo)
                st.success(f"Pasta renomeada para '{novo_nome}'")
                st.experimental_rerun()  # Atualiza a lista de pastas

    # -------------------------
    # Excluir pasta
    # -------------------------
    st.write("---")
    if st.button("Excluir Pasta"):
        caminho = os.path.join(BASE_DIR, pasta_selecionada)
        try:
            shutil.rmtree(caminho)
            st.success(f"Pasta '{pasta_selecionada}' excluída com sucesso!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Erro ao excluir pasta: {e}")

# -------------------------
# Listar pastas atuais
# -------------------------
st.header("Pastas Atuais")
pastas = listar_pastas()
if pastas:
    st.write(pastas)
else:
    st.write("Nenhuma pasta encontrada.")
