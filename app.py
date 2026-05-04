import streamlit as st
import yt_dlp
import os
import re

st.title("📥 YouTube Downloader")

# 📜 Histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

# 🧹 Limpar nome de arquivo
def limpar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

url = st.text_input("Cole a URL do vídeo:")

if url:
    try:
        # 🔎 Info do vídeo
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        titulo = limpar_nome(info["title"])

        st.image(info["thumbnail"], width="stretch")
        st.subheader(info["title"])

        opcao = st.radio("Escolha o formato:", ["Vídeo", "Áudio"])

        pasta = "downloads"
        os.makedirs(pasta, exist_ok=True)

        download_area = st.empty()

        # ========================
        # 🎬 VÍDEO
        # ========================
        if opcao == "Vídeo":
            formatos = info.get("formats", [])

            resolucoes = sorted(
                list(set(f.get("height") for f in formatos if f.get("height"))),
                reverse=True
            )

            resolucoes_str = [f"{r}p" for r in resolucoes]
            escolha = st.selectbox("Qualidade:", resolucoes_str)

            if st.button("Baixar vídeo"):
                altura = int(escolha.replace("p", ""))

                ydl_opts = {
                    "format": f"bestvideo[height={altura}]+bestaudio/best",
                    "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
                    "merge_output_format": "mp4"
                }

                with st.spinner("Baixando vídeo..."):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                caminho = os.path.join(pasta, f"{titulo}.mp4")

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Vídeo",
                    "qualidade": escolha
                })

                st.success("Vídeo pronto!")

                if os.path.exists(caminho):
                    with open(caminho, "rb") as f:
                        download_area.download_button(
                            "📥 Baixar arquivo",
                            data=f,
                            file_name=f"{titulo}.mp4"
                        )

        # ========================
        # 🎧 ÁUDIO
        # ========================
        elif opcao == "Áudio":
            if st.button("Baixar áudio"):
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
                }

                with st.spinner("Baixando áudio..."):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                # tenta extensões comuns
                caminho_webm = os.path.join(pasta, f"{titulo}.webm")
                caminho_m4a = os.path.join(pasta, f"{titulo}.m4a")

                caminho = caminho_webm if os.path.exists(caminho_webm) else caminho_m4a

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Áudio",
                    "qualidade": "Melhor"
                })

                st.success("Áudio pronto!")

                if os.path.exists(caminho):
                    with open(caminho, "rb") as f:
                        download_area.download_button(
                            "📥 Baixar áudio",
                            data=f,
                            file_name=os.path.basename(caminho)
                        )

    except Exception as e:
        st.error(f"Erro: {e}")

# ========================
# 📜 HISTÓRICO
# ========================
st.divider()
st.subheader("📜 Histórico de downloads")

if st.session_state.historico:
    for item in reversed(st.session_state.historico):
        st.write(f"🎬 {item['titulo']}")
        st.write(f"Tipo: {item['tipo']} | Qualidade: {item['qualidade']}")
        st.write("---")
else:
    st.info("Nenhum download ainda.")