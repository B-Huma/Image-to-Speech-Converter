import streamlit as st
from openai import OpenAI
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="Görselden Sese", page_icon="🖼️📝🎤", layout="wide")

st.title("🖼️📝🎤 Görselden Sese Dönüştürücü")
st.write("Bu uygulama, yüklediğiniz bir görüntüdeki metni algılar ve ardından bu metni sesli olarak okur.")

uploaded_file = st.file_uploader("Bir görüntü yükleyin (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    if uploaded_file:
        st.header("Yüklenen Görüntü")
        st.image(uploaded_file, width="content")

    if st.button("Metni Çıkar"):
        with st.spinner("Metin çıkarılıyor..."):

            image_bytes = uploaded_file.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Bu fotoğraftaki metni çıkar. Yorum yapma, sadece metni yaz."
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    }
                ]
            )

            extracted_text = response.output_text
            st.session_state["ocr_text"] = extracted_text

        st.success("Metin başarıyla çıkarıldı.")
        st.text_area("Çıkarılan Metin", extracted_text, height=300)

with col2:
    if "ocr_text" in st.session_state:
        voice_select = st.selectbox("Ses Seçin", options=["verse", "alloy", "bella", "dario", "fiona"])
        READING_STYLES = {
                "📘 Eğitici / Ders Anlatımı": """Metni sakin, net ve öğretici bir tonla oku.
            Önemli kavramları hafifçe vurgula.
            Cümleleri anlaşılır şekilde ayır.
            Hızlı veya aceleci okuma yapma.
            Dinleyenin rahatça takip edebilmesini sağla.
            """,

                "📖 Hikâye / Roman": """Metni sıcak, akıcı ve duygulu bir ses tonuyla oku.
            Anlama göre vurgu yap.
            Duygusal cümlelerde sesi yumuşat.
            Betimlemelerde biraz daha yavaş oku.
            Doğal nefes ve duraklamalar ekle.
            """,

                "📰 Haber / Makale": """Metni net, tarafsız ve profesyonel bir tonla oku.
            Bilgi veren cümleleri açık ve kararlı oku.
            Abartılı duygu kullanma.
            Paragraflar arasında kısa duraklamalar yap.
            """,

                "📄 Resmi / Akademik": """Metni ciddi, dengeli ve ölçülü bir tonla oku.
            Duygusal vurgulardan kaçın.
            Terimleri net ve anlaşılır şekilde telaffuz et.
            Cümle sonlarında belirgin duraklamalar yap.
            """,

                "👶 Çocuk Metni": """Metni neşeli, sıcak ve yumuşak bir sesle oku.
            Cümleleri yavaş ve anlaşılır kur.
            Vurguları biraz daha belirgin yap.
            Samimi ve eğlenceli bir ton kullan.
            """,

                "🎧 Sesli Kitap (Genel)": """Metni doğal, akıcı ve insan gibi oku.
            Noktalama işaretlerine göre duraklamalar yap.
            Virgüllerde kısa, paragraflarda daha uzun durakla.
            Monoton veya robotik bir ton kullanma.
            Sanki bir sesli kitap okuyormuş gibi oku.
            """,

                "🧠 OCR Metni (Tarafsız)": """Bu metin bir görselden çıkarılmıştır.
            Satır ve paragraf yapısını koru.
            Anlamsız karakterleri yumuşak geç.
            Okumayı sade, net ve akıcı tut.
            Yorum ekleme, sadece oku.
            """
            }
        style_select = st.selectbox("Okuma Stili Seçin", options=list(READING_STYLES.keys()))
        instructions = READING_STYLES[style_select]

        if st.button("Metni Sese Dönüştür"):
            with st.spinner("Metin sese dönüştürülüyor..."):
                text = st.session_state["ocr_text"]


                audio_response = client.audio.speech.create(
                    model="gpt-4o-mini-tts",
                    voice=voice_select,
                    input=text,
                    instructions= instructions
                )
                audio_bytes = audio_response.read()                

                st.success("Metin başarıyla sese dönüştürüldü.")
                st.audio(audio_bytes, format="audio/mp3")
