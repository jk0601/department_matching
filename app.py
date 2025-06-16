import streamlit as st
import pandas as pd
import numpy as np
import openai
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import io
from analysis import DepartmentMatcher
from visualization import create_visualization

# 페이지 설정
st.set_page_config(
    page_title="부서 매칭 통합 분석 시스템",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

    # CSS 스타일링
def load_css():
    st.markdown("""
    <style>
    /* 전체 배경 */
    .main {
        background-color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-width: 700px;
        margin: 0 auto;
    }
    
    .block-container {
        max-width: 700px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* 제목 스타일 */
    .main-title {
        color: #2c2c2c;
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        border: 1px solid #dee2e6;
    }
    
    /* 작은 글꼴 */
    .small-text {
        font-size: 13px;
        color: #4a4a4a;
        margin-bottom: 8px;
    }
    
    /* 알림 메시지 스타일 조정 */
    .stAlert {
        padding: 10px !important;
        margin: 0 !important;
    }
    
    .stAlert [data-testid="stAlertContainer"] {
        padding: 8px 14px !important;
        min-height: auto !important;
        margin: 0 !important;
    }
    
    .stAlert [data-testid="stMarkdownContainer"] {
        margin: 0 !important;
    }
    
    .stAlert [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }
    
    .stAlert [data-testid="stAlertContentSuccess"] {
        padding: 6px 10px !important;
        margin: 0 !important;
    }
    
    .stAlert [data-testid="stAlertContentError"] {
        padding: 6px 10px !important;
        margin: 0 !important;
    }
    
    /* 알림을 감싸는 요소 컨테이너 margin 제거 */
    .stAlert .st-emotion-cache-1ii4qqd {
        margin: 0 !important;
    }
    
    /* 커스텀 성공 메시지 스타일 */
    .custom-success {
        background-color: #d4edda;
        color: #155724;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #c3e6cb;
        font-size: 13px;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 12px;
    }
    
    /* 커스텀 에러 메시지 스타일 */
    .custom-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
        font-size: 13px;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 12px;
    }
    
    /* 보라 그라데이션 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #8e44ad, #9b59b6, #af7ac5);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(142, 68, 173, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7d3c98, #8e44ad, #9b59b6);
        box-shadow: 0 4px 12px rgba(142, 68, 173, 0.4);
        transform: translateY(-1px);
    }
    
    /* 파일 업로더 스타일 */
    .stFileUploader > div {
        background-color: #f8f9fa;
        border: 2px dashed #c0c0c0;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* 선택박스 스타일 */
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border: 1px solid #c0c0c0;
        border-radius: 6px;
        font-size: 13px;
    }
    
    /* 텍스트 입력 스타일 */
    .stTextInput > div > div > input {
        background-color: #f8f9fa;
        border: 1px solid #c0c0c0;
        border-radius: 6px;
        font-size: 13px;
        padding: 8px;
    }
    
    /* 성공 메시지 */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #c3e6cb;
        font-size: 13px;
    }
    
    /* 에러 메시지 */
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
        font-size: 13px;
    }
    
    /* 진행상황 표시 */
    .progress-text {
        color: #6c757d;
        font-size: 12px;
        font-style: italic;
        text-align: center;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    # 메인 제목
    st.markdown('<div class="main-title">부서 매칭 통합 분석 시스템</div>', unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'api_verified' not in st.session_state:
        st.session_state.api_verified = False
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # 1. API 키 인증 섹션
    with st.container(border=True):
        st.markdown("**OpenAI API 키 인증**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            api_key = st.text_input(
                "API 키를 입력하세요",
                type="password",
                placeholder="sk-...",
                label_visibility="collapsed"
            )
        
        with col2:
            auth_clicked = st.button("인증", key="auth_btn")
        
        # 인증 결과 메시지를 컨테이너 안에 표시
        if auth_clicked:
            if api_key:
                try:
                    openai.api_key = api_key
                    # API 키 검증  
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    test_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=1
                    )
                    st.session_state.api_verified = True
                    st.session_state.api_key = api_key
                    st.markdown('<div class="custom-success">API 키가 성공적으로 인증되었습니다!</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="custom-error">API 키 인증 실패: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-error">API 키를 입력해주세요.</div>', unsafe_allow_html=True)
        
        # 기존 인증 상태 표시
        elif st.session_state.get('api_verified', False):
            st.markdown('<div class="custom-success">API 키가 인증되어 있습니다.</div>', unsafe_allow_html=True)
    
    # 2. 파일 업로드 섹션
    if st.session_state.api_verified:
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.markdown("**기업 조직도 AI 분석 파일**")
                dept_file = st.file_uploader(
                    "조직도 분석 CSV 파일을 업로드하세요",
                    type=['csv'],
                    key="dept_upload",
                    label_visibility="collapsed"
                )
        
        with col2:
            with st.container(border=True):
                st.markdown("**개인 디지털 행동 분석 파일**")
                personal_files = st.file_uploader(
                    "디지털 행동 분석 CSV 파일을 업로드하세요 (여러개 가능)",
                    type=['csv'],
                    key="personal_upload",
                    label_visibility="collapsed",
                    accept_multiple_files=True
                )
                if personal_files:
                    st.info(f"총 {len(personal_files)}개 파일이 업로드되었습니다.")
        
        # 3. MBTI 선택 섹션
        with st.container(border=True):
            st.markdown("**MBTI 성격유형 선택**")
            
            mbti_types = [
                "알 수 없음", "INTJ", "INTP", "ENTJ", "ENTP",
                "INFJ", "INFP", "ENFJ", "ENFP",
                "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                "ISTP", "ISFP", "ESTP", "ESFP"
            ]
            
            selected_mbti = st.selectbox(
                "MBTI를 선택하세요 (모르시면 '알 수 없음' 선택)",
                mbti_types,
                index=0,
                label_visibility="collapsed"
            )
        
        # 4. 분석 시작 버튼
        st.markdown('<div style="text-align: center; margin: 30px 0;">', unsafe_allow_html=True)
        
        if dept_file and personal_files:
            if st.button("부서 매칭 분석 시작", key="analyze_btn"):
                with st.spinner('분석 중입니다...'):
                    try:
                        # 데이터 로드
                        dept_df = pd.read_csv(dept_file)
                        
                        # 여러 개인 파일 통합
                        personal_dfs = []
                        file_info = []
                        for pf in personal_files:
                            df = pd.read_csv(pf)
                            df['파일명'] = pf.name  # 파일 출처 추가
                            personal_dfs.append(df)
                            file_info.append(f"{pf.name} ({len(df)}행)")
                        
                        # 파일들을 통합 (세로로 연결)
                        personal_df = pd.concat(personal_dfs, ignore_index=True)
                        
                        # 분석 수행
                        matcher = DepartmentMatcher(st.session_state.api_key)
                        results = matcher.analyze_matching(dept_df, personal_df, selected_mbti)
                        
                        # 결과에 파일 정보 추가
                        results['file_info'] = file_info
                        results['total_data_points'] = len(personal_df)
                        
                        # 결과 저장
                        st.session_state.analysis_results = results
                        st.session_state.analysis_complete = True
                        
                        st.success(f"분석이 완료되었습니다! (총 {len(personal_files)}개 파일, {len(personal_df)}개 데이터 포인트 분석)")
                        
                    except Exception as e:
                        st.markdown(f'<div class="error-message">분석 중 오류가 발생했습니다: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="progress-text">부서 파일과 개인 분석 파일(들)을 모두 업로드해주세요</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 5. 결과 표시 및 다운로드
        if st.session_state.analysis_complete and 'analysis_results' in st.session_state:
            st.markdown("---")
            st.markdown('<div class="main-title">분석 결과</div>', unsafe_allow_html=True)
            
            results = st.session_state.analysis_results
            
            # 결과 표시
            display_results(results)
            
            # HTML 다운로드 버튼
            html_content = create_visualization(results)
            st.download_button(
                label="분석 결과 HTML 다운로드",
                data=html_content,
                file_name=f"department_matching_result.html",
                mime="text/html",
                key="download_btn"
            )

def display_results(results):
    """분석 결과를 화면에 표시"""
    
    # 상위 2개 부서 표시
    with st.container(border=True):
        st.markdown("**추천 부서 Top 2**")
        
        for i, dept in enumerate(results['top_departments'][:2], 1):
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 12px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #8e44ad;">
                <strong style="color: #2c2c2c; font-size: 14px;">{i}. {dept['name']}</strong><br>
                <span style="color: #6c757d; font-size: 12px;">적합도: {dept['score']:.1f}%</span><br>
                <span style="color: #4a4a4a; font-size: 11px;">{dept['reason']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # 적합도 차트
    if 'chart_data' in results:
        with st.container(border=True):
            st.markdown("**부서별 적합도 비교**")
            
            # 데이터 준비
            dept_names = [dept['name'] for dept in results['top_departments'][:2]]
            dept_scores = [dept['score'] for dept in results['top_departments'][:2]]
            
            # 입체감 있는 애니메이션 바 차트 HTML/CSS/JS
            chart_html = f"""
            <div style="padding: 20px;">
                <style>
                .progress-container {{
                    margin: 15px 0;
                    padding: 0;
                }}
                
                .dept-label {{
                    font-size: 13px;
                    font-weight: 600;
                    color: #2c2c2c;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .score-value {{
                    font-size: 14px;
                    font-weight: 700;
                    color: #8e44ad;
                }}
                
                .progress-track {{
                    width: 100%;
                    height: 28px;
                    background: linear-gradient(145deg, #f8f9fa, #e9ecef);
                    border-radius: 14px;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 
                        inset 2px 2px 5px rgba(0,0,0,0.1),
                        inset -2px -2px 5px rgba(255,255,255,0.7);
                    border: 1px solid rgba(0,0,0,0.05);
                }}
                
                .progress-bar {{
                    height: 100%;
                    border-radius: 14px;
                    position: relative;
                    background: linear-gradient(135deg, #8e44ad, #9b59b6, #af7ac5);
                    box-shadow: 
                        2px 2px 8px rgba(142, 68, 173, 0.3),
                        inset 1px 1px 3px rgba(255,255,255,0.3);
                    transition: width 2.5s cubic-bezier(0.4, 0, 0.2, 1);
                    width: 0%;
                    overflow: hidden;
                }}
                
                .progress-bar::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, 
                        transparent, 
                        rgba(255,255,255,0.4), 
                        transparent
                    );
                    animation: shine 3s infinite;
                }}
                
                .progress-bar.high-score {{
                    background: linear-gradient(135deg, #27ae60, #2ecc71, #58d68d);
                    box-shadow: 
                        2px 2px 8px rgba(46, 204, 113, 0.3),
                        inset 1px 1px 3px rgba(255,255,255,0.3);
                }}
                
                .progress-bar.medium-score {{
                    background: linear-gradient(135deg, #f39c12, #e67e22, #f4d03f);
                    box-shadow: 
                        2px 2px 8px rgba(243, 156, 18, 0.3),
                        inset 1px 1px 3px rgba(255,255,255,0.3);
                }}
                
                .progress-bar.low-score {{
                    background: linear-gradient(135deg, #e74c3c, #c0392b, #ec7063);
                    box-shadow: 
                        2px 2px 8px rgba(231, 76, 60, 0.3),
                        inset 1px 1px 3px rgba(255,255,255,0.3);
                }}
                
                @keyframes shine {{
                    0% {{ left: -100%; }}
                    50% {{ left: 100%; }}
                    100% {{ left: 100%; }}
                }}
                
                .progress-text {{
                    position: absolute;
                    top: 50%;
                    right: 12px;
                    transform: translateY(-50%);
                    color: white;
                    font-size: 11px;
                    font-weight: 700;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                    opacity: 0;
                    transition: opacity 1s ease-in-out 1.5s;
                }}
                
                .progress-text.show {{
                    opacity: 1;
                }}
                
                .chart-title {{
                    text-align: center;
                    font-size: 16px;
                    font-weight: 600;
                    color: #2c2c2c;
                    margin-bottom: 25px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #e9ecef;
                }}
                </style>
                
                <div class="chart-title">부서별 적합도 분석</div>
                
                <div id="progress-chart">
            """
            
            # 각 부서별 진행 바 생성
            for i, (name, score) in enumerate(zip(dept_names, dept_scores)):
                score_class = "high-score" if score >= 80 else "medium-score" if score >= 60 else "low-score"
                
                chart_html += f"""
                <div class="progress-container">
                    <div class="dept-label">
                        <span>{i+1}. {name}</span>
                        <span class="score-value" id="score-{i}">0%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-bar {score_class}" id="bar-{i}" data-score="{score:.1f}">
                            <div class="progress-text" id="text-{i}">{score:.1f}%</div>
                        </div>
                    </div>
                </div>
                """
            
            chart_html += """
                </div>
                
                <script>
                // 페이지 로드 후 애니메이션 시작
                setTimeout(() => {
                    const bars = document.querySelectorAll('.progress-bar');
                    bars.forEach((bar, index) => {
                        const score = parseFloat(bar.dataset.score);
                        const scoreElement = document.getElementById(`score-${index}`);
                        const textElement = document.getElementById(`text-${index}`);
                        
                        // 바 애니메이션
                        setTimeout(() => {
                            bar.style.width = score + '%';
                        }, index * 200);
                        
                        // 숫자 카운트 애니메이션
                        setTimeout(() => {
                            let currentScore = 0;
                            const increment = score / 50; // 50단계로 나누어 애니메이션
                            const timer = setInterval(() => {
                                currentScore += increment;
                                if (currentScore >= score) {
                                    currentScore = score;
                                    clearInterval(timer);
                                    textElement.classList.add('show');
                                }
                                scoreElement.textContent = currentScore.toFixed(1) + '%';
                            }, 50);
                        }, index * 200 + 500);
                    });
                }, 500);
                </script>
            </div>
            """
            
            # HTML 렌더링
            st.components.v1.html(chart_html, height=250)

if __name__ == "__main__":
    main() 