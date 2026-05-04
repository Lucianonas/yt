import streamlit as st
from pytubefix import YouTube
import os
import platform

st.title("📥 YouTube Downloader")

# 📜 Histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

url = st.text_input("Cole a URL do vídeo:")

if url:
    try:
        yt = YouTube(url)

        # 🖼️ Thumbnail
        st.image(yt.thumbnail_url, width="stretch")

        st.subheader(yt.title)

        opcao = st.radio("Escolha o formato:", ["Vídeo", "Áudio"])

        progress_bar = st.progress(0)
        status_text = st.empty()

        pasta = "downloads"

        # 📁 Garante que a pasta existe
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        # 📊 Callback progresso
        def progress_callback(stream, chunk, bytes_remaining):
            total_size = stream.filesize or stream.filesize_approx
            if total_size:
                bytes_downloaded = total_size - bytes_remaining
                progress = int(bytes_downloaded / total_size * 100)

                progress_bar.progress(progress)
                status_text.text(f"Baixando... {progress}%")

        yt.register_on_progress_callback(progress_callback)

        # ========================
        # 🎬 VÍDEO
        # ========================
        if opcao == "Vídeo":
            streams = yt.streams.filter(progressive=True, file_extension="mp4")\
                                .order_by("resolution")\
                                .desc()

            opcoes = [stream.resolution for stream in streams]
            escolha = st.selectbox("Qualidade:", opcoes)

            stream = streams[opcoes.index(escolha)]

            # 📦 Tamanho
            tamanho = stream.filesize or stream.filesize_approx
            if tamanho:
                tamanho_mb = tamanho / (1024 * 1024)
                st.info(f"Tamanho: {tamanho_mb:.2f} MB")
            else:
                st.warning("Tamanho não disponível")

            if st.button("Baixar vídeo"):
                arquivo = stream.download(output_path=pasta)

                progress_bar.progress(100)
                status_text.text("Download concluído!")

                st.session_state.historico.append({
                    "titulo": yt.title,
                    "tipo": "Vídeo",
                    "qualidade": escolha,
                    "arquivo": arquivo
                })

                st.success("Vídeo baixado!")

        # ========================
        # 🎧 ÁUDIO
        # ========================
        elif opcao == "Áudio":
            stream = yt.streams.filter(only_audio=True)\
                               .order_by("abr")\
                               .desc()\
                               .first()

            tamanho = stream.filesize or stream.filesize_approx
            if tamanho:
                tamanho_mb = tamanho / (1024 * 1024)
                st.info(f"Tamanho: {tamanho_mb:.2f} MB")
            else:
                st.warning("Tamanho não disponível")

            if st.button("Baixar áudio"):
                arquivo = stream.download(output_path=pasta)

                progress_bar.progress(100)
                status_text.text("Download concluído!")

                st.session_state.historico.append({
                    "titulo": yt.title,
                    "tipo": "Áudio",
                    "qualidade": stream.abr,
                    "arquivo": arquivo
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
        st.write(f"Arquivo: {item['arquivo']}")
        st.write("---")
else:
    st.info("Nenhum download ainda.")