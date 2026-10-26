import streamlit as st
import os
from database import init_db, authenticate_user, save_document_meta, get_all_documents, delete_document_meta
from rag_engine import add_document_to_vector_db, remove_document_from_vector_db, query_relevant_context, generate_sample_chart
from google import genai

# Inisialisasi Database
init_db()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN & STYLING CSS ABSTRACT BACKGROUND
# ---------------------------------------------------------
st.set_page_config(
    page_title="BAPPEDA AI - Salatiga Management System",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS dengan Latar Belakang Pola Abstrak Adaptif (Light & Dark)
st.markdown("""
    <style>
    /* 1. Base Font & Layout */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        font-size: 16px;
    }

    /* 2. BACKGROUND ABSTRAK MODE LIGHT (Default & Light Theme) */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(249, 115, 22, 0.12) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(34, 197, 94, 0.12) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* 3. BACKGROUND ABSTRAK MODE DARK (Otomatis Aktif Saat Pakai Dark Theme) */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0f172a !important;
            background-image: 
                radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.25) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.2) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(249, 115, 22, 0.2) 0px, transparent 50%),
                radial-gradient(at 0% 100%, rgba(34, 197, 94, 0.2) 0px, transparent 50%) !important;
            background-attachment: fixed !important;
        }
    }

    /* 4. Header Berwarna Gradien Ceria + Logo Bappeda */
    .app-header {
        background: linear-gradient(135deg, #0284C7 0%, #EC4899 50%, #F97316 100%);
        border-radius: 20px;
        padding: 24px 30px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    .header-logo-img {
        width: 75px;
        height: auto;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.2));
    }
    .app-header-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        color: #FFFFFF;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .app-header-sub {
        font-size: 16px;
        color: #FEF08A;
        font-weight: 600;
        margin-top: 4px;
    }

    /* 5. Kartu Profil Sidebar dengan Glassmorphism Abstrak */
    .user-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid rgba(34, 197, 94, 0.4);
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    @media (prefers-color-scheme: dark) {
        .user-card {
            background: rgba(30, 41, 59, 0.7);
            border-color: rgba(34, 197, 94, 0.6);
            color: #f8fafc;
        }
    }
    .avatar-circle {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: linear-gradient(135deg, #F97316 0%, #EC4899 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: bold;
        margin: 0 auto 12px auto;
        box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
    }

    /* 6. Navigasi Tab Modern */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        border-radius: 14px;
        padding: 0px 24px;
        font-size: 16px;
        font-weight: 700;
        background-color: rgba(243, 244, 246, 0.7);
        backdrop-filter: blur(8px);
        color: #4B5563;
        border: 2px solid rgba(229, 231, 235, 0.5);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284C7 0%, #3B82F6 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.35);
    }

    /* 7. Tombol Responsive */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        font-size: 15px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ---------------------------------------------------------
# 2. HALAMAN LOGIN MODERN & ABSTRAK
# ---------------------------------------------------------
if not st.session_state.authenticated:
    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("""
            <div style="text-align: center; margin-top: 25px; margin-bottom: 20px;">
                <img src="https://media.licdn.com/dms/image/v2/D560BAQE0kx4hzSUlqg/company-logo_200_200/company-logo_200_200/0/1667441250712?e=2147483647&v=beta&t=qyNaBUhS342Qa4MuQocWcoNDRDcwnqnpNUevQ1rnh2s" width="100" style="margin-bottom: 15px;">
                <h1 style="color: #0284C7; font-weight: 800; font-size: 32px; margin: 0;">BAPPEDA KOTA SALATIGA</h1>
                <p style="color: #EC4899; font-weight: 700; font-size: 18px; margin-top: 5px;">Sistem Integrasi Dokumen & AI Ekbang</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h3 style='color: #F97316; font-weight: 700;'>🔑 Masuk ke Akun</h3>", unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("🚀 Masuk Sekarang", use_container_width=True)
            
            if submit:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_info = {"username": user[0], "role": user[1], "opd_name": user[2]}
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")


# ---------------------------------------------------------
# 3. HALAMAN UTAMA APLIKASI WEB
# ---------------------------------------------------------
else:
    user = st.session_state.user_info

    # Sidebar Kiri
    with st.sidebar:
        st.markdown(f"""
            <div class="user-card">
                <div class="avatar-circle">{user['username'][0].upper()}</div>
                <h3 style="margin: 0; font-weight: 800;">{user['username']}</h3>
                <p style="margin: 4px 0; font-size: 15px; color: #16A34A; font-weight: 700;">🏢 {user['opd_name']}</p>
                <span style="background: #FEF08A; color: #854D0E; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 800; display: inline-block; margin-top: 6px;">
                    ROLE: {user['role'].upper()}
                </span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color: #EAB308;'>🔑 Gemini API Key</h4>", unsafe_allow_html=True)
        api_key = st.text_input("API Key:", type="password", label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 Keluar Akun", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()

    # Header Atas Berlogo Bappeda Salatiga
    st.markdown(f"""
        <div class="app-header">
            <img src="https://media.licdn.com/dms/image/v2/D560BAQE0kx4hzSUlqg/company-logo_200_200/company-logo_200_200/0/1667441250712?e=2147483647&v=beta&t=qyNaBUhS342Qa4MuQocWcoNDRDcwnqnpNUevQ1rnh2s" class="header-logo-img">
            <div>
                <div class="app-header-title">BAPPEDA EKBANG AI SYSTEM</div>
                <div class="app-header-sub">Pemerintah Kota Salatiga — Integrasi Dokumen & Komunikasi OPD</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Navigasi Tab Utama
    tab1, tab2, tab3 = st.tabs(["💬 AI Assistant", "📁 Repository Dokumen", "📊 Grafik & Analisis"])

    # ---------------------------------------------------------
    # TAB 1: AI CHAT
    # ---------------------------------------------------------
    with tab1:
        st.markdown("<h3 style='color: #0284C7;'>🤖 Diskusi & Tanya Jawab Dokumen</h3>", unsafe_allow_html=True)
        
        if not api_key:
            st.warning("⚠️ Masukkan Gemini API Key di sidebar sebelah kiri untuk mulai bertanya.")
        else:
            client = genai.Client(api_key=api_key.strip())

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if user_query := st.chat_input("Tanyakan sesuatu (contoh: Analisis prospek dokumen yang diunggah)..."):
                st.session_state.messages.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)

                context = query_relevant_context(user_query, user['role'], user['opd_name'])

                prompt = f"""
Anda adalah Asisten AI Resmi Bappeda Kota Salatiga. Jawablah pertanyaan pengguna secara mendalam, jelas, dan profesional berdasarkan dokumen pendukung berikut.

KONTEKS DOKUMEN:
{context if context else "Tidak ada dokumen relevan ditemukan."}

PERTANYAAN PENGGUNA:
{user_query}
"""
                with st.chat_message("assistant"):
                    with st.spinner("AI sedang membaca perpustakaan dokumen..."):
                        try:
                            response = client.models.generate_content(
                                model="gemini-3.8-flash",
                                contents=prompt
                            )
                            answer = response.text
                            st.markdown(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.error(f"Gagal memanggil AI: {e}")

            if st.session_state.messages:
                st.markdown("---")
                st.markdown("<h4 style='color: #EC4899;'>🛠️ Tools Bagikan & Simpan Hasil AI</h4>", unsafe_allow_html=True)
                chat_text = "\n\n".join([f"[{m['role'].upper()}]:\n{m['content']}" for m in st.session_state.messages])
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.download_button("📥 Unduh Hasil Obrolan (.txt)", data=chat_text, file_name="Hasil_Chat_Bappeda.txt", use_container_width=True)
                with c2:
                    if st.button("🧹 Bersihkan Riwayat Chat", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()

    # ---------------------------------------------------------
    # TAB 2: REPOSITORY DOKUMEN
    # ---------------------------------------------------------
    with tab2:
        st.markdown("<h3 style='color: #16A34A;'>📁 Manajemen Berkas & Dokumen</h3>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Unggah dokumen (PDF, DOCX, XLSX, PPTX, TXT, JPG, PNG)",
            type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True
        )

        if st.button("💾 Simpan Dokumen Baru"):
            if uploaded_files:
                for file in uploaded_files:
                    save_path = os.path.join(UPLOAD_DIR, file.name)
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())

                    doc_id = save_document_meta(file.name, save_path, user['username'], user['opd_name'])
                    add_document_to_vector_db(doc_id, save_path, file.name, user['opd_name'])

                st.success("Berhasil diunggah dan disimpan di sistem!")
                st.rerun()

        st.markdown("---")
        st.markdown("<h4 style='color: #0284C7;'>📚 Daftar Dokumen Tersimpan</h4>", unsafe_allow_html=True)
        docs = get_all_documents(user['role'], user['opd_name'])
        if docs:
            for doc in docs:
                doc_id, filename, uploaded_by, opd_name, upload_date = doc
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                c1.write(f"📄 **{filename}**")
                c2.write(f"🏢 {opd_name}")
                c3.write(f"🕒 {upload_date}")
                if c4.button("🗑️ Hapus", key=f"del_{doc_id}"):
                    delete_document_meta(doc_id)
                    remove_document_from_vector_db(doc_id)
                    st.success("Dokumen dihapus.")
                    st.rerun()
        else:
            st.info("Belum ada dokumen yang diunggah.")

    # ---------------------------------------------------------
    # TAB 3: VISUALISASI GRAFIK
    # ---------------------------------------------------------
    with tab3:
        st.markdown("<h3 style='color: #F97316;'>📊 Visualisasi Data & Grafik Automatic</h3>", unsafe_allow_html=True)
        c_left, c_right = st.columns([1, 2])
        with c_left:
            chart_style = st.selectbox("Tipe Grafik:", ["Grafik Batang (Bar)", "Grafik Garis (Line)"])
            chart_title = st.text_input("Judul Grafik:", "Analisis Prospek Pembangunan Ekonomi Salatiga")
            btn_gen = st.button("✨ Hasilkan Grafik Analisis", use_container_width=True)

        with c_right:
            if btn_gen:
                selected_type = "line" if "Garis" in chart_style else "bar"
                fig = generate_sample_chart(chart_type=selected_type)
                fig.update_layout(title=chart_title)
                st.plotly_chart(fig, use_container_width=True)