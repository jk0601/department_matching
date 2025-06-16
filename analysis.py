import pandas as pd
import numpy as np
import openai
from typing import Dict, List, Any
import json
import time

class DepartmentMatcher:
    def __init__(self, api_key: str):
        """
        부서 매칭 분석기 초기화
        
        Args:
            api_key (str): OpenAI API 키
        """
        self.api_key = api_key
        openai.api_key = api_key
        
        # MBTI별 특성 정의
        self.mbti_traits = {
            "INTJ": {"분석력": 90, "독립성": 85, "계획성": 90, "창의성": 75, "소통력": 40, "협력성": 50, "실행력": 80, "안정성": 70},
            "INTP": {"분석력": 95, "독립성": 90, "계획성": 60, "창의성": 90, "소통력": 35, "협력성": 45, "실행력": 65, "안정성": 60},
            "ENTJ": {"분석력": 80, "독립성": 70, "계획성": 85, "창의성": 70, "소통력": 80, "협력성": 75, "실행력": 95, "안정성": 75},
            "ENTP": {"분석력": 75, "독립성": 75, "계획성": 50, "창의성": 95, "소통력": 85, "협력성": 70, "실행력": 70, "안정성": 40},
            "INFJ": {"분석력": 75, "독립성": 70, "계획성": 80, "창의성": 80, "소통력": 70, "협력성": 85, "실행력": 75, "안정성": 80},
            "INFP": {"분석력": 70, "독립성": 85, "계획성": 50, "창의성": 90, "소통력": 60, "협력성": 80, "실행력": 60, "안정성": 70},
            "ENFJ": {"분석력": 65, "독립성": 50, "계획성": 75, "창의성": 75, "소통력": 95, "협력성": 95, "실행력": 85, "안정성": 75},
            "ENFP": {"분석력": 60, "독립성": 70, "계획성": 40, "창의성": 95, "소통력": 90, "협력성": 85, "실행력": 70, "안정성": 50},
            "ISTJ": {"분석력": 70, "독립성": 75, "계획성": 95, "창의성": 40, "소통력": 50, "협력성": 70, "실행력": 90, "안정성": 95},
            "ISFJ": {"분석력": 65, "독립성": 60, "계획성": 85, "창의성": 50, "소통력": 75, "협력성": 90, "실행력": 80, "안정성": 90},
            "ESTJ": {"분석력": 75, "독립성": 60, "계획성": 90, "창의성": 45, "소통력": 80, "협력성": 75, "실행력": 95, "안정성": 85},
            "ESFJ": {"분석력": 60, "독립성": 40, "계획성": 80, "창의성": 55, "소통력": 90, "협력성": 95, "실행력": 85, "안정성": 80},
            "ISTP": {"분석력": 85, "독립성": 95, "계획성": 60, "창의성": 75, "소통력": 30, "협력성": 40, "실행력": 85, "안정성": 70},
            "ISFP": {"분석력": 60, "독립성": 80, "계획성": 50, "창의성": 85, "소통력": 55, "협력성": 75, "실행력": 65, "안정성": 75},
            "ESTP": {"분석력": 55, "독립성": 70, "계획성": 35, "창의성": 70, "소통력": 85, "협력성": 70, "실행력": 90, "안정성": 45},
            "ESFP": {"분석력": 45, "독립성": 60, "계획성": 30, "창의성": 80, "소통력": 95, "협력성": 85, "실행력": 75, "안정성": 50}
        }

    def analyze_digital_behavior(self, personal_df: pd.DataFrame) -> Dict[str, float]:
        """
        개인의 디지털 행동 패턴을 분석하여 성향 점수를 계산
        
        Args:
            personal_df (pd.DataFrame): 개인 디지털 행동 분석 데이터 (여러 파일 통합 가능)
            
        Returns:
            Dict[str, float]: 성향별 점수
        """
        try:
            behavior_scores = {
                "분석력": 50, "독립성": 50, "계획성": 50, "창의성": 50,
                "소통력": 50, "협력성": 50, "실행력": 50, "안정성": 50
            }
            
            # 데이터프레임의 컬럼을 분석하여 점수 조정
            if not personal_df.empty:
                columns = personal_df.columns.tolist()
                print(f"분석 중인 컬럼들: {columns}")  # 디버깅용
                print(f"데이터 행 수: {len(personal_df)}")  # 디버깅용
                
                # 여러 파일이 통합된 경우를 고려한 가중치 계산
                total_rows = len(personal_df)
                
                # 웹사이트 방문 패턴 분석 - 더 다양한 컬럼명 지원
                interest_columns = ['관심사', 'category', '카테고리', 'interest', 'interests']
                interest_col = None
                for col in interest_columns:
                    if col in columns:
                        interest_col = col
                        break
                
                if interest_col:
                    print(f"관심사 컬럼 발견: {interest_col}")  # 디버깅용
                    categories = personal_df[interest_col].tolist()
                    
                    # 카테고리별 빈도 및 사용시간 가중치 계산
                    category_scores = {}
                    time_weights = {}
                    
                    # 사용시간도 함께 고려
                    time_col = None
                    time_columns = ['사용시간', 'usage_time', '시간', 'time']
                    for col in time_columns:
                        if col in columns:
                            time_col = col
                            break
                    
                    for i, category in enumerate(categories):
                        category_str = str(category).lower()
                        
                        # 사용시간 가져오기
                        time_weight = 1.0
                        if time_col and i < len(personal_df):
                            try:
                                time_value = float(personal_df.iloc[i][time_col])
                                time_weight = min(time_value / 5.0, 3.0)  # 5시간 기준, 최대 3배 가중
                            except:
                                time_weight = 1.0
                        
                        # 카테고리별 분류 및 가중치 적용
                        if any(keyword in category_str for keyword in ['tech', '기술', 'programming', '개발', 'work', '업무']):
                            category_scores['tech'] = category_scores.get('tech', 0) + time_weight
                        elif any(keyword in category_str for keyword in ['social', '소셜', 'community', '커뮤니티']):
                            category_scores['social'] = category_scores.get('social', 0) + time_weight
                        elif any(keyword in category_str for keyword in ['news', '뉴스', 'finance', '금융']):
                            category_scores['news'] = category_scores.get('news', 0) + time_weight
                        elif any(keyword in category_str for keyword in ['art', '예술', 'design', '디자인']):
                            category_scores['art'] = category_scores.get('art', 0) + time_weight
                        elif any(keyword in category_str for keyword in ['education', '학습', '교육', 'learning']):
                            category_scores['education'] = category_scores.get('education', 0) + time_weight
                        elif any(keyword in category_str for keyword in ['shopping', '쇼핑', 'commerce']):
                            category_scores['shopping'] = category_scores.get('shopping', 0) + time_weight
                        elif any(keyword in category_str for keyword in ['game', '게임', 'entertainment', '엔터']):
                            category_scores['entertainment'] = category_scores.get('entertainment', 0) + time_weight
                    
                    print(f"카테고리 점수: {category_scores}")  # 디버깅용
                    
                    # 총 가중치 계산
                    total_weight = sum(category_scores.values()) or 1
                    
                    # 카테고리별 점수 조정 (비율 기반)
                    for cat_type, score in category_scores.items():
                        influence = min((score / total_weight) * 100, 40)  # 최대 40점까지 영향
                        
                        if cat_type == 'tech':
                            behavior_scores["분석력"] += influence * 0.6
                            behavior_scores["창의성"] += influence * 0.4
                            behavior_scores["독립성"] += influence * 0.3
                        elif cat_type == 'social':
                            behavior_scores["소통력"] += influence * 0.8
                            behavior_scores["협력성"] += influence * 0.6
                        elif cat_type == 'news':
                            behavior_scores["분석력"] += influence * 0.4
                            behavior_scores["안정성"] += influence * 0.6
                            behavior_scores["계획성"] += influence * 0.3
                        elif cat_type == 'art':
                            behavior_scores["창의성"] += influence * 0.8
                            behavior_scores["독립성"] += influence * 0.5
                        elif cat_type == 'education':
                            behavior_scores["분석력"] += influence * 0.5
                            behavior_scores["계획성"] += influence * 0.6
                            behavior_scores["안정성"] += influence * 0.3
                        elif cat_type == 'shopping':
                            behavior_scores["계획성"] += influence * 0.4
                            behavior_scores["실행력"] += influence * 0.3
                        elif cat_type == 'entertainment':
                            behavior_scores["창의성"] += influence * 0.4
                            behavior_scores["소통력"] += influence * 0.3
                
                # 전체적인 사용 패턴 분석
                if time_col:
                    usage_times = personal_df[time_col].tolist()
                    valid_times = []
                    for time_val in usage_times:
                        try:
                            valid_times.append(float(time_val))
                        except:
                            continue
                    
                    if valid_times:
                        avg_usage = np.mean(valid_times)
                        total_usage = sum(valid_times)
                        
                        print(f"평균 사용시간: {avg_usage:.2f}시간, 총 사용시간: {total_usage:.2f}시간")  # 디버깅용
                        
                        # 사용 패턴에 따른 추가 점수
                        if avg_usage > 6:  # 고사용자
                            behavior_scores["실행력"] += 20
                            behavior_scores["독립성"] += 15
                        elif avg_usage > 3:  # 중간 사용자
                            behavior_scores["계획성"] += 15
                            behavior_scores["안정성"] += 10
                        else:  # 저사용자
                            behavior_scores["협력성"] += 15
                            behavior_scores["소통력"] += 10
                        
                        # 총 사용시간이 많으면 실행력 추가 보너스
                        if total_usage > 20:
                            behavior_scores["실행력"] += 10
            
            # 점수를 0-100 범위로 제한
            for key in behavior_scores:
                behavior_scores[key] = min(100, max(0, behavior_scores[key]))
                
            return behavior_scores
            
        except Exception as e:
            print(f"디지털 행동 분석 중 오류: {e}")
            return {
                "분석력": 50, "독립성": 50, "계획성": 50, "창의성": 50,
                "소통력": 50, "협력성": 50, "실행력": 50, "안정성": 50
            }

    def calculate_department_compatibility(self, user_profile: Dict[str, float], dept_requirements: Dict[str, float]) -> float:
        """
        사용자 프로필과 부서 요구사항 간의 적합도를 계산
        
        Args:
            user_profile (Dict[str, float]): 사용자 성향 프로필
            dept_requirements (Dict[str, float]): 부서별 요구 성향
            
        Returns:
            float: 적합도 점수 (0-100)
        """
        try:
            compatibility_score = 0
            total_weight = 0
            penalty_score = 0
            
            print(f"사용자 프로필: {user_profile}")  # 디버깅용
            print(f"부서 요구사항: {dept_requirements}")  # 디버깅용
            
            for trait, user_score in user_profile.items():
                if trait in dept_requirements:
                    dept_requirement = dept_requirements[trait]
                    
                    # 차이 계산
                    difference = abs(user_score - dept_requirement)
                    
                    # 부족한 경우와 초과한 경우 다르게 처리
                    if user_score < dept_requirement:
                        # 부족한 경우 더 큰 페널티
                        trait_score = max(0, 100 - difference * 1.2)
                    else:
                        # 초과한 경우 적은 페널티
                        trait_score = max(0, 100 - difference * 0.8)
                    
                    # 가중치 계산 (부서별 중요도)
                    weight = (dept_requirement / 100) * 1.5  # 가중치 강화
                    
                    # 핵심 역량에 대한 추가 가중치
                    if dept_requirement >= 85:  # 매우 중요한 역량
                        weight *= 1.3
                    elif dept_requirement >= 75:  # 중요한 역량
                        weight *= 1.1
                    
                    compatibility_score += trait_score * weight
                    total_weight += weight
                    
                    # 큰 차이가 나는 핵심 역량에 대한 페널티
                    if dept_requirement >= 80 and difference > 25:
                        penalty_score += difference * 0.3
            
            if total_weight > 0:
                final_score = (compatibility_score / total_weight) - penalty_score
            else:
                final_score = 50
            
            # 최종 점수를 0-100 범위로 제한하고 소수점 반올림
            final_score = min(100, max(0, final_score))
            final_score = round(final_score, 1)  # 소수점 1자리로 반올림
            
            print(f"최종 적합도: {final_score:.1f}%")  # 디버깅용
            
            return final_score
            
        except Exception as e:
            print(f"적합도 계산 중 오류: {e}")
            return 50.0

    def generate_department_analysis(self, user_profile: Dict[str, float], dept_name: str, 
                                   compatibility_score: float, mbti: str) -> str:
        """
        GPT를 이용한 부서 배치 사유 분석 생성
        
        Args:
            user_profile (Dict[str, float]): 사용자 성향 프로필
            dept_name (str): 부서명
            compatibility_score (float): 적합도 점수
            mbti (str): MBTI 유형
            
        Returns:
            str: 배치 사유 분석
        """
        try:
            prompt = f"""
            다음 정보를 바탕으로 개인이 {dept_name} 부서에 적합한 이유를 2-3문장으로 간결하게 설명해주세요.
            
            개인 성향:
            - 분석력: {user_profile.get('분석력', 50)}/100
            - 창의성: {user_profile.get('창의성', 50)}/100
            - 소통력: {user_profile.get('소통력', 50)}/100
            - 협력성: {user_profile.get('협력성', 50)}/100
            - 실행력: {user_profile.get('실행력', 50)}/100
            - 계획성: {user_profile.get('계획성', 50)}/100
            - MBTI: {mbti}
            
            적합도 점수: {compatibility_score:.1f}%
            
            설명은 개인의 강점과 부서의 특성을 연결하여 작성해주세요.
            """
            
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 인사 전문가입니다. 개인의 성향과 부서 특성을 분석하여 간결하고 전문적인 배치 사유를 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"GPT 분석 생성 중 오류: {e}")
            return f"{dept_name} 부서의 업무 특성과 개인의 성향이 {compatibility_score:.1f}% 일치하여 효과적인 업무 수행이 가능할 것으로 예상됩니다."

    def analyze_matching(self, dept_df: pd.DataFrame, personal_df: pd.DataFrame, mbti: str) -> Dict[str, Any]:
        """
        종합적인 부서 매칭 분석 수행
        
        Args:
            dept_df (pd.DataFrame): 부서 분석 데이터
            personal_df (pd.DataFrame): 개인 분석 데이터
            mbti (str): MBTI 유형
            
        Returns:
            Dict[str, Any]: 분석 결과
        """
        try:
            # 1. 개인 성향 프로필 생성
            digital_behavior_scores = self.analyze_digital_behavior(personal_df)
            print(f"디지털 행동 점수: {digital_behavior_scores}")  # 디버깅용
            
            # MBTI 점수와 디지털 행동 점수 가중 평균
            if mbti != "알 수 없음" and mbti in self.mbti_traits:
                mbti_scores = self.mbti_traits[mbti]
                print(f"MBTI ({mbti}) 점수: {mbti_scores}")  # 디버깅용
                # MBTI 70%, 디지털 행동 30% 가중치
                user_profile = {}
                for trait in mbti_scores:
                    combined_score = (mbti_scores[trait] * 0.7 + digital_behavior_scores[trait] * 0.3)
                    user_profile[trait] = round(combined_score, 1)  # 소수점 1자리로 반올림
            else:
                user_profile = {k: round(v, 1) for k, v in digital_behavior_scores.items()}
            
            print(f"최종 사용자 프로필: {user_profile}")  # 디버깅용
            
            # 2. 부서별 적합도 계산
            department_scores = []
            
            for _, dept_row in dept_df.iterrows():
                # 부서명과 하위부서명 추출
                dept_name = dept_row.get('부서명', dept_row.get('department', '알 수 없는 부서'))
                subdept_name = dept_row.get('하위부서명', dept_row.get('subdepartment', ''))
                
                # 전체 부서명 생성 (하위부서가 있으면 결합)
                if subdept_name and str(subdept_name).strip() and str(subdept_name) != 'nan':
                    full_dept_name = f"{dept_name} - {subdept_name}"
                    display_name = full_dept_name
                else:
                    full_dept_name = dept_name
                    display_name = dept_name
                
                print(f"분석 중인 부서: {display_name}")  # 디버깅용
                
                # 부서별 요구 성향 (하위부서 고려)
                dept_requirements = self._get_department_requirements_with_subdept(dept_name, subdept_name)
                
                # 적합도 계산
                compatibility_score = self.calculate_department_compatibility(user_profile, dept_requirements)
                
                # GPT 분석 생성
                analysis = self.generate_department_analysis(user_profile, display_name, compatibility_score, mbti)
                
                department_scores.append({
                    'name': display_name,
                    'full_name': full_dept_name,
                    'main_dept': dept_name,
                    'sub_dept': subdept_name,
                    'score': compatibility_score,
                    'reason': analysis,
                    'requirements': dept_requirements
                })
                
                # API 호출 제한을 위한 짧은 지연
                time.sleep(0.5)
            
            # 3. 점수순으로 정렬
            department_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # 모든 부서 점수 출력 (디버깅용)
            print("\n=== 모든 부서별 적합도 점수 ===")
            for i, dept in enumerate(department_scores, 1):
                print(f"{i}. {dept['name']}: {dept['score']:.2f}%")
            print("===========================\n")
            
            # 4. 결과 반환
            return {
                'user_profile': user_profile,
                'top_departments': department_scores[:2],
                'all_departments': department_scores,
                'mbti': mbti,
                'chart_data': self._prepare_chart_data(department_scores[:2])
            }
            
        except Exception as e:
            print(f"매칭 분석 중 오류: {e}")
            raise e

    def _get_department_requirements_with_subdept(self, dept_name: str, subdept_name: str = "") -> Dict[str, float]:
        """
        부서와 하위부서를 고려한 요구 성향 반환
        """
        print(f"부서명: '{dept_name}', 하위부서: '{subdept_name}'")  # 디버깅용
        
        # 기본 부서 요구사항
        base_requirements = self._get_department_requirements(dept_name)
        
        # 하위부서가 있으면 추가 조정
        if subdept_name and str(subdept_name).strip() and str(subdept_name) != 'nan':
            adjusted_requirements = base_requirements.copy()
            
            # 하위부서별 특성 조정
            subdept_lower = str(subdept_name).lower()
            
            # 개발 관련 하위부서
            if any(keyword in subdept_lower for keyword in ['frontend', '프론트엔드', 'ui', 'ux']):
                adjusted_requirements["창의성"] = min(95, adjusted_requirements["창의성"] + 10)
                adjusted_requirements["소통력"] = min(95, adjusted_requirements["소통력"] + 5)
            elif any(keyword in subdept_lower for keyword in ['backend', '백엔드', 'server', '서버']):
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 10)
                adjusted_requirements["안정성"] = min(95, adjusted_requirements["안정성"] + 5)
            elif any(keyword in subdept_lower for keyword in ['devops', '데브옵스', 'infra', '인프라']):
                adjusted_requirements["안정성"] = min(95, adjusted_requirements["안정성"] + 15)
                adjusted_requirements["계획성"] = min(95, adjusted_requirements["계획성"] + 10)
            elif any(keyword in subdept_lower for keyword in ['ai', '인공지능', 'ml', '머신러닝', 'data', '데이터']):
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 15)
                adjusted_requirements["창의성"] = min(95, adjusted_requirements["창의성"] + 5)
            
            # 마케팅 관련 하위부서
            elif any(keyword in subdept_lower for keyword in ['digital', '디지털', 'online', '온라인']):
                adjusted_requirements["창의성"] = min(95, adjusted_requirements["창의성"] + 10)
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 5)
            elif any(keyword in subdept_lower for keyword in ['brand', '브랜드', 'pr', '홍보']):
                adjusted_requirements["창의성"] = min(95, adjusted_requirements["창의성"] + 15)
                adjusted_requirements["소통력"] = min(95, adjusted_requirements["소통력"] + 5)
            elif any(keyword in subdept_lower for keyword in ['performance', '퍼포먼스', 'growth', '그로스']):
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 10)
                adjusted_requirements["실행력"] = min(95, adjusted_requirements["실행력"] + 10)
            
            # 영업 관련 하위부서
            elif any(keyword in subdept_lower for keyword in ['b2b', 'enterprise', '기업']):
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 5)
                adjusted_requirements["계획성"] = min(95, adjusted_requirements["계획성"] + 10)
            elif any(keyword in subdept_lower for keyword in ['b2c', 'consumer', '소비자']):
                adjusted_requirements["소통력"] = min(95, adjusted_requirements["소통력"] + 10)
                adjusted_requirements["창의성"] = min(95, adjusted_requirements["창의성"] + 5)
            
            # 기획 관련 하위부서
            elif any(keyword in subdept_lower for keyword in ['product', '상품', 'service', '서비스']):
                adjusted_requirements["창의성"] = min(95, adjusted_requirements["창의성"] + 10)
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 5)
            elif any(keyword in subdept_lower for keyword in ['strategy', '전략', 'business', '사업']):
                adjusted_requirements["분석력"] = min(95, adjusted_requirements["분석력"] + 10)
                adjusted_requirements["계획성"] = min(95, adjusted_requirements["계획성"] + 10)
            
            # 랜덤 요소 추가 (하위부서명 기반)
            import random
            random.seed(hash(f"{dept_name}_{subdept_name}") % 1000)
            
            # 각 능력치에 -3~+3 범위의 랜덤 조정
            for trait in adjusted_requirements:
                adjustment = random.randint(-3, 3)
                adjusted_requirements[trait] = max(40, min(100, adjusted_requirements[trait] + adjustment))
            
            print(f"하위부서 조정 후 요구사항: {adjusted_requirements}")
            return adjusted_requirements
        
        return base_requirements

    def _get_department_requirements(self, dept_name: str) -> Dict[str, float]:
        """
        부서별 요구 성향 반환 (예시 데이터)
        실제로는 CSV 파일에서 가져와야 함
        """
        print(f"부서명 조회: '{dept_name}'")  # 디버깅용
        
        dept_requirements = {
            "개발팀": {"분석력": 90, "창의성": 80, "독립성": 85, "실행력": 85, "계획성": 75, "소통력": 60, "협력성": 70, "안정성": 70},
            "마케팅팀": {"소통력": 90, "창의성": 85, "협력성": 80, "실행력": 80, "분석력": 70, "계획성": 75, "독립성": 60, "안정성": 65},
            "인사팀": {"소통력": 95, "협력성": 90, "안정성": 85, "계획성": 80, "분석력": 75, "실행력": 75, "창의성": 60, "독립성": 50},
            "재무팀": {"분석력": 95, "계획성": 90, "안정성": 90, "실행력": 80, "독립성": 70, "소통력": 60, "협력성": 65, "창의성": 45},
            "영업팀": {"소통력": 95, "실행력": 90, "협력성": 85, "창의성": 75, "분석력": 70, "계획성": 70, "독립성": 60, "안정성": 60},
            "기획팀": {"분석력": 85, "계획성": 90, "창의성": 85, "소통력": 80, "협력성": 80, "실행력": 80, "독립성": 70, "안정성": 75},
            "디자인팀": {"창의성": 95, "독립성": 80, "분석력": 70, "실행력": 75, "소통력": 70, "협력성": 70, "계획성": 65, "안정성": 60},
            "고객서비스팀": {"소통력": 95, "협력성": 90, "안정성": 85, "실행력": 80, "계획성": 75, "분석력": 65, "창의성": 60, "독립성": 45}
        }
        
        # 부서명 정확히 매칭되는지 확인
        if dept_name in dept_requirements:
            print(f"부서 매칭 성공: {dept_name}")
            return dept_requirements[dept_name]
        else:
            # 유사한 부서명 찾기
            for key in dept_requirements.keys():
                if key in dept_name or dept_name in key:
                    print(f"유사 부서 매칭: '{dept_name}' -> '{key}'")
                    return dept_requirements[key]
            
            print(f"부서 매칭 실패, 기본값 사용: {dept_name}")
            # 다양한 기본값 설정으로 차별화
            import random
            random.seed(hash(dept_name) % 1000)  # 부서명으로 시드 설정하여 일관성 유지
            
            base_scores = {}
            for trait in ["분석력", "창의성", "독립성", "실행력", "계획성", "소통력", "협력성", "안정성"]:
                base_scores[trait] = random.randint(60, 85)  # 60-85 범위에서 랜덤
            
            return base_scores

    def _prepare_chart_data(self, top_departments: List[Dict]) -> Dict[str, Any]:
        """차트 생성을 위한 데이터 준비"""
        return {
            'names': [dept['name'] for dept in top_departments],
            'scores': [dept['score'] for dept in top_departments],
            'requirements': [dept['requirements'] for dept in top_departments]
        } 