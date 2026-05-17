import streamlit as st
import yfinance as yf
import base64
import os

# 셰프의 비주얼 설정
st.set_page_config(page_title="Investment Kitchen", layout="centered")

st.title("👨‍🍳 투자 주방: 오늘의 나스닥")

# 오디오 자동 재생을 위한 헬퍼 함수
def autoplay_audio(filepath: str):
    if not os.path.exists(filepath):
        st.warning(f"소리 파일이 없습니다: {filepath}")
        return
        
    with open(filepath, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# 데이터 가져오기 (재료 수급)
with st.spinner("오늘의 재료(나스닥) 상태를 확인 중입니다..."):
    try:
        data = yf.Ticker("^IXIC").history(period="1d")
        current_price = data['Close'].iloc[-1]
        open_price = data['Open'].iloc[-1]
        change = ((current_price - open_price) / open_price) * 100
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric("나스닥 (IXIC) 현재가", f"{current_price:,.2f}", f"{change:.2f}%")

        # CSS로 전체 배경색을 변경하기 위한 헬퍼 함수
        def set_bg_color(hex_color):
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-color: {hex_color} !important;
                    transition: background-color 1.5s ease;
                }}
                /* 텍스트 가독성을 위해 일부 글자색 조정 */
                h1, .stMetricValue {{
                    text-shadow: 1px 1px 4px rgba(0,0,0,0.2);
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

        # 음향 및 비주얼 로직 (플레이팅)
        if change > 0.5:
            st.balloons() # 시각적 효과
            st.success(f"🔥 현재 화력 강함! (+{change:.2f}%)")
            set_bg_color("#FFD700") # 황금색
            autoplay_audio("assets/sizzle.mp3")
            
        elif change < -0.5:
            st.error(f"🌧️ 재료값이 저렴해졌습니다! ({change:.2f}%)")
            set_bg_color("#000080") # 네이비 블루
            autoplay_audio("assets/rain.mp3")
            
        else:
            st.info(f"🍵 간이 딱 맞습니다. 보합세 ({change:.2f}%)")
            set_bg_color("#50C878") # 에메랄드 그린
            
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")

st.markdown("---")
st.markdown("*(안내: 브라우저 정책상 화면을 새로고침하거나 클릭해야 오디오가 재생될 수 있습니다. 실제 소리를 들으시려면 `assets` 폴더 내에 진짜 mp3 파일을 넣어주세요!)*")
