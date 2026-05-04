import streamlit as st
import yt_dlp
import os
import re

st.title("📥 YouTube Downloader (yt-dlp)")

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

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 📊 Progresso
        def progress_hook(d):
            if d["status"] == "downloading":
                if "_percent_str" in d:
                    p = d["_percent_str"].replace("%", "").strip()
                    try:
                        progress = int(float(p))
                        progress_bar.progress(progress)
                        status_text.text(f"Baixando... {progress}%")
                    except:
                        pass

            elif d["status"] == "finished":
                progress_bar.progress(100)
                status_text.text("Download concluído!")

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
                    "progress_hooks": [progress_hook],
                    "merge_output_format": "mp4"
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                caminho = os.path.join(pasta, f"{titulo}.mp4")

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Vídeo",
                    "qualidade": escolha
                })

                st.success("Vídeo baixado!")

                # 📥 botão download (funciona no cloud)
                if os.path.exists(caminho):
                    with open(caminho, "rb") as f:
                        st.download_button(
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
                    "progress_hooks": [progress_hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                caminho = os.path.join(pasta, f"{titulo}.webm")

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Áudio",
                    "qualidade": "Melhor"
                })

                st.success("Áudio baixado!")

                if os.path.exists(caminho):
                    with open(caminho, "rb") as f:
                        st.download_button(
                            "📥 Baixar áudio",
                            data=f,
                            file_name=f"{titulo}.webm"
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