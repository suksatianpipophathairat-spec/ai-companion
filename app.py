import streamlit as st
import google.generativeai as genai

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI Soulmate (Gemini)", page_icon="💖")
st.title("💖 พื้นที่ปลอดภัยของใจ (Gemini Edition)")

# 2. ดึงกุญแจลับ (API Key) มาใช้
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("ไม่พบ API Key! กรุณาตั้งค่า GOOGLE_API_KEY ใน secrets")
    st.stop()

# 3. กำหนดโมเดล (ใช้ Gemini 1.5 Flash รุ่นใหม่ เร็วและฟรี)
model = genai.GenerativeModel('gemini-1.5-flash')

# กำหนดนิสัย (System Prompt) - ใส่ตรงนี้
SYSTEM_PROMPT = """
บทบาท: คุณคือ 'ริน' เพื่อนสาวคนสนิทวัย 22 ปี
นิสัย: ขี้เล่น, เป็นกันเอง, ให้กำลังใจเก่ง, และกวนนิดๆ
กฎสำคัญ: ห้ามตอบยาวเหมือนเรียงความ ให้ตอบสั้นๆ เหมือนแชทไลน์ (1-3 ประโยค)
"""

# 4. สร้างความจำ (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # (Gemini API เก็บประวัติใน chat_session เอง แต่เราเก็บใน state เพื่อโชว์บนจอ)

# 5. แสดงบทสนทนาเก่าบนหน้าจอ
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. รับข้อความจากลูกค้า
if user_input := st.chat_input("พิมพ์ระบายความในใจ..."):
    # 6.1 แสดงข้อความลูกค้า
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 6.2 ส่งให้ Gemini คิด
    with st.chat_message("assistant"):
        # เตรียมประวัติการคุยส่งให้ Gemini (แปลง Format ให้ตรงกับ Google)
        history_for_gemini = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            history_for_gemini.append({"role": role, "parts": [msg["content"]]})
        
        # เพิ่ม System Prompt ไปในข้อความล่าสุด (เทคนิคบังคับนิสัย)
        final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}"
        
        # ยิงไปถาม AI
        response = model.generate_content(final_prompt, stream=True)
        
        # แสดงผลแบบพิมพ์ทีละคำ
        def stream_data():
            for chunk in response:
                yield chunk.text
        
        full_response = st.write_stream(stream_data)
    
    # 6.3 บันทึกคำตอบลงความจำ
    st.session_state.messages.append({"role": "assistant", "content": full_response})
