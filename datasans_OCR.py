import openai
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from docx import Document
from reportlab.pdfgen import canvas
import tempfile
import requests

openai.api_key = st.secrets['user_api']

st.set_option('deprecation.showPyplotGlobalUse', False)
st.image('https://drive.google.com/uc?export=view&id=1dWu3kImQ11Q-M2JgLtVz9Dng0MD5S4LK', use_column_width=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
def check_word_in_url(url, word="Berhasil"):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Akan menghasilkan exception jika terjadi kesalahan (misal: 404 error)

        if word in response.text:
            return True
        else:
            return False
    except requests.RequestException as e:
        st.write(f"Terjadi kesalahan saat mengakses URL: {e}")
        return False


def ocr_image(image):
    # Melakukan OCR pada gambar
    return pytesseract.image_to_string(image)

def ocr_analyze(ocr_output):
    messages = [
        {"role": "system", "content": "Aku akan menulis ulang text kamu dengan format yang baik."},
        # {"role": "user", "content": f"""Buat 2 bagian. Pertama, tuliskan text dari hasil OCR saya yang berantakan agar terbaca dengan mudah. Kedua, analisa data tersebut dengan basis keilmuan yang kuat dan ilmiah, serta berikan referensinya. Output OCR:  {ocr_output}."""}
        {"role": "user", "content": f"""Rapikan text dari hasil OCR saya yang berantakan agar terbaca dengan mudah dengan format yang baik. Text OCR:  {ocr_output}."""}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        max_tokens=10000,
        temperature=0
    )
    script = response.choices[0].message['content']

    return script
    
def save_file(text, output_format='docx'):
    # Membuat nama file yang unik
    unique_filename = str(uuid.uuid4())
    if output_format == 'docx':
        file_path = os.path.join(os.getcwd(), f"{unique_filename}.docx")
        document = Document()
        document.add_paragraph(text)
        document.save(file_path)
    elif output_format == 'pdf':
        file_path = os.path.join(os.getcwd(), f"{unique_filename}.pdf")
        c = canvas.Canvas(file_path)
        c.drawString(100, 750, text)
        c.save()
    return file_path

st.title('Datasans OCR App')
st.write("Pastikan foto/gambar tidak blur dan terbaca dengan jelas dengan mata telajang.")
uploaded_file = st.file_uploader("Pilih gambar untuk OCR", type=["png", "jpg", "jpeg"])


if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Gambar yang Diunggah.', use_column_width=True)
    st.write("")
    st.markdown(f"[Sawer seikhlasnya dengan mengeklik link ini.]({'https://saweria.co/DatasansBook'})")
    url = st.text_input("Masukkan link bukti sawer untuk melanjutkan.")
   
    if check_word_in_url(url):
        with st.spinner('Wait for it...'):
            # if st.button('Lakukan OCR'):
            ocr_result = ocr_image(image)
            st.subheader("Hasil OCR Original:")
            st.write(ocr_result)
            st.subheader("")
            st.subheader("Hasil OCR Seteleh dirapikan secara otomatis:")
            ocr_result_gpt = ocr_analyze(ocr_result)
            st.write(ocr_result_gpt)
    
            # format_option = st.selectbox('Pilih format file keluaran:', ['docx', 'pdf'])
    
    
