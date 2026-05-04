import streamlit as st
import yt_dlp
import os
import platform

st.title("📥 YouTube Downloader (yt-dlp)")

# 📜 Histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

url = st.text_input("Cole a URL do vídeo:")

if url:
    try:
        # 🔎 Pega informações do vídeo
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        st.image(info["thumbnail"], width="stretch")
        st.subheader(info["title"])

        opcao = st.radio("Escolha o formato:", ["Vídeo", "Áudio"])

        pasta = "downloads"
        os.makedirs(pasta, exist_ok=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 📊 Hook de progresso
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

            # filtrar resoluções com vídeo
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
                    "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
                    "progress_hooks": [progress_hook],
                    "merge_output_format": "mp4"
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Vídeo",
                    "qualidade": escolha
                })

                st.success("Vídeo baixado!")

        # ========================
        # 🎧 ÁUDIO
        # ========================
        elif opcao == "Áudio":
            if st.button("Baixar áudio"):
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
                    "progress_hooks": [progress_hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": "Áudio",
                    "qualidade": "Melhor"
                })

                st.success("Áudio baixado!")

    except Exception as e:
        st.error(f"Erro: {e}")

# ========================
# 📂 ABRIR PASTA
# ========================
st.divider()

if st.button("📂 Abrir pasta de downloads"):
    try:
        if platform.system() == "Windows":
            os.startfile("downloads")
        elif platform.system() == "Darwin":
            os.system("open downloads")
        else:
            os.system("xdg-open downloads")
    except:
        st.error("Não foi possível abrir a pasta.")

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