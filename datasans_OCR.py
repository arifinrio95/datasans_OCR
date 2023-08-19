import openai
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from docx import Document
from reportlab.pdfgen import canvas
import tempfile
import requests
from datetime import datetime, timedelta

# Tambahkan 15 menit ke waktu sekarang
expired_time = datetime.now() + timedelta(minutes=15)

# Endpoint URL
url = "https://bigflip.id/api/v2/pwf/bill"

# Otentikasi
auth = (st.secrets['flip_payment'], "")

# Data yang akan dikirim
data = {
    "title": "Kopi Angkringan",
    "amount": "2000",
    "type": "SINGLE",
    "expired_date": expired_time.strftime('%Y-%m-%d %H:%M:%S'),
    "is_address_required": "0",
    "is_phone_number_required": "0",
    "sender_name": "Testing User",
    "sender_email": "testing@gmail.com",
    "sender_phone_number": "08111109749",
    "sender_address": "Testing Testing Testing",
    "sender_bank": "qris",
    "sender_bank_type": "wallet_account"
}

# Header yang diperlukan
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth[0]}:"
}

# Alamat endpoint
url = "https://bigflip.id/api/v2/pwf/bill"

# Melakukan request POST dengan header yang diperlukan
# response = requests.post(url, data=data, headers=headers)
response = requests.post(url, data=data, auth=auth)

# Mendapatkan responsenya
response_content = response.json()

# payment_url = response_content['payment_url']

st.write(response_content)  # Cetak untuk debugging
if 'payment_url' in response_content:
    payment_url = response_content['payment_url']
else:
    st.write("Payment URL not found in the response.")


# Menampilkan di Streamlit
st.title("Payment URL")
iframe_code = f'<iframe src="{payment_url}" width="100%" height="600"></iframe>'
st.components.v1.html(iframe_code, height=600)

# Payment Done

openai.api_key = st.secrets['user_api']

st.set_option('deprecation.showPyplotGlobalUse', False)
st.image('https://drive.google.com/uc?export=view&id=1dWu3kImQ11Q-M2JgLtVz9Dng0MD5S4LK', use_column_width=True)


# def ocr_image(image):
#     # Ubah ke grayscale
#     image = image.convert('L')

#     # Terapkan filter untuk menghilangkan noise
#     image = image.filter(ImageFilter.MedianFilter())

#     # Tingkatkan kontras
#     enhancer = ImageEnhance.Contrast(image)
#     image = enhancer.enhance(2)

#     # Terapkan threshold untuk memperjelas teks
#     # image = image.point(lambda p: 0 if p < 200 else 255)

#     # Jalankan OCR pada gambar yang sudah diolah
#     text = pytesseract.image_to_string(image)

#     return text


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
    # st.write("Mengklasifikasi...")

    if st.button('Lakukan OCR'):
        # Tampilkan URL Saweria setelah OCR
        # st.markdown(
        #     """<iframe src="https://saweria.co/widgets/qr?streamKey=0069192f5795ea2a865affcdc39e6f51" 
        #         width="200" height="200" frameborder="0" scrolling="no"></iframe>""",
        #     unsafe_allow_html=True,
        # )
        ocr_result = ocr_image(image)
        st.subheader("Hasil OCR Original:")
        st.write(ocr_result)
        st.subheader("")
        st.subheader("Hasil OCR Rapi:")
        ocr_result_gpt = ocr_analyze(ocr_result)
        st.write(ocr_result_gpt)

        format_option = st.selectbox('Pilih format file keluaran:', ['docx', 'pdf'])
        # if st.button('Download Hasil'):
        #     output_path = save_file(ocr_result_gpt, format_option)
        #     href = f'<a href="file://{output_path}" download>Click here to download {format_option.upper()}</a>'
        #     st.markdown(href, unsafe_allow_html=True)
