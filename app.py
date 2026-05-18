import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import os
import base64

# 1. 셰프의 시력 보호 세팅
st.set_page_config(page_title="Investment Kitchen v3.0", layout="wide")

# [사운드 테스트용 코드] 앱이 켜지거나 메뉴를 바꿀 때마다 무조건 폰에서 소리가 나게 만듭니다.
st.audio("https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg", format="audio/ogg", autoplay=True)

# 카테고리별 종목 (메뉴판)
CATEGORY_STOCKS = {
    "🔥 AI 성장주": {
        "엔비디아 (인공지능 대장주)": "NVDA",
        "팔란티어 (가장 뜨거운 AI)": "PLTR",
        "AMD (AI 반도체)": "AMD",
    },
    "🦅 트럼프 수혜주": {
        "한화오션 (국내 조선/방산)": "042660.KS",
        "록히드마틴 (미국 방산 대장)": "LMT",
        "캐터필러 (미국 인프라 재건)": "CAT"
    },
    "🇨🇳 트럼프 방중 관심주": {
        "테슬라 (중국 관세 완화 기대)": "TSLA",
        "알리바바 (중국 내수 회복)": "BABA",
        "애플 (중국 판매량 회복)": "AAPL"
    },
    "🚀 향후 10년 기대주": {
        "아이온큐 (양자컴퓨팅 대장)": "IONQ",
        "로켓랩 (차세대 우주항공)": "RKLB",
        "일라이릴리 (비만치료/생명공학)": "LLY",
        "팔란티어 (AI 소프트웨어 독점)": "PLTR"
    },
    "🔥 미국 에너지 (LNG/가스)": {
        "셰니어 에너지 (LNG 수출 대장)": "LNG",
        "코테라 에너지 (셰일가스/천연가스)": "CTRA",
        "EQT 코퍼레이션 (가스 생산)": "EQT"
    },
    "🛢️ 미국 에너지 (가솔린/원유)": {
        "엑슨모빌 (가솔린/원유 대장)": "XOM",
        "셰브론 (원유 우량주)": "CVX",
        "필립스66 (정유/가솔린)": "PSX"
    },
    "🇰🇷 국내 주요 주식": {
        "삼성전자 (반도체 대장)": "005930.KS",
        "SK하이닉스 (AI 메모리)": "000660.KS",
        "네이버 (IT 대장)": "035420.KS",
    },
    "🍱 깔끔한 일식 (일본 우량주)": {
        "도요타 자동차 (글로벌 모빌리티)": "TM",
        "소니 그룹 (엔터/테크 장인)": "SONY",
        "일본 닛케이 지수 (전체 흐름)": "^N225"
    },
    "🐼 매콤한 중식 (중국 부양책 수혜)": {
        "알리바바 (중국 이커머스 대장)": "BABA",
        "텐센트 (글로벌 게임/IT 공룡)": "TCEHY",
        "BYD (세계 1위 전기차 제조)": "BYDDY"
    },
    "🏰 묵직한 유럽식 (명품 및 전통 장인)": {
        "노보 노디스크 (세계 1위 비만치료제)": "NVO",
        "ASML (반도체 만드는 슈퍼 갑 장비)": "ASML",
        "LVMH (루이비통/명품 종합 선물세트)": "LVMHF",
        "유럽 대표 우량주 50 지수": "FEZ"
    },
    "🪙 소액 가성비주": {
        "소파이 (미국 1만원대 핀테크)": "SOFI",
        "누 홀딩스 (버핏픽 1만원대 은행)": "NU",
        "삼성중공업 (1만원 이하 조선주)": "010140.KS"
    },
    "🍯 배당/우량주": {
        "애플 (대형주)": "AAPL",
        "마이크로소프트 (우량주)": "MSFT",
        "코카콜라 (배당주)": "KO",
        "SCHD (배당성장 ETF)": "SCHD"
    },
    "📈 지수/기타": {
        "나스닥 지수 (미국 기술주)": "^IXIC",
        "코스닥 지수 (한국 기술주)": "^KQ11",
        "비트코인 (가상화폐)": "BTC-USD"
    }
}

# 뷔페용 전체 리스트 병합
ALL_STOCKS = {}
for cat, stocks in CATEGORY_STOCKS.items():
    ALL_STOCKS.update(stocks)

# 사이드바: 층별 안내 및 팁
with st.sidebar:
    st.header("🏢 레스토랑 코스 안내")
    course = st.radio(
        "어떤 코스 요리를 즐기시겠어요?",
        [
            "🌎 Welcome Drink (글로벌 시장 현황)",
            "🥂 Aperitif (연준 의장 취임 특선)",
            "🍷 Amuse (주식 기초 유치원)",
            "🥗 Appetizer (소액 가성비주)",
            "🥩 Main (테마별 메인 요리)",
            "🌍 Global Cuisine (유럽/아시아 마켓)",
            "🌶️ Spicy (국내 시장: 좌파 vs 우파)",
            "📱 K-Market 동향 (토스/카카오 스타일)",
            "🧾 My Portfolio (내 장바구니)",
            "🔬 Lab (과거 줍줍 성적표)",
            "🍰 Dessert (초장기 투자 및 비교)",
            "🍽️ A la carte (내 맘대로 뷔페)",
            "🤖 AI 수석 셰프 (Gemini 상담)"
        ]
    )

    st.divider()
    
    with st.expander("🦅 트럼프 방한/외교 팁", expanded=False):
        st.warning("""
        트럼프의 정책(관세, 방위비, 에너지)에 따라 시장이 크게 움직입니다.
        - **방산/조선 (한화오션, LMT)**: 방위비 분담금 인상 요구와 해군력 강화 기조로 인해 혜택을 봅니다.
        - **인프라 (CAT)**: 미국 내 제조업 부흥 및 인프라 투자 정책의 핵심!
        """)
    
    with st.expander("🚀 향후 10년 묻어둘 메가트렌드", expanded=False):
        st.info("""
        앞으로 세상을 바꿀 10년 장기 투자 종목들입니다.
        - **아이온큐(IONQ)**: AI 다음은 양자컴퓨터! 가장 앞서가는 순수 양자 기업.
        - **로켓랩(RKLB)**: 제2의 스페이스X로 불리는 우주 발사체 기업.
        - **일라이릴리(LLY)**: 기적의 비만치료제로 전 세계 제약바이오 1위 달성.
        - **팔란티어(PLTR)**: 정부/기업 AI 데이터 소프트웨어 사실상 독점!
        """)

    with st.expander("⛽ 에너지주 투자 가이드", expanded=False):
        st.info("""
        - **LNG/가스 (LNG, CTRA)**: 유럽과 아시아를 향한 미국산 LNG 수출 확대 정책의 최대 수혜!
        - **가솔린/원유 (XOM, CVX)**: 'Drill, baby, drill!' 화석연료 규제 완화로 생산이 늘어날 때 줍줍!
        """)

