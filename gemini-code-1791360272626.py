import platform
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# ---------------------------------------------------------
# [한글 폰트 깨짐 방지 설정]
# ---------------------------------------------------------
system_name = platform.system()
if system_name == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif system_name == "Darwin":
    plt.rc("font", family="AppleGothic")
else:
    plt.rc("font", family="NanumGothic")

plt.rc("axes", unicode_minus=False)

# ---------------------------------------------------------
# [페이지 기본 설정]
# ---------------------------------------------------------
st.set_page_config(
    page_title="iOS 배터리 예측기",
    page_icon="🔋",
    layout="wide",
)

# ---------------------------------------------------------
# [iOS 스타일 전체 다크 테마 CSS]
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
        }

        [data-testid="stSidebar"] {
            background-color: #1c1c1e !important;
            border-right: 1px solid #2c2c2e;
        }
        
        [data-testid="stSidebar"] * {
            color: #f2f2f7 !important;
        }

        .stNumberInput input, .stSelectbox div, .stMultiSelect div {
            background-color: #2c2c2e !important;
            color: #ffffff !important;
            border-radius: 10px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# [사용자 입력 섹션 - 사이드바]
# ---------------------------------------------------------
st.sidebar.header("⚙️ 1. 기기 기본 & 배터리 건강 정보")
current_battery_pct = st.sidebar.slider(
    "현재 남아있는 배터리 잔량 (%)", 1, 100, 80
)
battery_capacity_mah = 5000

battery_soh = st.sidebar.slider(
    "배터리 성능 상태 / 건강도 (%)",
    50,
    100,
    90,
    help="배터리 효율(SoH)이 낮을수록 실제 사용 가능 용량이 줄어듭니다.",
)

st.sidebar.header("💾 2. 저장공간 상태 (GB)")
total_storage_gb = st.sidebar.number_input(
    "총 저장용량 (GB)", value=128, step=64, min_value=16
)
used_storage_gb = st.sidebar.number_input(
    "사용 중인 용량 (GB)",
    value=100,
    step=1,
    min_value=0,
    max_value=total_storage_gb,
)

free_storage_gb = max(0, total_storage_gb - used_storage_gb)
storage_free_pct = (
    (free_storage_gb / total_storage_gb) * 100 if total_storage_gb > 0 else 0
)

st.sidebar.caption(
    f"💡 남은 저장공간: {free_storage_gb} GB ({storage_free_pct:.1f}%)"
)

st.sidebar.header("📱 3. 사용 앱 & 메인 앱 설정")

all_app_options = [
    "카카오톡 / 문자 (텍스트 중심)",
    "인스타그램 / 숏폼 (이미지/미디어)",
    "유튜브 / 동영상 스트리밍",
    "3D 고사양 게임 (원신, 배그 등)",
]

# 1. 이용할 앱 다중 선택
app_choices = st.sidebar.multiselect(
    "이용할 앱 선택 (다중 선택 가능)",
    all_app_options,
    default=["유튜브 / 동영상 스트리밍", "카카오톡 / 문자 (텍스트 중심)"],
)

# 2. 가장 많이 쓸 앱 지정 (선택된 앱 목록을 최상단으로 정렬)
ordered_apps = []
main_app = None

if app_choices:
    main_app = st.sidebar.selectbox(
        "🥇 가장 많이 사용할 메인 앱 선택 (1위 지정)",
        app_choices,
        index=0,
    )
    # 메인 앱을 가장 위(1순위)로 두고 나머지 앱을 배치
    ordered_apps = [main_app] + [app for app in app_choices if app != main_app]
    
    st.sidebar.caption("📌 **사용 우선순위 순서:**")
    for idx, app in enumerate(ordered_apps, 1):
        st.sidebar.caption(f"{idx}위: {app}")

video_resolution = "1080p (FHD)"
if "유튜브 / 동영상 스트리밍" in app_choices:
    video_resolution = st.sidebar.radio(
        "🎬 유튜브 재생 해상도",
        ["480p (SD)", "720p (HD)", "1080p (FHD)", "4K (2160p)"],
        index=2,
    )

st.sidebar.header("💡 4. 디스플레이 & 사운드")

col_ios1, col_ios2 = st.sidebar.columns(2)
with col_ios1:
    screen_brightness = st.sidebar.slider("☀️ 밝기 (%)", 10, 100, 70)

with col_ios2:
    volume_level = st.sidebar.slider("🔊 음량 (%)", 0, 100, 50)

is_dark_mode = st.sidebar.checkbox("다크 모드 적용 (OLED 절전)", value=True)

sound_mode = st.sidebar.radio(
    "사운드 모드",
    ["소리 모드", "진동 모드", "무음 모드"],
    horizontal=True,
)

st.sidebar.header("📡 5. 통신 & 무선 연결")
network_type = st.sidebar.radio(
    "인터넷 연결 방식", ["Wi-Fi", "5G / LTE"], horizontal=True
)
is_bluetooth_gps = st.sidebar.checkbox(
    "블루투스 / GPS / 위치서비스 켜짐", value=True
)

st.sidebar.header("🔋 6. 절전 옵션")
is_power_saving = st.sidebar.checkbox("절전 모드 활성화")

# ---------------------------------------------------------
# [iOS 헤더 & 아이콘]
# ---------------------------------------------------------
st.markdown(
    """
<div style="display: flex; align-items: center; gap: 18px; margin-bottom: 25px;">
    <div style="
        width: 60px;
        height: 60px;
        background: #30d158;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        box-shadow: 0 4px 15px rgba(48, 209, 88, 0.4);
    ">
        🔋
    </div>
    <div>
        <h1 style="margin: 0; font-size: 26px; font-weight: 700; color: #ffffff;">
            배터리 상태 & 예측
        </h1>
        <p style="margin: 2px 0 0 0; font-size: 13px; color: #8e8e93;">
            iOS Control Center & Battery Analytics
        </p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# [전력 소모량(W) 연산 엔진]
# ---------------------------------------------------------
effective_capacity_mah = battery_capacity_mah * (battery_soh / 100.0)

storage_power = 0.0
if storage_free_pct < 5:
    storage_power = 0.5
elif storage_free_pct < 15:
    storage_power = 0.2

app_power_dict = {
    "카카오톡 / 문자 (텍스트 중심)": 0.8,
    "인스타그램 / 숏폼 (이미지/미디어)": 2.2,
    "유튜브 / 동영상 스트리밍": 2.0,
    "3D 고사양 게임 (원신, 배그 등)": 5.2,
}

# 1위 앱 전력 100% 반영 + 백그라운드/서브 앱 전력 40% 반영 계산
if ordered_apps:
    main_power = app_power_dict[ordered_apps[0]]
    sub_power = sum(app_power_dict[app] * 0.4 for app in ordered_apps[1:])
    base_power = main_power + sub_power
else:
    base_power = 0.3

resolution_power = 0.0
if "유튜브 / 동영상 스트리밍" in app_choices:
    res_power_dict = {
        "480p (SD)": 0.2,
        "720p (HD)": 0.5,
        "1080p (FHD)": 0.9,
        "4K (2160p)": 2.2,
    }
    resolution_power = res_power_dict[video_resolution]

brightness_factor = (screen_brightness / 100) ** 1.5
dark_mode_discount = 0.7 if is_dark_mode else 1.0
screen_power = (0.5 + brightness_factor * 2.0) * dark_mode_discount

audio_power = 0.0
if sound_mode == "소리 모드":
    audio_power = 0.1 + (volume_level / 100) * 0.4
elif sound_mode == "진동 모드":
    audio_power = 0.15

network_power = 0.9 if network_type == "5G / LTE" else 0.3
extra_wireless_power = 0.4 if is_bluetooth_gps else 0.0

total_power_w = (
    base_power
    + resolution_power
    + screen_power
    + audio_power
    + network_power
    + extra_wireless_power
    + storage_power
)

if is_power_saving:
    total_power_w *= 0.75

nominal_voltage = 3.85
total_current_ma = (total_power_w / nominal_voltage) * 1000

drain_rate_per_hour = (total_current_ma / effective_capacity_mah) * 100
drain_rate_per_min = drain_rate_per_hour / 60.0

total_remaining_minutes = int(
    (current_battery_pct / 100.0 * effective_capacity_mah)
    / total_current_ma
    * 60
)
remaining_hours = total_remaining_minutes // 60
remaining_minutes = total_remaining_minutes % 60

# ---------------------------------------------------------
# [아이폰 제어센터 위젯]
# ---------------------------------------------------------
c_bright, c_vol, c_empty = st.columns([1, 1, 3])

with c_bright:
    st.markdown(
        f"""
        <div style="background: #1c1c1e; border-radius: 20px; padding: 15px; text-align: center; border: 1px solid #2c2c2e;">
            <div style="font-size: 11px; color: #8e8e93; font-weight: 600; margin-bottom: 8px;">BRIGHTNESS</div>
            <div style="background: #2c2c2e; height: 90px; width: 44px; margin: 0 auto; border-radius: 22px; position: relative; overflow: hidden; display: flex; align-items: flex-end;">
                <div style="background: #ffffff; width: 100%; height: {screen_brightness}%;"></div>
            </div>
            <div style="font-size: 14px; color: #ffffff; font-weight: 700; margin-top: 8px;">☀️ {screen_brightness}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_vol:
    st.markdown(
        f"""
        <div style="background: #1c1c1e; border-radius: 20px; padding: 15px; text-align: center; border: 1px solid #2c2c2e;">
            <div style="font-size: 11px; color: #8e8e93; font-weight: 600; margin-bottom: 8px;">VOLUME</div>
            <div style="background: #2c2c2e; height: 90px; width: 44px; margin: 0 auto; border-radius: 22px; position: relative; overflow: hidden; display: flex; align-items: flex-end;">
                <div style="background: #ffffff; width: 100%; height: {volume_level}%;"></div>
            </div>
            <div style="font-size: 14px; color: #ffffff; font-weight: 700; margin-top: 8px;">🔊 {volume_level}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# [iOS 메트릭 카드]
# ---------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)


def draw_card(col, title, value, sub=""):
    with col:
        st.markdown(
            f"""
            <div style="background: #1c1c1e; border-radius: 16px; padding: 12px 14px; border: 1px solid #2c2c2e;">
                <div style="font-size: 11px; color: #8e8e93; margin-bottom: 4px;">{title}</div>
                <div style="font-size: 17px; color: #ffffff; font-weight: 700;">{value}</div>
                <div style="font-size: 10px; color: #30d158; margin-top: 2px;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


draw_card(
    col1,
    "실효 용량 (SoH)",
    f"{int(effective_capacity_mah)} mAh",
    f"기본 {battery_capacity_mah} mAh",
)
draw_card(col2, "총 소모 전력", f"{total_power_w:.2f} W")
draw_card(col3, "분당 감소율", f"-{drain_rate_per_min:.2f} %/분")
draw_card(col4, "시간당 감소율", f"-{drain_rate_per_hour:.1f} %/시간")
draw_card(
    col5,
    "남은 시간",
    f"{remaining_hours}시간 {remaining_minutes}분",
    f"총 {total_remaining_minutes}분",
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# [분 단위 고정 축 시각화 그래프]
# ---------------------------------------------------------
st.subheader("📉 시간 경과(분)에 따른 배터리 잔량 예측 곡선")

max_minutes = 720
time_steps_min = np.linspace(0, max_minutes, 300)

battery_levels = current_battery_pct - (drain_rate_per_min * time_steps_min)
battery_levels = np.maximum(0, battery_levels)

fig, ax = plt.subplots(figsize=(10, 3.5), facecolor="#000000")
ax.set_facecolor("#1c1c1e")

ax.plot(
    time_steps_min,
    battery_levels,
    color="#30d158",
    linewidth=3,
    label="배터리 잔량 추이",
)

ax.axhline(20, color="#ff9f0a", linestyle="--", label="절전 권장 구간 (20%)")

ax.set_xlim(0, max_minutes)
ax.set_ylim(0, 105)

ax.set_xlabel("사용 시간 (분)", color="#8e8e93", fontsize=10)
ax.set_ylabel("배터리 잔량 (%)", color="#8e8e93", fontsize=10)

ax.tick_params(colors="#ffffff", labelsize=9)
ax.spines["bottom"].set_color("#2c2c2e")
ax.spines["top"].set_color("#2c2c2e")
ax.spines["right"].set_color("#2c2c2e")
ax.spines["left"].set_color("#2c2c2e")

ax.grid(True, color="#2c2c2e", alpha=0.6)
ax.legend(
    loc="upper right",
    facecolor="#2c2c2e",
    edgecolor="#3a3a3c",
    labelcolor="#ffffff",
)

st.pyplot(fig)