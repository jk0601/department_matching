import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

def create_visualization(results: Dict[str, Any]) -> str:
    """
    분석 결과를 HTML로 시각화
    
    Args:
        results (Dict[str, Any]): 분석 결과 데이터
        
    Returns:
        str: HTML 콘텐츠
    """
    
    # 1. 막대 차트 생성 (부서별 적합도)
    bar_chart = create_compatibility_bar_chart(results['top_departments'])
    
    # 2. 레이더 차트 생성 (개인 성향 프로필)
    radar_chart = create_personal_profile_radar(results['user_profile'])
    
    # 3. 히트맵 생성 (부서별 요구사항 비교)
    heatmap_chart = create_department_requirements_heatmap(results['top_departments'])
    
    # HTML 템플릿 생성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>부서 매칭 분석 결과</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #ffffff;
                color: #2c2c2c;
                font-size: 13px;
                line-height: 1.6;
            }}
            
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 30px;
                border-radius: 15px;
                border: 1px solid #dee2e6;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #2c2c2c;
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            
            .header .date {{
                color: #6c757d;
                font-size: 12px;
                margin-top: 10px;
            }}
            
            .section {{
                background-color: #ffffff;
                margin: 20px 0;
                padding: 25px;
                border-radius: 12px;
                border: 1px solid #c0c0c0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}
            
            .section h2 {{
                color: #2c2c2c;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
                border-bottom: 2px solid #8e44ad;
                padding-bottom: 8px;
            }}
            
            .dept-card {{
                background-color: #f8f9fa;
                margin: 15px 0;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #8e44ad;
            }}
            
            .dept-name {{
                font-size: 16px;
                font-weight: 600;
                color: #2c2c2c;
                margin-bottom: 5px;
            }}
            
            .dept-score {{
                font-size: 14px;
                color: #8e44ad;
                font-weight: 500;
                margin-bottom: 8px;
            }}
            
            .dept-reason {{
                font-size: 12px;
                color: #4a4a4a;
                line-height: 1.5;
            }}
            
            .chart-container {{
                margin: 20px 0;
                text-align: center;
            }}
            
            .summary {{
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #dee2e6;
                margin-top: 30px;
            }}
            
            .summary h3 {{
                color: #2c2c2c;
                font-size: 16px;
                margin-bottom: 15px;
            }}
            
            .profile-item {{
                display: inline-block;
                margin: 5px 10px;
                padding: 5px 10px;
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #c0c0c0;
                font-size: 11px;
                color: #4a4a4a;
            }}
            
            @media print {{
                body {{ 
                    font-size: 11px; 
                }}
                .section {{ 
                    break-inside: avoid; 
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>부서 매칭 분석 결과</h1>
            <div class="date">생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</div>
        </div>
        
        <div class="section">
            <h2>추천 부서 Top 5</h2>
            {generate_department_list_html(results['top_departments'])}
        </div>
        
        <div class="section">
            <h2>부서별 적합도 비교</h2>
            <div class="chart-container">
                <div id="bar-chart"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>개인 성향 프로필</h2>
            <div class="chart-container">
                <div id="radar-chart"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>부서별 요구사항 분석</h2>
            <div class="chart-container">
                <div id="heatmap-chart"></div>
            </div>
        </div>
        
        <div class="summary">
            <h3>분석 요약</h3>
            <div>
                <strong>MBTI:</strong> {results.get('mbti', '알 수 없음')}
            </div>
            <div style="margin-top: 10px;">
                <strong>개인 성향:</strong><br>
                {generate_profile_summary_html(results['user_profile'])}
            </div>
        </div>
        
        <script>
            {bar_chart}
            {radar_chart}
            {heatmap_chart}
        </script>
    </body>
    </html>
    """
    
    return html_content

def create_compatibility_bar_chart(top_departments: List[Dict]) -> str:
    """부서별 적합도 막대 차트 생성"""
    
    names = [dept['name'] for dept in top_departments]
    scores = [dept['score'] for dept in top_departments]
    
    chart_js = f"""
    var barData = [{{
        x: {names},
        y: {scores},
        type: 'bar',
        marker: {{
            color: ['#8e44ad', '#9b59b6', '#af7ac5', '#c39bd3', '#d7bde2'],
            line: {{
                color: '#6c5077',
                width: 1
            }}
        }},
        text: {[f'{score:.1f}%' for score in scores]},
        textposition: 'auto',
        textfont: {{
            size: 11,
            color: 'white'
        }}
    }}];
    
    var barLayout = {{
        title: {{
            text: '부서별 적합도 점수',
            font: {{ size: 16, color: '#2c2c2c' }}
        }},
        xaxis: {{
            title: '부서',
            titlefont: {{ size: 12, color: '#4a4a4a' }},
            tickfont: {{ size: 10, color: '#4a4a4a' }}
        }},
        yaxis: {{
            title: '적합도 (%)',
            titlefont: {{ size: 12, color: '#4a4a4a' }},
            tickfont: {{ size: 10, color: '#4a4a4a' }},
            range: [0, 100]
        }},
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        margin: {{ l: 60, r: 30, t: 60, b: 80 }},
        height: 400
    }};
    
    Plotly.newPlot('bar-chart', barData, barLayout, {{responsive: true}});
    """
    
    return chart_js

def create_personal_profile_radar(user_profile: Dict[str, float]) -> str:
    """개인 성향 프로필 레이더 차트 생성"""
    
    traits = list(user_profile.keys())
    values = list(user_profile.values())
    
    chart_js = f"""
    var radarData = [{{
        type: 'scatterpolar',
        r: {values},
        theta: {traits},
        fill: 'toself',
        fillcolor: 'rgba(142, 68, 173, 0.3)',
        line: {{
            color: '#8e44ad',
            width: 2
        }},
        marker: {{
            color: '#8e44ad',
            size: 6
        }},
        name: '개인 성향'
    }}];
    
    var radarLayout = {{
        title: {{
            text: '개인 성향 프로필',
            font: {{ size: 16, color: '#2c2c2c' }}
        }},
        polar: {{
            radialaxis: {{
                visible: true,
                range: [0, 100],
                tickfont: {{ size: 10, color: '#4a4a4a' }},
                gridcolor: '#dee2e6'
            }},
            angularaxis: {{
                tickfont: {{ size: 11, color: '#2c2c2c' }}
            }}
        }},
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        margin: {{ l: 80, r: 80, t: 60, b: 60 }},
        height: 450
    }};
    
    Plotly.newPlot('radar-chart', radarData, radarLayout, {{responsive: true}});
    """
    
    return chart_js

def create_department_requirements_heatmap(top_departments: List[Dict]) -> str:
    """부서별 요구사항 히트맵 생성"""
    
    dept_names = [dept['name'] for dept in top_departments]
    requirements = [dept['requirements'] for dept in top_departments]
    
    if not requirements:
        return ""
    
    # 모든 특성 추출
    all_traits = list(requirements[0].keys())
    
    # 히트맵 데이터 구성
    z_values = []
    for req in requirements:
        z_values.append([req.get(trait, 0) for trait in all_traits])
    
    chart_js = f"""
    var heatmapData = [{{
        z: {z_values},
        x: {all_traits},
        y: {dept_names},
        type: 'heatmap',
        colorscale: [
            [0, '#ffffff'],
            [0.5, '#c39bd3'],
            [1, '#8e44ad']
        ],
        showscale: true,
        colorbar: {{
            title: '요구 수준',
            titlefont: {{ size: 11, color: '#4a4a4a' }},
            tickfont: {{ size: 10, color: '#4a4a4a' }}
        }},
        text: {[[f'{val:.0f}' for val in row] for row in z_values]},
        texttemplate: '%{{text}}',
        textfont: {{ size: 10, color: '#2c2c2c' }}
    }}];
    
    var heatmapLayout = {{
        title: {{
            text: '부서별 성향 요구사항',
            font: {{ size: 16, color: '#2c2c2c' }}
        }},
        xaxis: {{
            title: '성향 요소',
            titlefont: {{ size: 12, color: '#4a4a4a' }},
            tickfont: {{ size: 10, color: '#4a4a4a' }},
            tickangle: -45
        }},
        yaxis: {{
            title: '부서',
            titlefont: {{ size: 12, color: '#4a4a4a' }},
            tickfont: {{ size: 10, color: '#4a4a4a' }}
        }},
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        margin: {{ l: 100, r: 60, t: 60, b: 100 }},
        height: 400
    }};
    
    Plotly.newPlot('heatmap-chart', heatmapData, heatmapLayout, {{responsive: true}});
    """
    
    return chart_js

def generate_department_list_html(top_departments: List[Dict]) -> str:
    """추천 부서 목록 HTML 생성"""
    
    html = ""
    for i, dept in enumerate(top_departments, 1):
        html += f"""
        <div class="dept-card">
            <div class="dept-name">{i}. {dept['name']}</div>
            <div class="dept-score">적합도: {dept['score']:.1f}%</div>
            <div class="dept-reason">{dept['reason']}</div>
        </div>
        """
    
    return html

def generate_profile_summary_html(user_profile: Dict[str, float]) -> str:
    """개인 성향 요약 HTML 생성"""
    
    html = ""
    for trait, score in user_profile.items():
        html += f'<span class="profile-item">{trait}: {score:.0f}점</span>'
    
    return html 