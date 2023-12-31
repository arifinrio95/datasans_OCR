import openai
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from docx import Document
from reportlab.pdfgen import canvas
import tempfile
import requests
from datetime import datetime, timedelta
import re

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style.css")

openai.api_key = st.secrets['user_api']

st.set_option('deprecation.showPyplotGlobalUse', False)
st.image('https://drive.google.com/uc?export=view&id=19pbADOQ5KjjzcB_Em8qqqe8YG_tYDRTs', use_column_width=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
def check_word_in_url(url, word="Berhasil"):
    try:
        if url == 'founder_pass':
            return True
            
        response = requests.get(url, headers = headers)
        response.raise_for_status()

        # Pengecekan kata "Berhasil"
        if word not in response.text:
            return False

        if "DatasansBook" not in response.text:
            return False
            
        # Pengecekan tanggal hari ini
        today_date = datetime.today().strftime('%d-%m-%Y')
        if today_date not in response.text:
            return False
        
        # Pengecekan waktu saat ini sampai 1 jam ke belakang dalam format 12 jam
        current_time = datetime.now()
        one_hour_before = current_time - timedelta(hours=1)
        time_range = [one_hour_before + timedelta(minutes=i) for i in range(61)]
        formatted_times = [time.strftime('%I:%M') for time in time_range]

        # Jika tidak ada waktu yang cocok dalam konten, kembalikan False
        if not any(time in response.text for time in formatted_times):
            return False

        # Pengecekan untuk string bernilai "Rp 1.000" atau lebih
        # rupiah_pattern = r'Rp\s?(\d{1,3}(\.\d{3})*|\d+)'
        # matches = re.findall(rupiah_pattern, response.text)
        # for match in matches:
        #     # Menghilangkan titik dan konversi ke integer
        #     value = int(match[0].replace("Rp", "").replace(".", "").strip())
        #     if value < 1000:
        #         return False
        # Jika semua pengecekan berhasil, kembalikan True
        return True

    except requests.RequestException as e:
        st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses.")
        return False


def ocr_image(image):
    # Melakukan OCR pada gambar
    return pytesseract.image_to_string(image)

def ocr_analyze(ocr_output, doc_type):
    messages = [
        {"role": "system", "content": "Aku akan menulis ulang text kamu dengan format yang baik."},
        # {"role": "user", "content": f"""Buat 2 bagian. Pertama, tuliskan text dari hasil OCR saya yang berantakan agar terbaca dengan mudah. Kedua, analisa data tersebut dengan basis keilmuan yang kuat dan ilmiah, serta berikan referensinya. Output OCR:  {ocr_output}."""}
        # {"role": "user", "content": f"""Ini adalah hasil OCR dari dokumen {doc_type}. Rapikan text dari hasil OCR yang berantakan ini agar terbaca dengan mudah dengan format yang rapi. Koreksi jika ada yang typo. Lalu berikan hasil analisamu sebagai notes. Text OCR:  {ocr_output}."""}
        {"role": "user", "content": f"""Ini adalah hasil OCR dari dokumen {doc_type}. Rapikan text-nya agar terstruktur dengan asumsi textnya berada dalam st.write, tidak usah ditulis lagi st.write nya karena nanti responmu akan saya running di dalam st.write secara manual. Berikan juga analisamu sebagai 'Notes dari SansGPT'. Text OCR:  {ocr_output}."""}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=4000,
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

st.title('Datasans OCR')
st.write("OCR atau Optical Character Recognition adalah teknologi yang memungkinkan konversi berbagai jenis dokumen, seperti dokumen yang dipindai, foto dokumen, atau bahkan teks yang ada dalam gambar, menjadi data yang dapat diedit, dicari, dan disimpan oleh sebuah komputer. Proses ini melibatkan pengidentifikasian dan ekstraksi teks dari gambar untuk mengubahnya menjadi data yang bisa dimanipulasi. Teknologi OCR bisa digunakan dalam aplikasi pengelolaan dokumen dan otomatisasi tugas.")
st.write("Pastikan foto/gambar yang diupload tidak blur dan terbaca dengan jelas dengan mata telajang.")
uploaded_file = st.file_uploader("Pilih gambar untuk OCR", type=["png", "jpg", "jpeg"])



if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Gambar yang Diunggah.', use_column_width=True)
    st.write("")
    # st.markdown(f"[Sawer dulu dengan mengeklik link ini.]({'https://lynk.id/datasans.book/s/KVnDnod'})")
    # st.markdown("""
    #     <style>
    #     .tooltip {
    #       position: relative;
    #       display: inline-block;
    #       cursor: pointer;
    #       background-color: #f2f2f2; /* Warna abu-abu */
    #       padding: 5px;
    #       border-radius: 6px;
    #     }
        
    #     .tooltip .tooltiptext {
    #       visibility: hidden;
    #       width: 300px;
    #       background-color: #555;
    #       color: #fff;
    #       text-align: center;
    #       border-radius: 6px;
    #       padding: 5px;
    #       position: absolute;
    #       z-index: 1;
    #       bottom: 125%; 
    #       left: 50%;
    #       margin-left: -150px;
    #       opacity: 0;
    #       transition: opacity 0.3s;
    #     }
        
    #     .tooltip:hover .tooltiptext {
    #       visibility: visible;
    #       opacity: 1;
    #     }
    #     </style>
        
    #     <div class="tooltip">Kenapa tidak gratis? (harus nyawer)
    #       <span class="tooltiptext">Proses cleansing hasil OCR menggunakan API ChatGPT yang aksesnya berbayar. Sawer seikhlasnya untuk melanjutkan. Link berlaku selama 1 jam setelah sawer berhasil.</span>
    #     </div>
    #     """, unsafe_allow_html=True)
    # url = st.text_input("Masukkan link bukti sawer untuk melanjutkan. Masukkan link lengkap mulai dari 'https://'")

    # if url and check_word_in_url(url)==False:
    #     st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses/valid.")
        
    # if check_word_in_url(url):
    with st.spinner('Memproses.'):
        # if st.button('Lakukan OCR'):
        ocr_result = ocr_image(image)
        st.subheader("Hasil OCR Original:")
        st.write(ocr_result)
        st.subheader("")

    st.subheader("Hasil OCR Rapi (powered by GPT4):")
    st.markdown(f"[Sawer dulu untuk mendapatkan passkey [klik disini].]({'https://lynk.id/datasans.book/s/KVnDnod'})")
    passkey = st.text_input("Masukkan passkey.")
    
    if passkey != '' and passkey!=st.secrets['passkey']:
        st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses/valid.")
    if passkey==st.secrets['passkey']:
        doc_type = st.text_input("Dokumen apa ini? (Informasi ini diperlukan agar saya lebih memahami konteks.)")
        if doc_type:
            with st.spinner('Memproses.'):
                
                ocr_result_gpt = ocr_analyze(ocr_result, doc_type)
                st.write(ocr_result_gpt)
    
            # format_option = st.selectbox('Pilih format file keluaran:', ['docx', 'pdf'])
    
    
