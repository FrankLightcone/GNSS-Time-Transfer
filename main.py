# @Author: 范睿捷
# @ID: 23303017
# @Date: 2025-03-23
# @File: GNSS Experiment 1: GNSS 时间转换
# @Builder: Streamlit


import streamlit as st
import datetime
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta

# 会话状态 session state
if 'time_input' not in st.session_state:
    st.session_state.time_input = datetime.now().strftime("%H:%M:%S")
if 'gps_time_input' not in st.session_state:
    st.session_state.gps_time_input = datetime.now().strftime("%H:%M:%S")
if 'bds_time_input' not in st.session_state:
    st.session_state.bds_time_input = datetime.now().strftime("%H:%M:%S")
if 'base_time_input' not in st.session_state:
    st.session_state.base_time_input = datetime.now().strftime("%H:%M:%S")

# 设置页面配置
st.set_page_config(
    page_title="GNSS 时间转换器",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用自定义CSS改善美观
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #3B82F6;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-text {
        color: #4B5563;
        font-size: 1rem;
    }
    .result-container {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1.5rem;
        border-left: 5px solid #3B82F6;
    }
    .homework-container {
        background-color: #EFF6FF;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1.5rem;
        border-left: 5px solid #1D4ED8;
    }
    .stButton button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: 600;
    }
    .stButton button:hover {
        background-color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# 儒略日计算常量
MODIFIED = 2400000.5
JDAD = 1720981.5
ADOY = 365.25
ADOM = 30.6001

# GPS和BDS起始时间
GPS_START_MJD = 44244  # GPS时间起点 (1980-01-06)
BDS_START_MJD = 53005  # 北斗时间起点 (2006-01-01)

# 标题
st.markdown('<div class="main-header">GNSS 时间转换器</div>', unsafe_allow_html=True)
st.markdown('<div class="info-text">卫星导航系统时间系统全面转换工具</div>', unsafe_allow_html=True)

# 创建不同转换功能的标签页
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "日期/时间 → MJD", 
    "日期 → 年积日", 
    "日期/时间 → GPS时间", 
    "日期/时间 → 北斗时间",
    "时间相加",
    "作业题目"
])

# 计算MJD的函数
def to_mjd(year, month, day, hour=0, minute=0, second=0):
    if month <= 2:
        year = year - 1
        month = month + 12
    
    a = math.floor(ADOY * year)
    b = math.floor(ADOM * (month + 1))
    
    jd = a + b + day + (hour / 24) + (minute / 1440) + (second / 86400) + JDAD
    mjd = jd - MODIFIED
    
    return mjd

# 计算年积日的函数
def to_doy(year, month, day):
    date_obj = datetime(year, month, day)
    day_of_year = date_obj.timetuple().tm_yday
    return day_of_year

# 转换为GPS周和秒的函数
def to_gps(year, month, day, hour=0, minute=0, second=0):
    mjd = to_mjd(year, month, day, hour, minute, second)
    gps_week = math.floor((mjd - GPS_START_MJD) / 7)
    
    # 计算周内秒
    days_in_week = mjd - GPS_START_MJD - gps_week * 7
    gps_seconds = (days_in_week * 86400) + 18  # 添加闰秒
    
    return gps_week, gps_seconds

# 转换为北斗周和秒的函数
def to_bds(year, month, day, hour=0, minute=0, second=0):
    gps_week, gps_seconds = to_gps(year, month, day, hour, minute, second)
    bds_week = gps_week - 1356
    bds_seconds = gps_seconds - 14  # GPS与北斗的差异
    
    return bds_week, bds_seconds