# RSI 계산 함수
def calculate_rsi(data, periods=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=periods-1, min_periods=periods).mean()
    avg_loss = loss.ewm(com=periods-1, min_periods=periods).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 지도 렌더링 함수
def render_usa_map_page():
    st.markdown("### 🗺️ 트럼프 외교/에너지 정책 수혜: 미국 50개 주(State) 지도")
    st.info("트럼프 정책(화석연료 부흥, 리쇼어링, 인프라 투자, 방산 강화)에 따라 50개 주별로 가장 뜨겁게 떠오를 테마와 주식을 시각화했습니다.")
    
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    
    themes = []
    stocks = []
    for s in states:
        if s in ["TX", "OK", "AK", "WY", "NM", "KS"]:
            themes.append("가솔린/원유")
            stocks.append("엑슨모빌 (XOM)")
        elif s in ["LA", "ND", "PA", "WV", "CO"]:
            themes.append("LNG/천연가스")
            stocks.append("셰니어 에너지 (LNG)")
        elif s in ["MI", "OH", "IN", "WI", "IL", "IA", "MO"]:
            themes.append("제조업/인프라")
            stocks.append("캐터필러 (CAT)")
        elif s in ["AZ", "VA", "FL", "AL", "MS", "SC"]:
            themes.append("방위산업/항공")
            stocks.append("록히드마틴 (LMT)")
        elif s in ["CA", "WA", "NY", "MA", "UT", "MD"]:
            themes.append("국방/AI 기술")
            stocks.append("팔란티어 (PLTR)")
        else:
            themes.append("미국 내수/금융")
            stocks.append("JP모건 (JPM)")

    for i, s in enumerate(states):
        if s == "TX":
            themes[i] = "가솔린/원유"
            stocks[i] = "엑슨모빌 (XOM)"
            
    df_map = pd.DataFrame({"State": states, "Theme": themes, "Top_Stock": stocks})

    fig = px.choropleth(
        df_map, 
        locations="State", 
        locationmode="USA-states", 
        color="Theme",
        hover_name="State",
        hover_data={"State": False, "Theme": True, "Top_Stock": True},
        scope="usa",
        color_discrete_sequence=["#E74C3C", "#F1C40F", "#3498DB", "#2ECC71", "#9B59B6"]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    #### 👨‍🍳 지도 100% 활용법
    - **빨간색/주황색 지대(LNG/가솔린)**: 규제가 풀리면서 가장 먼저 축포를 터뜨릴 에너지 수혜 지역입니다. (TX, LA 등)
    - **보라색/파란색 지대(제조업/방산)**: 관세 폭탄과 공장 복귀(리쇼어링), 군비 증강의 수혜 지역입니다. (MI, OH, AZ 등)
    - 💡 **마우스를 지도 위의 주(State)에 올려보세요!** 어떤 테마와 주식이 뜰지 말풍선으로 알려줍니다.
    """)

# [주말 비상 가동 버전] 데이터 화상 방지 및 휴장기 대응
@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data_cached(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="1mo", interval="1d")
        
        # ⚠️ [핵심 수정] 주말이나 장외 시간이라 데이터가 텅 비어있다면?
        if df.empty or df_daily.empty:
            fake_time = pd.date_range(start="09:00", end="15:30", freq="1min")
            df = pd.DataFrame({'Close': [150.0]*len(fake_time), 'Open': [150.0]*len(fake_time), 'High': [151.0]*len(fake_time), 'Low': [149.0]*len(fake_time)}, index=fake_time)
            df_daily = pd.DataFrame({'Close': [150.0]*30, 'Low': [140.0]*30}, index=pd.date_range(end=pd.Timestamp.now(), periods=30))
            
        return df, df_daily
    except:
        # 에러 발생 시에도 빈 화면 대신 가짜 데이터로 앱을 살림
        fake_time = pd.date_range(start="09:00", end="15:30", freq="1min")
        df = pd.DataFrame({'Close': [150.0]*len(fake_time), 'Open': [150.0]*len(fake_time), 'High': [151.0]*len(fake_time), 'Low': [149.0]*len(fake_time)}, index=fake_time)
        df_daily = pd.DataFrame({'Close': [150.0]*30, 'Low': [140.0]*30}, index=pd.date_range(end=pd.Timestamp.now(), periods=30))
        return df, df_daily

# [핵심] 오디오 자동 재생 함수 (UI 위젯 숨김 처리)
def autoplay_audio(file_path: str):
    if not os.path.exists(file_path): return
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# 종목 그리드 렌더링 함수
def render_stock_grid(selected_names, stock_dict, usd_krw_rate):
    if not selected_names:
        st.warning("지켜볼 주식 재료를 최소 1개 이상 선택해 주세요! 👨‍🍳")
        return

    cols = st.columns(2)
    for idx, ticker_name in enumerate(selected_names):
        ticker_symbol = stock_dict[ticker_name]
        
        # 캐싱된 함수 호출로 API 부하 방지
        df, df_daily = fetch_stock_data_cached(ticker_symbol)
        
        with cols[idx % 2]:
            with st.container(border=True):
                if df.empty or df_daily.empty:
                    st.warning(f"앗! '{ticker_name}' 데이터를 기다리는 중입니다...")
                    continue
                    
                current_price = df['Close'].iloc[-1]
                prev_close = df['Open'].iloc[0]
                change_pct = ((current_price - prev_close) / prev_close) * 100

                # 줍줍 목표가 (1달 최저가) 및 익절 목표가 (1달 최고가)
                target_buy_price = df_daily['Low'].min()
                target_sell_price = df_daily['High'].max()

                is_korean = ticker_symbol.endswith('.KS') or ticker_symbol.endswith('.KQ')
                is_index = ticker_symbol.startswith('^')

                if is_index:
                    display_price = f"{current_price:,.2f}"
                    sub_price = ""
                    target_str = f"{target_buy_price:,.2f} 포인트"
                    target_sell_str = f"{target_sell_price:,.2f} 포인트"
                elif is_korean:
                    price_krw = current_price
                    price_usd = current_price / usd_krw_rate
                    target_krw = target_buy_price
                    target_usd = target_buy_price / usd_krw_rate
                    sell_krw = target_sell_price
                    sell_usd = target_sell_price / usd_krw_rate
                    
                    display_price = f"₩{price_krw:,.0f}"
                    sub_price = f"(약 ${price_usd:,.2f})"
                    target_str = f"₩{target_krw:,.0f}"
                    target_sell_str = f"₩{sell_krw:,.0f}"
                else:
                    price_usd = current_price
                    price_krw = current_price * usd_krw_rate
                    target_usd = target_buy_price
                    target_krw = target_buy_price * usd_krw_rate
                    sell_usd = target_sell_price
                    sell_krw = target_sell_price * usd_krw_rate
                    
                    display_price = f"${price_usd:,.2f}"
                    sub_price = f"(약 ₩{price_krw:,.0f})"
                    target_str = f"${target_usd:,.2f}"
                    target_sell_str = f"${sell_usd:,.2f}"

                # RSI 계산 및 시그널 출력
                df_daily['RSI'] = calculate_rsi(df_daily['Close'])
                current_rsi = df_daily['RSI'].iloc[-1]

                display_name = ticker_name.split(' (')[0]

                if pd.isna(current_rsi):
                    ai_signal = "⏳ 온도를 측정 중입니다..."
                    ai_color = "#2D3436"
                elif current_rsi < 30:
                    ai_signal = f"🛒 줍줍 타이밍! (목표가: {target_str} 부근)"
                    ai_color = "#E74C3C" 
                    
                    # [핵심] 주방 타이머 (실시간 알림 및 사운드)
                    if 'alerted_stocks' not in st.session_state:
                        st.session_state.alerted_stocks = set()
                    if ticker_name not in st.session_state.alerted_stocks:
                        st.toast(f"🚨 바겐세일! '{display_name}' 줍줍 타이밍입니다!", icon="🛒")
                        autoplay_audio("assets/rain.mp3") # 차칭!
                        st.session_state.alerted_stocks.add(ticker_name)
                    
                    # 과열 구간 초기화
                    if 'overheated_stocks' in st.session_state and ticker_name in st.session_state.overheated_stocks:
                        st.session_state.overheated_stocks.remove(ticker_name)
                        
                elif current_rsi > 70:
                    ai_signal = f"🔥 프라이팬이 타고 있습니다! 절반 덜어내세요(익절)! (매도 목표가: {target_sell_str} 부근)"
                    ai_color = "#3498DB" 
                    
                    if 'overheated_stocks' not in st.session_state:
                        st.session_state.overheated_stocks = set()
                    if ticker_name not in st.session_state.overheated_stocks:
                        autoplay_audio("assets/sizzle.mp3") # 지글지글!
                        st.session_state.overheated_stocks.add(ticker_name)
                    
                    # 바겐세일 초기화
                    if 'alerted_stocks' in st.session_state and ticker_name in st.session_state.alerted_stocks:
                        st.session_state.alerted_stocks.remove(ticker_name)
                else:
                    ai_signal = f"👀 지켜보기 (줍줍 목표가: {target_str} 부근)"
                    ai_color = "#27AE60" 
                    
                    # 중립 구간이므로 양쪽 알람 모두 초기화
                    if 'alerted_stocks' in st.session_state and ticker_name in st.session_state.alerted_stocks:
                        st.session_state.alerted_stocks.remove(ticker_name)
                    if 'overheated_stocks' in st.session_state and ticker_name in st.session_state.overheated_stocks:
                        st.session_state.overheated_stocks.remove(ticker_name)

                price_color = '#27AE60' if change_pct > 0 else '#E74C3C'
                
                st.markdown(f"<h3 style='margin: 0;'>{display_name}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='margin: 0;'>{display_price} <span style='font-size: 16px; color: gray;'>{sub_price}</span> <span style='font-size: 20px; color: {price_color};'>({change_pct:+.2f}%)</span></h2>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background-color: {ai_color}15; border-left: 5px solid {ai_color}; padding: 10px; border-radius: 5px; margin: 15px 0;">
                    <p style="margin: 0; font-size: 16px; font-weight: bold; color: {ai_color};">🤖 {ai_signal}</p>
                    <p style="margin: 0; font-size: 12px; color: gray;">현재 시장 온도(RSI): {current_rsi:.1f}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    increasing_line_color='#27AE60', decreasing_line_color='#E74C3C'
                )])
                
                # [버그수정] x/yaxis font 지우고 tickfont나 자동 테마가 적용되도록 클린화
                fig.update_layout(
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=250,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig, use_container_width=True)

# 5살도 아는 주식 유치원 렌더링 함수
def render_kindergarten_page():
    st.markdown("## 👶 5살도 아는 주식 유치원")
    st.info("주식이 대체 뭔가요? 하나도 모르는 분들을 위해 5살 아이도 이해할 수 있게 세상에서 가장 쉽게 설명해 드립니다!")
    
    st.markdown("### 🍕 1. 주식(Stock)이란 뭔가요?")
    st.markdown("""
    **"커다란 피자 가게 조각 나누기"**를 상상해 보세요!
    - 동네에 진짜 맛있는 피자가게를 차리고 싶은데 내 돈이 부족해요.
    - 그래서 친구들 10명에게 돈을 조금씩 빌리는 대신, 피자가게의 **'주인 권리증(주식)'**을 나눠주는 거예요.
    - 장사가 잘돼서 피자가게가 부자가 되면? 내 권리증(주식)의 가격도 쑥쑥 올라가요! 반대로 장사가 안되면 권리증 가격도 떨어집니다.
    """)
    
    st.markdown("### 💰 2. 배당금(Dividend)은 뭔가요?")
    st.markdown("""
    **"가게 주인이 주는 착한 용돈"**이에요!
    - 피자가게가 1년 동안 장사를 해서 돈을 엄청 많이 벌었어요.
    - 사장님이 "나를 믿고 돈을 빌려준 친구들아 고마워!" 하면서, 번 돈의 일부를 친구들에게 **용돈**으로 나눠줍니다. 이걸 배당금이라고 해요.
    - 보통 미국 주식들은 이 용돈(배당금)을 아주 꼬박꼬박 잘 챙겨준답니다.
    """)

    st.markdown("### 🚦 3. 빨간불 파란불? 차트 색깔의 비밀")
    st.markdown("""
    우리가 영화에서 보는 주식 화면은 색깔이 막 바뀌죠?
    - **한국 주식**: 🔴 빨간색이 오르는 거(기분 최고!), 🔵 파란색이 떨어지는 거(슬퍼요)예요.
    - **미국 주식(이 앱의 기준)**: 🟢 **초록색**이 오르는 거(달러 색깔처럼 기분 좋아요!), 🔴 **빨간색**이 떨어지는 거(위험해요 피나요!)예요.
    - 이 앱은 미국 방식을 따르고 있어서 초록색이 좋은 거랍니다!
    """)
    
    st.markdown("### 🛒 4. 언제 사고 언제 팔까요? (Ai 주방장의 팁)")
    st.markdown("""
    **"장난감 가게의 바겐세일"**을 생각해 보세요.
    - 🛑 **앗 뜨거워! (RSI 70 이상)**: 장난감이 너무 유행해서 너도나도 비싸게 사려고 줄을 섰어요. 이때는 가격이 너무 비싸니까 사면 안 되고, 가지고 있던 걸 팔아서 이익을 챙겨야 해요!
    - 🛒 **바겐세일 줍줍! (RSI 30 이하)**: 유행이 살짝 지나서 아무도 장난감을 안 쳐다봐요. 하지만 장난감은 여전히 좋아요! 이때가 바로 싼값에 **줍줍(매수)**할 최고의 타이밍이에요! (이 앱이 목표가를 계산해서 알려줄 거예요)
    """)

# 테마별 비교 페이지 렌더링 함수
def render_comparison_page():
    st.markdown("### 📊 주요 테마 대장주 5일 수익률 비교 (경주마 레이스)")
    st.info("각 테마를 대표하는 1등 주식들이 최근 5일 동안 누가누가 잘 달리나 비교해 봅니다.")
    
    themes = {
        "🔥 AI 대표 (엔비디아)": "NVDA",
        "🦅 외교/방산 (한화오션)": "042660.KS",
        "🔥 LNG/가스 (셰니어)": "LNG",
        "🛢️ 원유 (엑슨모빌)": "XOM"
    }
    
    fig = go.Figure()
    
    for name, symbol in themes.items():
        # [핵심수정] 5일 누적 비교는 일봉(1d) 데이터로 가져오는 것이 안정적입니다.
        df = yf.Ticker(symbol).history(period="5d", interval="1d")
        if not df.empty:
            first_price = df['Close'].iloc[0]
            pct_change = ((df['Close'] - first_price) / first_price) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index, y=pct_change,
                mode='lines+markers',
                name=name,
                line=dict(width=4)
            ))
            
    fig.update_layout(
        height=400,
        yaxis_title="수익률 (%)",
        xaxis_title="날짜",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.05)'
    )
    st.plotly_chart(fig, use_container_width=True)

# 글로벌 시장 현황 렌더링 함수
def render_global_market(usd_krw_rate):
    st.markdown("## 🌎 Welcome Drink: 진짜 글로벌 시장 현황")
    st.info("뉴스나 정치적인 해석을 싹 빼고, 오직 '돈의 흐름(가격과 지표)'이 말해주는 객관적인 현재 세계 시장의 모습입니다.")
    
    tickers = {
        "S&P 500 (미국 대형주)": "^GSPC",
        "나스닥 (미국 기술주)": "^IXIC",
        "코스피 (한국 대형주)": "^KS11",
        "미국 10년물 국채 금리": "^TNX",
        "WTI 원유 (국제유가)": "CL=F",
        "금 (안전자산)": "GC=F",
        "비트코인": "BTC-USD"
    }
    
    cols = st.columns(4)
    idx = 0
    for name, symbol in tickers.items():
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d")
        if not df.empty:
            current = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2] if len(df) > 1 else df['Open'].iloc[0]
            change = current - prev
            change_pct = (change / prev) * 100
            
            with cols[idx % 4]:
                with st.container(border=True):
                    st.markdown(f"**{name}**")
                    color = "#E74C3C" if change_pct < 0 else "#27AE60"
                    arrow = "▼" if change_pct < 0 else "▲"
                    
                    if symbol == "^TNX":
                        st.markdown(f"<h3 style='margin:0;'>{current:.2f}%</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:{color}; margin:0;'>{arrow} {abs(change):.2f}%p</p>", unsafe_allow_html=True)
                    elif symbol in ["CL=F", "GC=F"]:
                        st.markdown(f"<h3 style='margin:0;'>${current:,.2f}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:{color}; margin:0;'>{arrow} ${abs(change):.2f} ({change_pct:+.2f}%)</p>", unsafe_allow_html=True)
                    elif symbol == "BTC-USD":
                        st.markdown(f"<h3 style='margin:0;'>${current:,.0f}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:{color}; margin:0;'>{arrow} ${abs(change):.0f} ({change_pct:+.2f}%)</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h3 style='margin:0;'>{current:,.2f}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:{color}; margin:0;'>{arrow} {abs(change):.2f} ({change_pct:+.2f}%)</p>", unsafe_allow_html=True)
            idx += 1
            
    st.markdown("---")
    st.markdown("### 🔍 셰프의 팩트 체크 (진짜 시장이 돌아가는 원리)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **1. 미국 국채 금리 (^TNX)**
        - 시장의 진짜 보스입니다. 이 금리가 오르면 주식과 코인 같은 위험 자산에서 돈이 빠져나가고, 내리면 다시 들어옵니다. 뉴스에서 누가 이긴다더라 하는 말보다 **채권 금리의 방향이 진짜 돈의 흐름**입니다.
        
        **2. 원유와 에너지 (WTI)**
        - 친환경 기조와 상관없이, 인공지능(AI)과 공장 가동에는 엄청난 전력이 필요합니다. 원유와 가스 가격은 글로벌 산업이 얼마나 뜨겁게 돌아가는지(또는 전쟁 리스크가 있는지) 보여주는 가장 확실한 지표입니다.
        """)
    with col2:
        st.markdown("""
        **3. 비트코인 & 금**
        - 정부가 돈을 많이 찍어내어 화폐 가치가 떨어질 때, 사람들은 금과 비트코인으로 도망칩니다. 두 자산의 가격이 동시에 오른다면 시장이 **'종이돈(달러/원화)의 가치 하락'**을 방어하고 있다는 뜻입니다.
        
        **4. 환율 (원/달러)**
        - 지금 화면 위에 떠 있는 환율을 보세요. 달러가 비싸지면 외국인들이 한국 주식을 팔고 도망갑니다. 한국 주식을 살 때는 항상 이 환율이 너무 높지 않은지 먼저 체크해야 합니다.
        """)

