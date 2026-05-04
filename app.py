import streamlit as st
import yt_dlp
import os
import re

st.title("📥 YouTube Downloader")

# 📜 Estado
if "historico" not in st.session_state:
    st.session_state.historico = []

if "arquivo_bytes" not in st.session_state:
    st.session_state.arquivo_bytes = None

if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = None

# 🧹 Limpar nome
def limpar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

url = st.text_input("Cole a URL do vídeo:")

if url:
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        titulo = limpar_nome(info["title"])

        st.image(info["thumbnail"], width="stretch")
        st.subheader(info["title"])

        opcao = st.radio("Formato:", ["Vídeo", "Áudio"])

        pasta = "downloads"
        os.makedirs(pasta, exist_ok=True)

        # ========================
        # 🎬 VÍDEO
        # ========================
        if opcao == "Vídeo":
            formatos = info.get("formats", [])

            resolucoes = sorted(
                list(set(f.get("height") for f in formatos if f.get("height"))),
                reverse=True
            )

            escolha = st.selectbox("Qualidade:", [f"{r}p" for r in resolucoes])

            if st.button("Baixar vídeo"):
                altura = int(escolha.replace("p", ""))

                ydl_opts = {
                    "format": f"bestvideo[height={altura}]+bestaudio/best",
                    "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
                    "merge_output_format": "mp4"
                }

                with st.spinner("Baixando..."):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                caminho = os.path.join(pasta, f"{titulo}.mp4")

                if os.path.exists(caminho):
                    with open(caminho, "rb") as f:
                        st.session_state.arquivo_bytes = f.read()
                        st.session_state.nome_arquivo = f"{titulo}.mp4"

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Vídeo",
                    "qualidade": escolha
                })

                st.success("Vídeo pronto!")

        # ========================
        # 🎧 ÁUDIO
        # ========================
        elif opcao == "Áudio":
            if st.button("Baixar áudio"):
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
                }

                with st.spinner("Baixando..."):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                caminho_webm = os.path.join(pasta, f"{titulo}.webm")
                caminho_m4a = os.path.join(pasta, f"{titulo}.m4a")

                caminho = caminho_webm if os.path.exists(caminho_webm) else caminho_m4a

                if os.path.exists(caminho):
                    with open(caminho, "rb") as f:
                        st.session_state.arquivo_bytes = f.read()
                        st.session_state.nome_arquivo = os.path.basename(caminho)

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Áudio",
                    "qualidade": "Melhor"
                })

                st.success("Áudio pronto!")

    except Exception as e:
        st.error(f"Erro: {e}")

# ========================
# 📥 BOTÃO FIXO (SEM BUG)
# ========================
if st.session_state.arquivo_bytes:
    st.download_button(
        "📥 Baixar arquivo",
        data=st.session_state.arquivo_bytes,
        file_name=st.session_state.nome_arquivo
    )

# ========================
# 📜 HISTÓRICO
# ========================
st.divider()
st.subheader("📜 Histórico")

if st.session_state.historico:
    for item in reversed(st.session_state.historico):
        st.write(f"🎬 {item['titulo']}")
        st.write(f"{item['tipo']} | {item['qualidade']}")
        st.write("---")
else:
    st.info("Nenhum download ainda.")