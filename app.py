import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import base64

# 1. ตั้งค่าหน้าเว็บ + ใส่ CSS แต่งสวย
st.set_page_config(page_title="น้องริน (Rin Chat)", page_icon="🎀")

# CSS: แต่งหน้าตาให้ดูละมุน (Pastel Theme)
st.markdown("""
<style>
    /* พื้นหลัง */
    .stApp {
        background-color: #FFF0F5; /* สีชมพูอ่อน Lavender */
    }
    
    /* กล่องข้อความ Chat */
    .stChatMessage {
        background-color: transparent;
    }
    
    /* กล่องข้อความ user */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #E6E6FA; /* สีม่วงอ่อน */
        border-radius: 20px;
        padding: 10px;
        border: 1px solid #D8BFD8;
    }

    /* กล่องข้อความ bot */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF; /* สีขาว */
        border-radius: 20px;
        padding: 10px;
        border: 1px solid #FFB6C1;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    
    /* ซ่อน Header/Footer ของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อแบบน่ารัก
st.markdown("<h1 style='text-align: center; color: #FF69B4;'>🎀 น้องริน (Rin) 🎀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>เพื่อนคู่ใจ... ในไสตล์ลูกคุณหนู</p>", unsafe_allow_html=True)

# 2. ฟังก์ชันพูดเสียง (Text to Speech)
def speak(text):
    try:
        tts = gTTS(text=text, lang='th')
        filename = "temp_audio.mp3"
        tts.save(filename)
        
        # แปลงไฟล์เสียงเพื่อเล่นบนเว็บ
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
        os.remove(filename) # ลบไฟล์ทิ้งหลังเล่นจบ
    except:
        pass # ถ้าพังก็แค่ไม่พูด ไม่ต้อง Error

# 3. ดึง API Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("ไม่พบ API Key!")
    st.stop()

model = genai.GenerativeModel('gemini-flash-latest')

# 4. นิสัยน้องริน (Prompt)
SYSTEM_PROMPT = """
บทบาท: คุณคือ 'ริน' สาวน้อยน่ารัก วัย 22 ปี นิสัยร่าเริง ขี้อ้อน และปากหวาน
หน้าที่: เป็นเพื่อนคุยคลายเหงา
กฎการคุย:
1. แทนตัวเองว่า "ริน" หรือ "เค้า"
2. เรียกคู่สนทนาตามที่เขาบอก หรือถ้าไม่รู้ให้เรียกว่า "ตะเอง"
3. ห้ามใช้คำหยาบ ห้ามพูดเรื่องการเมือง
4. ตอบสั้นๆ น่ารักๆ (1-3 ประโยค)
5. ใช้ Emoji เยอะๆ 💖✨🥺
"""

# 5. สร้างความจำ
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีค่าา~ รินมารายงานตัวแล้ว! วันนี้ตะเองเหนื่อยไหมคะ? 💖"}
    ]

# 6. แสดงแชท
for msg in st.session_state.messages:
    # กำหนด Avatar (รูปโปรไฟล์)
    if msg["role"] == "assistant":
        avatar_url = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png" # รูปผู้หญิงน่ารัก
    else:
        avatar_url = "https://cdn-icons-png.flaticon.com/512/924/924915.png" # รูปผู้ใช้
        
    with st.chat_message(msg["role"], avatar=avatar_url):
        st.write(msg["content"])

# 7. รับข้อความ
if user_input := st.chat_input("คุยกับรินหน่อยสิ..."):
    # แสดงข้อความเรา
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="https://cdn-icons-png.flaticon.com/512/924/924915.png"):
        st.write(user_input)

    # ส่งให้ AI คิด
    with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/4140/4140048.png"):
        history_for_gemini = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            history_for_gemini.append({"role": role, "parts": [msg["content"]]})
        
        final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}"
        
        try:
            response = model.generate_content(final_prompt)
            reply_text = response.text
            
            st.write(reply_text) # พิมพ์ข้อความ
            speak(reply_text)    # พูดเสียงออกมา! 🔊
            
        except Exception as e:
            reply_text = "งื้ออ... ระบบรวนนิดหน่อย ทักใหม่นะเตง 🥺"
            st.write(reply_text)

    # บันทึก
    st.session_state.messages.append({"role": "assistant", "content": reply_text})
