import streamlit as st
import google.generativeai as genai

# 1. Rêkxistina rûpelê (Page config)
st.set_page_config(page_title="Chatbotê Behdînî", page_icon="🦅", layout="centered")

# 2. Wergrtina API Key ji Streamlit Secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Bra, ji kerema xwe API Key ya xwe li nav Secrets ya Streamlit zêde bike!")
    st.stop()

# 3. Rênmayên Sîstemê (System Prompt) - Daku wek xelkê Dihokê û bi pîtên Aramî biaxivît
system_instruction = """
تۆ بۆتەکێ زیرەکی دەستکردی. پێدڤیە هەرتم ب زاراڤێ بەهدینی (وەکی خەلکێ دهۆکێ) و بتنێ ب پیتێن ئارامی (عەرەبی) بەرسڤا پرسیارێن بکارئینەری بدەی.
دڤێت ئاخڤتنا تە یا سروشتی بیت، پەیڤێن رەسەن یێن دەڤەرا بادینان بکاربینی و بەرسڤێن تە د هاریکار و جوان بن. چ جاران ب پیتێن لاتینی نەئاخڤە.
"""

# 4. Helbijartina Modêlê (Gemini 1.5 Pro) bo zîrekîyeka bihêz
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=system_instruction
)

# 5. Taybetmendiyên aliyekî (Sidebar)
with st.sidebar:
    st.title("⚙️ Taybetmendî")
    st.markdown("Ev bot bi taybetî hatiye dirustkirin ko bi Behdînî û pîtên ئارامی (Erebî) bersivê bidet.")
    if st.button("🗑️ Jêbirina Çatê (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Bota Behdînî ya Zîrek")
st.caption("Silav! Tu dşêy noke pirsa xwe li xwarê binvîsî...")

# 6. Kontrolkirina mێjûya axaftinê (Chat history)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Nîşandana namەyên berê
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Wergrtina pirsa bikarhênerî
if prompt := st.chat_input("Pirsa xwe ل ڤێرێ binvîse..."):
    # Zêdekirina pirsa te bo nav dîrokê
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Wergrtina bersivê ji Google AI
    with st.chat_message("assistant"):
        try:
            # Amadekirina dîroka çatê bo bîrhatina AI-yê
            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            
            # Wergirtina bersivê bşêweyê xelek (Stream)
            response = chat.send_message(prompt, stream=True)
            
            # Fanksiyonek bo nîşandana peyv bi peyv
            def stream_parser(res):
                for chunk in res:
                    if chunk.text:
                        yield chunk.text
                        
            full_response = st.write_stream(stream_parser(response))
            
        except Exception as e:
            st.error(f"Çewtiyek çêbû: {e}")
            full_response = None

    # Zêdekirina bersiva botî bo nav dîrokê (History)
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
