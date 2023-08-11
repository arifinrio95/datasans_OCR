import openai
import streamlit as st
from PIL import Image
import pytesseract
from docx import Document
from reportlab.pdfgen import canvas
import tempfile

openai.api_key = st.secrets['user_api']

def ocr_image(image):
    # Melakukan OCR pada gambar
    return pytesseract.image_to_string(image)

def ocr_analyze(ocr_output):
    messages = [
        {"role": "system", "content": "Aku akan menganalisis data kamu."},
        {"role": "user", "content": f"""Pertama, rapikan text dari hasil OCR saya yang berantakan agar terbaca dengan mudah. Kedua, analisa data tersebut dengan basis keilmuan yang kuat dan ilmiah. Output OCR:  {ocr_output}."""}
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
    # Menyimpan hasil dalam format yang diinginkan
    if output_format == 'docx':
        document = Document()
        document.add_paragraph(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as fp:
            document.save(fp.name)
            return fp.name
    elif output_format == 'pdf':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as fp:
            c = canvas.Canvas(fp.name)
            c.drawString(100, 750, text)
            c.save()
            return fp.name

st.title('Datasans OCR App')
uploaded_file = st.file_uploader("Pilih gambar untuk OCR", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Gambar yang Diunggah.', use_column_width=True)
    st.write("")
    # st.write("Mengklasifikasi...")

    if st.button('Lakukan OCR'):
        ocr_result = ocr_image(image)
        st.subheader("Hasil OCR:")
        # st.write(ocr_result)
        ocr_result_gpt = ocr_analyze(ocr_result)
        st.write(ocr_result_gpt)

        format_option = st.selectbox('Pilih format file keluaran:', ['docx', 'pdf'])
        if st.button('Download Hasil'):
            output_path = save_file(ocr_result_gpt, format_option)
            st.success(f'File siap diunduh dalam format {format_option}')
            st.download_button(label=f"Download {format_option.upper()}", file_path=output_path, file_name=f"output.{format_option}")
