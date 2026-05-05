import streamlit as st
import yt_dlp
import os
import re

st.set_page_config(page_title="Downloader", layout="centered")

st.title("📥 YouTube Downloader")

# Estado
if "arquivo_bytes" not in st.session_state:
    st.session_state.arquivo_bytes = None
if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = None
if "historico" not in st.session_state:
    st.session_state.historico = []

def limpar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

url = st.text_input("Cole a URL do vídeo:")

if url:
    try:
        # Cache evita rerun bugado
        @st.cache_data(show_spinner=False)
        def get_info(u):
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                return ydl.extract_info(u, download=False)

        info = get_info(url)
        titulo = limpar_nome(info["title"])

        st.image(info["thumbnail"], width="stretch")
        st.subheader(info["title"])

        formatos = info.get("formats", [])
        resolucoes = sorted(
            list(set(f.get("height") for f in formatos if f.get("height"))),
            reverse=True
        )

        with st.form("form_download"):
            tipo = st.radio("Formato:", ["Vídeo", "Áudio"])
            qualidade = st.selectbox(
                "Qualidade:",
                [f"{r}p" for r in resolucoes] if tipo == "Vídeo" else ["Melhor"]
            )

            submit = st.form_submit_button("Baixar")

        if submit:
            pasta = "downloads"
            os.makedirs(pasta, exist_ok=True)

            with st.spinner("Baixando..."):
                if tipo == "Vídeo":
                    altura = int(qualidade.replace("p", ""))

                    ydl_opts = {
                        "format": f"best[height<={altura}]",
                        "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
                        "merge_output_format": "mp4"
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    caminho = os.path.join(pasta, f"{titulo}.mp4")

                else:
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
                    }

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
                "tipo": tipo,
                "qualidade": qualidade
            })

            st.success("Download concluído!")

    except Exception as e:
        st.error(f"Erro: {e}")

# Botão fixo
if st.session_state.arquivo_bytes:
    st.download_button(
        "📥 Baixar arquivo",
        data=st.session_state.arquivo_bytes,
        file_name=st.session_state.nome_arquivo
    )

# Histórico
st.divider()
st.subheader("📜 Histórico")

for item in reversed(st.session_state.historico):
    st.write(f"🎬 {item['titulo']}")
    st.write(f"{item['tipo']} | {item['qualidade']}")
    st.write("---")