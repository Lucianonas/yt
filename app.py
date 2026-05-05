import streamlit as st
import yt_dlp
import os
import re

st.set_page_config(page_title="Downloader PRO", layout="centered")
st.title("📥 YouTube Downloader (PRO)")

# Estado
if "arquivo_bytes" not in st.session_state:
    st.session_state.arquivo_bytes = None
if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = None
if "historico" not in st.session_state:
    st.session_state.historico = []

def limpar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

# 🔥 Config base anti-403
def base_opts(pasta, titulo):
    return {
        "outtmpl": os.path.join(pasta, f"{titulo}.%(ext)s"),
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
    }

# 🧠 Função blindada
def baixar_blindado(url, pasta, titulo, altura=None, tipo="video"):
    tentativas = []

    if tipo == "video":
        tentativas = [
            # 🔥 melhor qualidade (precisa ffmpeg)
            {
                "format": f"bestvideo[height={altura}]+bestaudio/best",
                "merge_output_format": "mp4"
            },
            # ⚠️ médio
            {
                "format": f"best[height<={altura}]"
            },
            # 🛡️ fallback total
            {
                "format": "best"
            }
        ]
    else:
        tentativas = [
            {"format": "bestaudio/best"},
            {"format": "worstaudio"}
        ]

    for tentativa in tentativas:
        try:
            opts = base_opts(pasta, titulo)
            opts.update(tentativa)

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            return True  # sucesso

        except Exception as e:
            print("Tentativa falhou:", e)

    return False  # todas falharam


url = st.text_input("Cole a URL do vídeo:")

if url:
    try:
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

        with st.form("form"):
            tipo = st.radio("Formato:", ["Vídeo", "Áudio"])
            qualidade = st.selectbox(
                "Qualidade:",
                [f"{r}p" for r in resolucoes] if tipo == "Vídeo" else ["Melhor"]
            )
            enviar = st.form_submit_button("Baixar")

        if enviar:
            pasta = "downloads"
            os.makedirs(pasta, exist_ok=True)

            with st.spinner("Tentando baixar (modo blindado)..."):
                altura = int(qualidade.replace("p", "")) if tipo == "Vídeo" else None

                sucesso = baixar_blindado(
                    url,
                    pasta,
                    titulo,
                    altura,
                    tipo.lower()
                )

            if not sucesso:
                st.error("❌ Não foi possível baixar esse vídeo.")
            else:
                # detectar arquivo
                for ext in ["mp4", "webm", "m4a"]:
                    caminho = os.path.join(pasta, f"{titulo}.{ext}")
                    if os.path.exists(caminho):
                        with open(caminho, "rb") as f:
                            st.session_state.arquivo_bytes = f.read()
                            st.session_state.nome_arquivo = os.path.basename(caminho)
                        break

                st.session_state.historico.append({
                    "titulo": info["title"],
                    "tipo": tipo,
                    "qualidade": qualidade
                })

                st.success("Download concluído!")

    except Exception as e:
        st.error(f"Erro: {e}")

# botão fixo
if st.session_state.arquivo_bytes:
    st.download_button(
        "📥 Baixar arquivo",
        data=st.session_state.arquivo_bytes,
        file_name=st.session_state.nome_arquivo
    )

# histórico
st.divider()
st.subheader("📜 Histórico")

for item in reversed(st.session_state.historico):
    st.write(f"🎬 {item['titulo']}")
    st.write(f"{item['tipo']} | {item['qualidade']}")
    st.write("---")