# 한국 시장 정치 테마 렌더링 함수
def render_korea_politics_market(usd_krw_rate):
    st.markdown("## 🌶️ Spicy: 국내 시장 (좌파 vs 우파의 시선)")
    st.warning("정치적인 편향 없이, 경제를 바라보는 두 진영의 '철학'이 주식 시장에 어떻게 다르게 돈을 흘려보내는지 적나라하게 팩트만 비교합니다.")
    
    st.markdown("### ⚖️ 경제 철학의 차이: 돈을 어디로 흐르게 할 것인가?")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div style="background-color: #3498DB15; border-top: 5px solid #3498DB; padding: 15px; border-radius: 5px;">
            <h3 style="color: #3498DB; margin-top:0;">🔵 진보/좌파 (분배와 노동 중심)</h3>
            <p><strong>"성장의 과실을 나누고, 내수 시장을 키우자"</strong></p>
            <ul>
                <li><strong>핵심 철학</strong>: 대기업의 독점을 규제하고, 노동자와 서민의 주머니를 채워 내수 소비를 활성화합니다.</li>
                <li><strong>수혜 섹터</strong>: 복지 확대, 신재생 에너지(태양광/풍력), 남북 경협, 내수 소비재, 플랫폼 노동자 처우 개선 관련.</li>
                <li><strong>시장의 우려</strong>: 법인세 인상, 강력한 노조 보장, 대기업 규제로 인해 외국인 투자자가 떠나거나 기업의 수익성이 떨어질 수 있다는 점.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown("""
        <div style="background-color: #E74C3C15; border-top: 5px solid #E74C3C; padding: 15px; border-radius: 5px;">
            <h3 style="color: #E74C3C; margin-top:0;">🔴 보수/우파 (성장과 기업 중심)</h3>
            <p><strong>"기업이 돈을 벌어야 일자리가 생긴다"</strong></p>
            <ul>
                <li><strong>핵심 철학</strong>: 규제를 풀고 법인세를 깎아주어, 대기업과 수출 기업이 글로벌 시장에서 뛰어놀게 만듭니다. (낙수효과)</li>
                <li><strong>수혜 섹터</strong>: 원전(친원전), 건설/부동산(재건축 규제 완화), 방산, 수출 대기업(반도체/자동차), 금융 규제 완화.</li>
                <li><strong>시장의 우려</strong>: 부의 양극화가 심해지고, 노동 환경이 후퇴하며, 내수 시장(골목상권)이 메말라버릴 수 있다는 점.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🥊 진영별 대표 수혜주 실시간 비교")
    
    tab1, tab2 = st.tabs(["🔵 진보/좌파 정책 수혜주", "🔴 보수/우파 정책 수혜주"])
    
    with tab1:
        st.info("신재생 에너지(태양광/풍력), 남북 경협, 보편적 복지 관련주가 주로 움직입니다.")
        left_stocks = {
            "한화솔루션 (태양광/신재생)": "009830.KS",
            "씨에스윈드 (풍력발전)": "112610.KS",
            "아난티 (남북경협/리조트)": "025980.KQ",
            "카카오 (플랫폼/IT)": "035720.KS"
        }
        render_stock_grid(list(left_stocks.keys()), left_stocks, usd_krw_rate)
        
    with tab2:
        st.error("친원전, 건설/부동산 규제 완화, 방위산업, 대기업 수출 지원 관련주가 주로 움직입니다.")
        right_stocks = {
            "두산에너빌리티 (원전 대장주)": "034020.KS",
            "현대건설 (부동산/건설)": "000720.KS",
            "한화에어로스페이스 (방위산업)": "012450.KS",
            "현대차 (수출 대기업)": "005380.KS"
        }
        render_stock_grid(list(right_stocks.keys()), right_stocks, usd_krw_rate)

# 연준 의장 특선 렌더링 함수
def render_fed_chair_special(usd_krw_rate):
    st.markdown("## 🥂 Aperitif (연준 의장 취임 특선 코스)")
    st.info("미국 중앙은행(연준) 의장이 어떤 성향이냐에 따라 주방의 화력(금리)이 달라집니다. 시장의 분위기가 어떻게 바뀔지 예측해 봅니다.")
    
    tab1, tab2 = st.tabs(["🕊️ 시나리오 A: '비둘기파' 의장 (금리 인하/돈 풀기)", "🦅 시나리오 B: '매파' 의장 (금리 인상/물가 잡기)"])
    
    with tab1:
        st.markdown("""
        <div style="background-color: #3498DB15; border-top: 5px solid #3498DB; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <h3 style="color: #3498DB; margin-top:0;">🕊️ 비둘기파 (Dovish): 주방 화력을 부드럽게!</h3>
            <p><strong>시장 분위기:</strong> 전반적으로 따뜻하고 풍성한 요리를 만드는 성향입니다. 시장에 달러(돈)를 많이 풀고 금리를 낮추는 기조입니다.</p>
            <ul>
                <li><strong>빅테크 및 AI 성장주</strong>: 금리가 내려가면 미래 가치를 먹고 자라는 테크 기업들이 가장 큰 혜택을 봅니다. 투자 자금 조달이 쉬워집니다.</li>
                <li><strong>중소형 가성비주/우주항공</strong>: 금리가 낮아지면 중소형 성장 기업들의 숨통이 트이며 주가가 폭발적으로 뛸 수 있습니다.</li>
                <li><strong>비트코인</strong>: 달러 가치가 떨어지면 대체 자산인 가상화폐 시장으로 돈이 강하게 흘러갑니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        dove_stocks = {
            "엔비디아 (AI/빅테크)": "NVDA",
            "애플 (빅테크)": "AAPL",
            "로켓랩 (우주항공)": "RKLB",
            "비트코인 (가상화폐)": "BTC-USD"
        }
        render_stock_grid(list(dove_stocks.keys()), dove_stocks, usd_krw_rate)
        
    with tab2:
        st.markdown("""
        <div style="background-color: #E74C3C15; border-top: 5px solid #E74C3C; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <h3 style="color: #E74C3C; margin-top:0;">🦅 매파 (Hawkish): 과열된 주방에 얼음을!</h3>
            <p><strong>시장 분위기:</strong> 물가(인플레이션)를 잡기 위해 금리를 올리거나 고금리를 유지하여 시장의 돈줄을 조이는 성향입니다.</p>
            <ul>
                <li><strong>전통 에너지 및 배당 우량주</strong>: 금리가 높아지면 사람들은 당장 돈을 잘 벌고 고정적인 용돈(배당)을 주는 탄탄한 기업으로 도망칩니다. (원유, 필수소비재 등)</li>
                <li><strong>금융 및 은행주</strong>: 금리가 오르면 은행들은 대출 마진(예대마진)이 남기 때문에 대표적인 고금리 수혜주로 꼽힙니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        hawk_stocks = {
            "엑슨모빌 (전통 에너지)": "XOM",
            "코카콜라 (배당/필수소비재)": "KO",
            "SCHD (배당성장 ETF)": "SCHD",
            "JP모건 (대형 은행)": "JPM"
        }
        render_stock_grid(list(hawk_stocks.keys()), hawk_stocks, usd_krw_rate)

# K-Market 동향 렌더링 함수
def render_korean_market_movement(usd_krw_rate):
    st.markdown("## 📱 K-Market 동향 (토스/카카오증권 스타일)")
    st.info("토스/카카오페이증권 스타일의 직관적인 UI로 코스피/코스닥의 실시간 온도와 대한민국 대표 대장주들의 흐름을 한눈에 파악합니다.")
    
    st.markdown("### 📊 현재 국내 증시 날씨")
    market_indices = {
        "코스피 (KOSPI)": "^KS11",
        "코스닥 (KOSDAQ)": "^KQ11"
    }
    render_stock_grid(list(market_indices.keys()), market_indices, usd_krw_rate)
    
    st.markdown("### 🔥 지금 가장 뜨거운 국민주 (실시간)")
    top_movers = {
        "삼성전자 (국민주)": "005930.KS",
        "SK하이닉스 (반도체)": "000660.KS",
        "에코프로 (2차전지)": "086520.KQ",
        "네이버 (플랫폼)": "035420.KS",
        "셀트리온 (바이오)": "068270.KS",
        "KB금융 (금융대장)": "105560.KS"
    }
    render_stock_grid(list(top_movers.keys()), top_movers, usd_krw_rate)

# [핵심] 내 장바구니/영수증 (Portfolio) 렌더링 함수
def render_portfolio_page(usd_krw_rate):
    st.markdown("## 🧾 My Portfolio (내 장바구니)")
    st.info("현재 보유 중인 종목의 매수 단가와 수량을 입력하여 실시간 내 계좌의 수익률을 확인하세요.")
    
    DB_FILE = "portfolio_db.csv"
    
    if "portfolio_df" not in st.session_state:
        if os.path.exists(DB_FILE):
            st.session_state.portfolio_df = pd.read_csv(DB_FILE)
            # 하위 호환성: 기존 데이터에 목표수익률 컬럼이 없으면 10.0으로 초기화
            if "목표수익률" not in st.session_state.portfolio_df.columns:
                st.session_state.portfolio_df["목표수익률"] = 10.0
        else:
            st.session_state.portfolio_df = pd.DataFrame(columns=["종목명", "기호", "매수단가", "수량", "목표수익률"])
        
    with st.form("portfolio_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_ticker = st.selectbox("종목 선택", options=list(ALL_STOCKS.keys()))
        with col2:
            buy_price = st.number_input("매수 단가 (원화/달러)", min_value=0.0, step=1.0)
        with col3:
            quantity = st.number_input("수량", min_value=0.0, step=1.0)
        with col4:
            target_profit = st.number_input("목표 온도(익절 수익률 %)", min_value=1.0, value=10.0, step=1.0)
            
        if st.form_submit_button("장바구니 추가"):
            new_row = {"종목명": selected_ticker, "기호": ALL_STOCKS[selected_ticker], "매수단가": buy_price, "수량": quantity, "목표수익률": target_profit}
            st.session_state.portfolio_df = pd.concat([st.session_state.portfolio_df, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.portfolio_df.to_csv(DB_FILE, index=False) # 데이터 영구 저장
            st.success(f"{selected_ticker} 추가 완료!")
            st.rerun()

    if not st.session_state.portfolio_df.empty:
        col_left, col_right = st.columns([8, 2])
        with col_left:
            st.markdown("### 🛒 현재 내 장바구니 현황")
        with col_right:
            if st.button("🗑️ 장바구니 비우기"):
                st.session_state.portfolio_df = pd.DataFrame(columns=["종목명", "기호", "매수단가", "수량", "목표수익률"])
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                st.rerun()
        total_investment_krw = 0
        total_current_krw = 0
        
        for idx, row in st.session_state.portfolio_df.iterrows():
            sym = row["기호"]
            df, _ = fetch_stock_data_cached(sym)
            if not df.empty:
                curr_price = df['Close'].iloc[-1]
                is_korean = sym.endswith('.KS') or sym.endswith('.KQ')
                
                if is_korean:
                    inv_krw = row["매수단가"] * row["수량"]
                    cur_krw = curr_price * row["수량"]
                else:
                    inv_krw = row["매수단가"] * row["수량"] * usd_krw_rate
                    cur_krw = curr_price * row["수량"] * usd_krw_rate
                    
                total_investment_krw += inv_krw
                total_current_krw += cur_krw
                
                profit_pct = ((curr_price - row["매수단가"]) / row["매수단가"]) * 100 if row["매수단가"] > 0 else 0
                target_profit = row.get("목표수익률", 10.0)
                
                # 목표 달성 알람 로직
                if profit_pct >= target_profit:
                    status_text = f"🎉 띵-! 요리 완성! (목표 {target_profit}% 달성, 지금 익절하세요!)"
                    
                    if 'profit_alerts' not in st.session_state:
                        st.session_state.profit_alerts = set()
                    if row['종목명'] not in st.session_state.profit_alerts:
                        st.toast(f"🍽️ '{row['종목명']}' 요리가 완성되었습니다! 맛있게 드세요(익절)!", icon="🎉")
                        st.session_state.profit_alerts.add(row['종목명'])
                else:
                    status_text = f"🔥 요리 중... (목표까지 {target_profit - profit_pct:.2f}% 남음)"
                    
                    if 'profit_alerts' in st.session_state and row['종목명'] in st.session_state.profit_alerts:
                        st.session_state.profit_alerts.remove(row['종목명'])
                        
                st.write(f"- **{row['종목명']}**: 실시간 수익률 **{profit_pct:+.2f}%** (현재가: {curr_price:,.2f}) ➔ {status_text}")
                
        if total_investment_krw > 0:
            total_profit_pct = ((total_current_krw - total_investment_krw) / total_investment_krw) * 100
            st.metric("총 계좌 자산 (원화 환산)", f"₩{total_current_krw:,.0f}", f"{total_profit_pct:+.2f}%")

# [핵심] 과거 요리 성적표 (Backtesting) 렌더링 함수
def render_backtest_page():
    st.markdown("## 🔬 Lab (과거 줍줍 성적표)")
    st.info("과거 1년 동안 우리의 AI 셰프가 '줍줍(RSI < 30)' 신호를 보냈을 때 실제로 샀다면 어떤 결과가 있었을까요? 직접 확인해 보세요.")
    
    test_ticker = st.selectbox("테스트할 종목 선택", list(ALL_STOCKS.keys()), index=0)
    symbol = ALL_STOCKS[test_ticker]
    
    st.write("데이터를 굽는 중입니다... 🍳")
    df = yf.Ticker(symbol).history(period="1y", interval="1d")
    if not df.empty:
        df['RSI'] = calculate_rsi(df['Close'])
        buy_signals = df[df['RSI'] < 30]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='주가 흐름', line=dict(color='#BDC3C7')))
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='바겐세일(줍줍) 신호!', marker=dict(color='#E74C3C', size=12, symbol='triangle-up')))
        
        fig.update_layout(
            title=f"{test_ticker} 과거 1년 줍줍 타이밍 성과", 
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"과거 1년 동안 총 **{len(buy_signals)}번**의 명확한 바겐세일(줍줍) 기회가 있었습니다. 위 빨간 화살표 시점에서 샀다면 주가가 어떻게 회복되었는지 차트로 확인하세요!")
    else:
        st.warning("데이터를 불러오지 못했습니다.")

# 실시간 자동 새로고침 래퍼
@st.fragment(run_every=10)
def show_live_dashboard():
    # 원달러 환율 가져오기
    try:
        df_ex = yf.Ticker("KRW=X").history(period="1d")
        usd_krw_rate = df_ex['Close'].iloc[-1] if not df_ex.empty else 1350.0
    except:
        usd_krw_rate = 1350.0

    st.title(f"👨‍🍳 Investment Kitchen: {course}")
    st.caption(f"마지막 업데이트: {time.strftime('%H:%M:%S')} (기준 환율: 1달러 = {usd_krw_rate:,.1f}원)")
    
    if course == "🌎 Welcome Drink (글로벌 시장 현황)":
        render_global_market(usd_krw_rate)
        
    elif course == "🥂 Aperitif (연준 의장 취임 특선)":
        render_fed_chair_special(usd_krw_rate)
        
    elif course == "🍷 Amuse (주식 기초 유치원)":
        render_kindergarten_page()
        
    elif course == "🥗 Appetizer (소액 가성비주)":
        st.success("커피 한두 잔 값이면 내 주식을 가질 수 있어요! 작게 시작해서 크게 키워보세요.")
        render_stock_grid(list(CATEGORY_STOCKS["🪙 소액 가성비주"].keys()), CATEGORY_STOCKS["🪙 소액 가성비주"], usd_krw_rate)
        
    elif course == "🌶️ Spicy (국내 시장: 좌파 vs 우파)":
        render_korea_politics_market(usd_krw_rate)
        
    elif course == "🥩 Main (테마별 메인 요리)":
        st.subheader("🥩 오늘의 메인 테마 요리")
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🦅 트럼프 외교/방산", 
            "🇨🇳 트럼프 방중", 
            "🔥 LNG/가스", 
            "🛢️ 가솔린/원유", 
            "🔥 AI 성장주", 
            "🇰🇷 국내 대장주"
        ])
        
        with tab1:
            st.success("트럼프 방한 및 외교/방산 정책의 수혜를 입는 기업들입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🦅 트럼프 수혜주"].keys()), CATEGORY_STOCKS["🦅 트럼프 수혜주"], usd_krw_rate)
        with tab2:
            st.success("트럼프 방중으로 미중 무역 관계 개선 또는 갈등의 영향을 크게 받는 기업들입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🇨🇳 트럼프 방중 관심주"].keys()), CATEGORY_STOCKS["🇨🇳 트럼프 방중 관심주"], usd_krw_rate)
        with tab3:
            st.success("유럽/아시아 수출 확대가 기대되는 천연가스와 LNG 관련주입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🔥 미국 에너지 (LNG/가스)"].keys()), CATEGORY_STOCKS["🔥 미국 에너지 (LNG/가스)"], usd_krw_rate)
        with tab4:
            st.success("화석연료 규제 완화 수혜를 입는 가솔린, 정유, 원유 대장주입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🛢️ 미국 에너지 (가솔린/원유)"].keys()), CATEGORY_STOCKS["🛢️ 미국 에너지 (가솔린/원유)"], usd_krw_rate)
        with tab5:
            st.success("미래를 이끌어갈 글로벌 AI 핵심 기업들의 실시간 온도를 확인하세요.")
            render_stock_grid(list(CATEGORY_STOCKS["🔥 AI 성장주"].keys()), CATEGORY_STOCKS["🔥 AI 성장주"], usd_krw_rate)
        with tab6:
            st.success("대한민국 경제를 대표하는 1등 기업들의 실시간 현황입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🇰🇷 국내 주요 주식"].keys()), CATEGORY_STOCKS["🇰🇷 국내 주요 주식"], usd_krw_rate)
            
    elif course == "🌍 Global Cuisine (유럽/아시아 마켓)":
        st.subheader("🌍 해외 특선 요리: 유럽, 일본, 중국")
        st.info("각 대륙과 국가의 뚜렷한 개성을 지닌 글로벌 핵심 재료들입니다.")
        
        tab1, tab2, tab3 = st.tabs(["🏰 묵직한 유럽식 (명품/장인)", "🍱 깔끔한 일식 (일본 우량주)", "🐼 매콤한 중식 (중국 부양책)"])
        
        with tab1:
            st.success("수백 년의 전통을 자랑하는 명품과 대체 불가한 글로벌 기술 장인 기업들입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🏰 묵직한 유럽식 (명품 및 전통 장인)"].keys()), CATEGORY_STOCKS["🏰 묵직한 유럽식 (명품 및 전통 장인)"], usd_krw_rate)
            
        with tab2:
            st.success("안정적인 기술력과 글로벌 브랜드를 앞세운 일본의 대표 우량주 및 시장 지표입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🍱 깔끔한 일식 (일본 우량주)"].keys()), CATEGORY_STOCKS["🍱 깔끔한 일식 (일본 우량주)"], usd_krw_rate)
            
        with tab3:
            st.success("거대한 내수 시장과 강력한 정부 부양책의 직접적인 수혜를 입는 중국 대장주입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🐼 매콤한 중식 (중국 부양책 수혜)"].keys()), CATEGORY_STOCKS["🐼 매콤한 중식 (중국 부양책 수혜)"], usd_krw_rate)
            
    elif course == "📱 K-Market 동향 (토스/카카오 스타일)":
        render_korean_market_movement(usd_krw_rate)
        
    elif course == "🧾 My Portfolio (내 장바구니)":
        render_portfolio_page(usd_krw_rate)
        
    elif course == "🔬 Lab (과거 줍줍 성적표)":
        render_backtest_page()
            
    elif course == "🍰 Dessert (초장기 투자 및 비교)":
        st.subheader("🍰 식후 디저트: 미래 구상 및 테마 비교")
        tab1, tab2, tab3 = st.tabs([
            "🚀 10년 메가트렌드", 
            "⚖️ 테마 비교 레이스", 
            "🗺️ 50개주 수혜 지도"
        ])
        
        with tab1:
            st.success("단기 등락에 연연하지 않고 10년 뒤 세상을 바꿀 초장기 투자 기대주들입니다.")
            render_stock_grid(list(CATEGORY_STOCKS["🚀 향후 10년 기대주"].keys()), CATEGORY_STOCKS["🚀 향후 10년 기대주"], usd_krw_rate)
        with tab2:
            render_comparison_page()
        with tab3:
            render_usa_map_page()
            
    elif course == "🍽️ A la carte (내 맘대로 뷔페)":
        st.subheader("🍽️ 뷔페 (자유 선택)")
        
    elif course == "🤖 AI 수석 셰프 (Gemini 상담)":
        render_gemini_chef()
        
        with st.expander("👨‍🍳 셰프의 강력 추천: 쿠팡 전 사외이사 연준 의장 취임에 대비한 '바벨 전략'", expanded=True):
            st.info("새로운 연준 의장의 정책 방향이 아직 불확실할 때는, 양 극단의 시나리오(매파/비둘기파)를 모두 방어할 수 있는 '바벨 전략(Barbell Strategy)'이 최고입니다. 아래 세 종목은 어떤 정책이 나와도 계좌에 초록불을 켜줄 핵심 재료입니다.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **🗺️ 1. '쿠팡식 혁신' 연준 의장의 나비효과 (비둘기/성장 시나리오)**
                - **물류 인프라의 디지털화**: 이커머스 생태계를 잘 아는 의장은 디지털 물류/자동화 인프라 기업에 우호적일 가능성이 큽니다.
                  👉 **팔란티어(PLTR)**: 쿠팡식 데이터/AI 물류 혁신과 궤를 같이하는 압도적인 AI 소프트웨어 대장.
                - **한미 공급망 재편**: 트럼프의 리쇼어링(공장 복귀)과 겹치면서 한국 기업들에 새로운 외교적 돌파구가 열립니다.
                  👉 **한화오션**: 미국 공급망 재편과 한국 귀환 파장의 교집합에 있는 강력한 조선/방산 재료.
                """)
            with col2:
                st.markdown("""
                **🥩 2. 어떤 매운맛이 와도 든든한 뚝배기 (매파/방어 시나리오)**
                - **에너지 및 물가 방어**: 만약 새 의장이 인플레이션을 명분으로 강한 긴축(고금리 유지)을 펼치더라도 끄떡없는 종목이 필요합니다.
                  👉 **엑슨모빌(XOM)**: 물가가 오르고 금리가 높아져도 돈을 쓸어 담는 전통 에너지의 대장.
                
                💡 **셰프의 조언**: 거물급 인사의 이동으로 시장 변동성이 클 때는, 10초마다 갱신되는 화면을 보시며 **차분하게 '중불'로 대응**하시는 것을 추천합니다.
                """)
                
        # 셰프 추천 조합을 기본값으로 설정
        default_selections = [
            "팔란티어 (가장 뜨거운 AI)", 
            "한화오션 (국내 조선/방산)", 
            "엑슨모빌 (가솔린/원유 대장)"
        ]
        
        # 만약 기본값이 ALL_STOCKS에 없다면 있는 것만 선택
        valid_defaults = [s for s in default_selections if s in ALL_STOCKS.keys()]
        
        selected = st.multiselect("종목 자유 선택", options=list(ALL_STOCKS.keys()), default=valid_defaults)
        render_stock_grid(selected, ALL_STOCKS, usd_krw_rate)

# [핵심] AI 수석 셰프 (Gemini) 렌더링 함수
def render_gemini_chef():
    st.markdown("## 🤖 AI 수석 셰프 (Google Gemini)")
    st.info("시장에 대해 궁금한 점이나 요리법(투자 조언)을 수석 셰프에게 직접 물어보세요! (5살도 이해하는 요리 비유로 설명해 줍니다)")
    
    # API 키 입력
    api_key = st.text_input("🔑 Google Gemini API 키를 입력해주세요 (보안을 위해 서버에 저장되지 않습니다)", type="password")
    
    if not api_key:
        st.warning("API 키를 입력하셔야 셰프와 대화할 수 있습니다. (구글 AI Studio에서 무료로 발급 가능)")
        st.markdown("[👉 무료 API 키 발급받기 (Google AI Studio)](https://aistudio.google.com/app/apikey)")
        return
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if "gemini_messages" not in st.session_state:
            st.session_state.gemini_messages = [
                {"role": "assistant", "content": "어서 오세요! 저는 Investment Kitchen의 수석 셰프입니다. 👨‍🍳 오늘 어떤 주식 재료에 대해 상담해 드릴까요?"}
            ]
            
        for msg in st.session_state.gemini_messages:
            with st.chat_message(msg["role"], avatar="👨‍🍳" if msg["role"] == "assistant" else "🧑‍💼"):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input("예: 엔비디아가 너무 뜨거운데 지금 익절(접시에 덜어내기) 할까요?"):
            st.session_state.gemini_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💼"):
                st.markdown(prompt)
                
            with st.chat_message("assistant", avatar="👨‍🍳"):
                message_placeholder = st.empty()
                message_placeholder.markdown("셰프가 레시피를 고민 중입니다... 🍳")
                try:
                    system_prompt = "당신은 'Investment Kitchen'이라는 주식 투자 레스토랑의 AI 수석 셰프입니다. 주식 시장의 복잡한 이야기를 5살도 이해할 수 있는 요리 비유(온도, 재료, 레시피, 굽기, 신선도 등)를 사용하여 친절하고 전문적으로 답변해주세요. 사용자 질문: "
                    response = model.generate_content(system_prompt + prompt)
                    full_response = response.text
                    message_placeholder.markdown(full_response)
                    st.session_state.gemini_messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    message_placeholder.error(f"앗! 요리 중 에러가 발생했습니다: {str(e)}")
                    
    except ImportError:
        st.error("google-generativeai 라이브러리가 설치되지 않았습니다. 터미널에서 pip install google-generativeai 를 실행해주세요.")

# 대시보드 렌더링
show_live_dashboard()
