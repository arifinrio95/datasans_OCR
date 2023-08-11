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
        {"role": "user", "content": f"""Pertama, rapikan text dari hasil OCR saya yang berantakan agar terbaca dengan mudah dalam format poin-poin. Kedua, analisa data tersebut dengan basis keilmuan yang kuat dan ilmiah. Output OCR:  {ocr_output}."""}
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
    # st.write("Mengklasifikasi...")

    if st.button('Lakukan OCR'):
        # Tampilkan URL Saweria setelah OCR
        # st.markdown(
        #     """<iframe src="https://saweria.co/widgets/qr?streamKey=0069192f5795ea2a865affcdc39e6f51" 
        #         width="200" height="200" frameborder="0" scrolling="no"></iframe>""",
        #     unsafe_allow_html=True,
        # )
        # ocr_result = ocr_image(image)
        st.subheader("Hasil OCR:")
        # st.write(ocr_result)
        ocr_result_gpt = ocr_analyze(ocr_result)
        st.write(ocr_result_gpt)

        format_option = st.selectbox('Pilih format file keluaran:', ['docx', 'pdf'])
        # if st.button('Download Hasil'):
        #     output_path = save_file(ocr_result_gpt, format_option)
        #     href = f'<a href="file://{output_path}" download>Click here to download {format_option.upper()}</a>'
        #     st.markdown(href, unsafe_allow_html=True)