# 检查闰年的函数
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# 获取每月天数的函数
def days_in_month(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28
    else:
        return 0

# 时间相加的函数
def add_times(year, month, day, hour, minute, second, 
              add_year, add_month, add_day, add_hour, add_minute, add_second):
    
    # 添加秒
    second += add_second
    carry_minute = int(second // 60)
    second = second % 60
    
    # 添加分钟
    minute += add_minute + carry_minute
    carry_hour = int(minute // 60)
    minute = minute % 60
    
    # 添加小时
    hour += add_hour + carry_hour
    carry_day = int(hour // 24)
    hour = hour % 24
    
    # 添加天数(由于月份长度不同，这部分较复杂)
    day += add_day + carry_day
    
    # 添加月份
    month += add_month
    while month > 12:
        month -= 12
        year += 1
    
    # 调整日期溢出
    while day > days_in_month(year, month):
        day -= days_in_month(year, month)
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    # 添加年份
    year += add_year
    
    return year, month, day, hour, minute, second

# 解析输入时间的函数 (处理小数点)
def parse_time_input(time_str):
    parts = time_str.split(':')
    if len(parts) < 2 or len(parts) > 3:
        st.error("时间格式错误! 请使用 HH:MM:SS.sss 格式")
        return None, None, None
    
    try:
        hour = int(parts[0])
        minute = int(parts[1])
        second = 0
        
        if len(parts) == 3:
            second = float(parts[2])
            
        if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
            st.error("时间值超出范围!")
            return None, None, None
            
        return hour, minute, second
    except ValueError:
        st.error("时间格式错误! 请确保小时和分钟是整数，秒可以是小数")
        return None, None, None

# 标签页1: 日期/时间到MJD
with tab1:
    st.markdown('<div class="sub-header">将日期和时间转换为修正儒略日(MJD)</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        dt_date = st.date_input("选择日期", datetime.now())
    
    with col2:
        time_str = st.text_input("输入时间 (格式: HH:MM:SS.sss)", 
                         value=st.session_state.time_input,
                         key="time_str")
        st.session_state.time_input = time_str
    
    if st.button("计算MJD", key="calc_mjd"):
        hour, minute, second = parse_time_input(time_str)
        
        if hour is not None:
            year = dt_date.year
            month = dt_date.month
            day = dt_date.day
            
            result_mjd = to_mjd(year, month, day, hour, minute, second)
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown(f"### MJD结果: {result_mjd:.6f}")
            st.markdown(f"输入: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:06.3f}")
            st.markdown('</div>', unsafe_allow_html=True)

# 标签页2: 日期到年积日
with tab2:
    st.markdown('<div class="sub-header">将日期转换为年积日(DOY)</div>', unsafe_allow_html=True)
    
    doy_date = st.date_input("选择日期", datetime.now(), key="doy_date")
    
    if st.button("计算年积日", key="calc_doy"):
        year = doy_date.year
        month = doy_date.month
        day = doy_date.day
        
        result_doy = to_doy(year, month, day)
        
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.markdown(f"### 年积日结果: {result_doy}")
        st.markdown(f"输入: {year}-{month:02d}-{day:02d}")
        st.markdown('</div>', unsafe_allow_html=True)

# 标签页3: 日期/时间到GPS时间
with tab3:
    st.markdown('<div class="sub-header">将日期和时间转换为GPS周和周内秒</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        gps_date = st.date_input("选择日期", datetime.now(), key="gps_date")
    
    with col2:
        gps_time_str = st.text_input("输入时间 (格式: HH:MM:SS.sss)", 
                                     value=st.session_state.gps_time_input,
                                     key="gps_time_str")
        st.session_state.gps_time_input = gps_time_str
    
    if st.button("计算GPS时间", key="calc_gps"):
        hour, minute, second = parse_time_input(gps_time_str)
        
        if hour is not None:
            year = gps_date.year
            month = gps_date.month
            day = gps_date.day
            
            gps_week, gps_seconds = to_gps(year, month, day, hour, minute, second)
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown(f"### GPS时间结果")
            st.markdown(f"**GPS周：** {gps_week}")
            st.markdown(f"**周内秒：** {gps_seconds:.3f}")
            st.markdown(f"输入: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:06.3f}")
            st.markdown('</div>', unsafe_allow_html=True)

# 标签页4: 日期/时间到北斗时间
with tab4:
    st.markdown('<div class="sub-header">将日期和时间转换为北斗周和周内秒</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        bds_date = st.date_input("选择日期", datetime.now(), key="bds_date")
    
    with col2:
        bds_time_str = st.text_input("输入时间 (HH:MM:SS.sss)", 
                                     value=st.session_state.bds_time_input,
                                     key="bds_time_str")
        st.session_state.bds_time_input = bds_time_str
    
    if st.button("计算北斗时间", key="calc_bds"):
        hour, minute, second = parse_time_input(bds_time_str)
        
        if hour is not None:
            year = bds_date.year
            month = bds_date.month
            day = bds_date.day
            
            bds_week, bds_seconds = to_bds(year, month, day, hour, minute, second)
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown(f"### 北斗时间结果")
            st.markdown(f"**北斗周：** {bds_week}")
            st.markdown(f"**周内秒：** {bds_seconds:.3f}")
            st.markdown(f"输入: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:06.3f}")
            st.markdown('</div>', unsafe_allow_html=True)

# 标签页5: 时间相加
with tab5:
    st.markdown('<div class="sub-header">时间间隔相加</div>', unsafe_allow_html=True)
    
    st.markdown("### 基准时间")
    col1, col2 = st.columns(2)
    
    with col1:
        base_date = st.date_input("选择基准日期", datetime.now(), key="base_date")
    
    with col2:
        base_time_str = st.text_input("输入基准时间 (格式: HH:MM:SS.sss)", 
                                      value=st.session_state.base_time_input,
                                      key="base_time_str")
        st.session_state.base_time_input = base_time_str
    
    st.markdown("### 需要添加的时间")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        add_years = st.number_input("年", min_value=0, step=1, value=0)
        add_months = st.number_input("月", min_value=0, step=1, value=0)
        add_days = st.number_input("天", min_value=0, step=1, value=0)
    
    with col2:
        add_hours = st.number_input("小时", min_value=0, step=1, value=0)
        add_minutes = st.number_input("分钟", min_value=0, step=1, value=0)
    
    with col3:
        add_seconds = st.number_input("秒", min_value=0.0, step=0.1, value=0.0, format="%.1f")
    
    if st.button("计算新时间", key="calc_add"):
        base_hour, base_minute, base_second = parse_time_input(base_time_str)
        
        if base_hour is not None:
            base_year = base_date.year
            base_month = base_date.month
            base_day = base_date.day
            
            new_year, new_month, new_day, new_hour, new_minute, new_second = add_times(
                base_year, base_month, base_day, base_hour, base_minute, base_second,
                add_years, add_months, add_days, add_hours, add_minutes, add_seconds
            )
            
            # 为新时间计算MJD
            new_mjd = to_mjd(new_year, new_month, new_day, new_hour, new_minute, new_second)
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown(f"### 新时间结果")
            st.markdown(f"**日期和时间：** {new_year}-{new_month:02d}-{new_day:02d} {new_hour:02d}:{new_minute:02d}:{new_second:06.3f}")
            st.markdown(f"**对应MJD：** {new_mjd:.6f}")
            st.markdown('</div>', unsafe_allow_html=True)

# 标签页6: 作业题目
with tab6:
    st.markdown('<div class="sub-header">作业题目计算</div>', unsafe_allow_html=True)
    
    st.markdown("### 计算提前准备的题目")
    
    if st.button("计算所有作业题目"):
        # 作业题目1
        year, month, day = 2025, 3, 12
        mjd_result = to_mjd(year, month, day)
        doy_result = to_doy(year, month, day)
        
        # 作业题目2
        base_year, base_month, base_day = 2025, 3, 12
        base_hour, base_minute, base_second = 8, 18, 58.3
        
        # 添加时间
        add_hours, add_minutes, add_seconds = 112, 39, 30.5
        
        new_year, new_month, new_day, new_hour, new_minute, new_second = add_times(
            base_year, base_month, base_day, base_hour, base_minute, base_second,
            0, 0, 0, add_hours, add_minutes, add_seconds
        )
        
        new_mjd = to_mjd(new_year, new_month, new_day, new_hour, new_minute, new_second)
        
        # 作业题目3
        beijing_year, beijing_month, beijing_day = 2025, 3, 11
        beijing_hour, beijing_minute, beijing_second = 10, 13, 58.8
        
        # 北京时间转UTC（减8小时）
        utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second = add_times(
            beijing_year, beijing_month, beijing_day, beijing_hour, beijing_minute, beijing_second,
            0, 0, 0, -8, 0, 0
        )
        
        gps_week, gps_seconds = to_gps(utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second)
        bds_week, bds_seconds = to_bds(utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second)
        
        # 显示结果
        st.markdown('<div class="homework-container">', unsafe_allow_html=True)
        st.markdown("### 题目1: 计算2025年03月12日对应的MJD和DOY")
        st.markdown(f"**MJD结果:** {mjd_result:.6f}")
        st.markdown(f"**DOY结果:** {doy_result}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="homework-container">', unsafe_allow_html=True)
        st.markdown("### 题目2: 计算2025年03月12日 8时18分58.3秒加112时39分30.5秒的结果")
        st.markdown(f"**原始时间:** 2025-03-12 08:18:58.300")
        st.markdown(f"**添加时间:** 112小时39分钟30.5秒")
        st.markdown(f"**结果时间:** {new_year}-{new_month:02d}-{new_day:02d} {new_hour:02d}:{new_minute:02d}:{new_second:06.3f}")
        st.markdown(f"**对应MJD:** {new_mjd:.6f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="homework-container">', unsafe_allow_html=True)
        st.markdown("### 题目3: 已知北京时间：2025年03月11日 10时13分58.8秒，计算对应的GPS和北斗时间")
        st.markdown(f"**北京时间:** 2025-03-11 10:13:58.800")
        st.markdown(f"**转换为UTC:** {utc_year}-{utc_month:02d}-{utc_day:02d} {utc_hour:02d}:{utc_minute:02d}:{utc_second:06.3f}")
        st.markdown(f"**GPS周:** {gps_week}")
        st.markdown(f"**GPS周内秒:** {gps_seconds:.3f}")
        st.markdown(f"**北斗周:** {bds_week}")
        st.markdown(f"**北斗周内秒:** {bds_seconds:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)

# 侧边栏信息
with st.sidebar:
    st.image("satellite.png", width=100)
    st.markdown("### 关于GNSS时间系统")
    st.markdown("""
    **修正儒略日(MJD)** 是天文学、卫星导航和其他应用中使用的日期格式。它表示自1858年11月17日午夜以来的天数。
    
    **GPS时间** 从1980年1月6日00:00:00 UTC开始。它以周和周内秒表示。
    
    **北斗时间(BDS)** 从2006年1月1日00:00:00 UTC开始。它与GPS时间相差特定的周数。
    
    **年积日(DOY)** 表示一年中的连续日期编号，范围从1到365（闰年为366）。
    """)
    
    st.markdown("### 时间格式说明")
    st.markdown("""
    本应用支持精确的时间输入，包括小数秒：
    - 标准格式：HH:MM:SS.sss
    - 例如：22:10:32.126
    
    注意：在计算北京时间到UTC的转换时，会自动减去8小时。
    """)
    
    st.markdown("### 作业题目")
    st.markdown("""
    1. 计算2025年03月12日对应的MJD，DOY
    2. 计算2025年03月12日 8时18分58.3秒加112时39分30.5秒的结果
    3. 已知北京时间：2025年03月11日 10时13分58.8秒，计算GPS和北斗时间
    """)
    
    st.markdown("### 制作")
    st.markdown("使用Streamlit构建 • 2025")