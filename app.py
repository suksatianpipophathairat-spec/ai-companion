import streamlit as st
import google.generativeai as genai

st.title("🕵️ เครื่องมือสืบหา AI")

# ดึงกุญแจ
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("ไม่พบกุญแจ API Key")
    st.stop()

# สั่งให้ AI รายงานตัว
if st.button("กดปุ่มเพื่อค้นหา AI ที่ใช้ได้"):
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        
        if models:
            st.success(f"✅ เย้! เจอโมเดลที่ใช้ได้ {len(models)} ตัว:")
            st.code("\n".join(models))
            st.info("ให้ก็อปปี้ชื่อหนึ่งในนี้ (เช่น models/gemini-pro) ไปใส่ในโค้ดบรรทัด model = ...")
        else:
            st.error("❌ เชื่อมต่อได้ แต่ไม่เจอโมเดลเลย (บัญชีอาจมีปัญหา)")
            
    except Exception as e:
        st.error(f"💥 เกิดข้อผิดพลาด: {e}")
