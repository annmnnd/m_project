import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 분석 대시보드",
    page_icon="🎬",
    layout="wide"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 4px solid #FF6B6B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로딩 및 전처리 함수
@st.cache_data
def load_and_process_data():
    try:
        # 데이터 로딩
        kobis_df = pd.read_csv('kobis_weekly_2013_2025_enriched.csv')
        tmdb_df = pd.read_csv('tmdb_global_top_2014_2024_N100_with_genres.csv')
        
        # 현재 시점 기준으로 유효한 데이터만 필터링
        current_year = 2024
        kobis_df = kobis_df[kobis_df['year'] <= current_year]
        tmdb_df = tmdb_df[tmdb_df['year'] <= current_year]
        
        # 날짜 전처리
        kobis_df['openDt'] = pd.to_datetime(kobis_df['openDt'], errors='coerce')
        tmdb_df['release_date'] = pd.to_datetime(tmdb_df['release_date'], errors='coerce')
        
        # 이상치 제거
        kobis_df = kobis_df[kobis_df['audiCnt'] >= 0]
        kobis_df = kobis_df[kobis_df['salesAmt'] >= 0]
        tmdb_df = tmdb_df[(tmdb_df['vote_average'] >= 0) & (tmdb_df['vote_average'] <= 10)]
        
        return kobis_df, tmdb_df
    except Exception as e:
        st.error(f"데이터 로딩 오류: {e}")
        return None, None

def create_metric_card(title, value, subtitle=""):
    return f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">{subtitle}</div>
    </div>
    """

def main():
    st.markdown('<h1 class="main-header">🎬 영화 흥행 분석 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로딩
    with st.spinner('🔄 데이터 분석 중...'):
        kobis_df, tmdb_df = load_and_process_data()
    
    if kobis_df is None or tmdb_df is None:
        st.stop()
    
    # 기본 필터링 (최근 3년)
    recent_years = [2022, 2023, 2024]
    kobis_recent = kobis_df[kobis_df['year'].isin(recent_years)]
    tmdb_recent = tmdb_df[tmdb_df['year'].isin(recent_years)]
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 핵심 지표", 
        "🇰🇷 한국 박스오피스", 
        "🌍 글로벌 트렌드", 
        "💡 인사이트 리포트"
    ])
    
    with tab1:
        show_key_metrics(kobis_recent, tmdb_recent)
    
    with tab2:
        show_korean_analysis(kobis_recent)
    
    with tab3:
        show_global_analysis(tmdb_recent)
    
    with tab4:
        show_insights(kobis_recent, tmdb_recent)

def show_key_metrics(kobis_df, tmdb_df):
    st.header("🎯 핵심 성과 지표")
    
    # 주요 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    # 한국 영화 TOP 성과
    top_korean_movie = kobis_df.loc[kobis_df['audiAcc'].idxmax()] if not kobis_df.empty else None
    total_audience = kobis_df['audiAcc'].sum() if not kobis_df.empty else 0
    avg_screen = kobis_df['scrnCnt'].mean() if not kobis_df.empty else 0
    top_rating = tmdb_df['vote_average'].max() if not tmdb_df.empty else 0
    
    with col1:
        st.markdown(create_metric_card(
            "총 누적 관객수", 
            f"{total_audience:,.0f}명",
            "최근 3년 합계"
        ), unsafe_allow_html=True)
    
    with col2:
        if top_korean_movie is not None:
            st.markdown(create_metric_card(
                "최고 흥행작", 
                f"{top_korean_movie['audiAcc']:,.0f}명",
                f"{top_korean_movie['movieNm']}"
            ), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card("최고 흥행작", "데이터 없음"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "평균 상영관 수", 
            f"{avg_screen:.0f}개관",
            "개봉 영화 기준"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "글로벌 최고 평점", 
            f"{top_rating:.1f}/10",
            "TMDB 평점 기준"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 연도별 비교 차트
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 연도별 관객수 변화")
        
        yearly_audience = kobis_df.groupby('year')['audiCnt'].sum().reset_index()
        if not yearly_audience.empty:
            fig = px.bar(yearly_audience, x='year', y='audiCnt',
                        title="연도별 총 관객수",
                        color='audiCnt',
                        color_continuous_scale='Viridis')
            fig.update_layout(
                xaxis_title="연도",
                yaxis_title="총 관객수 (명)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🎭 월별 개봉 패턴")
        
        if 'openDt' in kobis_df.columns and not kobis_df['openDt'].isna().all():
            kobis_df['month'] = kobis_df['openDt'].dt.month
            monthly_releases = kobis_df.groupby('month').size().reset_index(name='count')
            month_names = ['1월', '2월', '3월', '4월', '5월', '6월', 
                          '7월', '8월', '9월', '10월', '11월', '12월']
            monthly_releases['month_name'] = monthly_releases['month'].map(
                {i+1: month_names[i] for i in range(12)}
            )
            
            fig = px.line(monthly_releases, x='month_name', y='count',
                         title="월별 영화 개봉 수",
                         markers=True)
            fig.update_layout(
                xaxis_title="월",
                yaxis_title="개봉 영화 수",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_korean_analysis(kobis_df):
    st.header("🇰🇷 한국 박스오피스 심층 분석")
    
    if kobis_df.empty:
        st.warning("⚠️ 분석할 한국 영화 데이터가 없습니다.")
        return
    
    # 흥행 순위
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 흥행 순위 TOP 10")
        top_movies = kobis_df.nlargest(10, 'audiAcc')[['movieNm', 'audiAcc', 'openDt', 'year']].copy()
        top_movies['순위'] = range(1, len(top_movies) + 1)
        top_movies['누적관객수'] = top_movies['audiAcc'].apply(lambda x: f"{x:,}명")
        top_movies['개봉년도'] = top_movies['year'].astype(int)
        
        display_df = top_movies[['순위', 'movieNm', '누적관객수', '개봉년도']].copy()
        display_df.columns = ['순위', '영화명', '누적관객수', '개봉년도']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 관객수 분포")
        audience_ranges = ['10만 미만', '10만-100만', '100만-500만', '500만-1000만', '1000만 이상']
        audience_counts = [
            len(kobis_df[kobis_df['audiAcc'] < 100000]),
            len(kobis_df[(kobis_df['audiAcc'] >= 100000) & (kobis_df['audiAcc'] < 1000000)]),
            len(kobis_df[(kobis_df['audiAcc'] >= 1000000) & (kobis_df['audiAcc'] < 5000000)]),
            len(kobis_df[(kobis_df['audiAcc'] >= 5000000) & (kobis_df['audiAcc'] < 10000000)]),
            len(kobis_df[kobis_df['audiAcc'] >= 10000000])
        ]
        
        fig = px.pie(values=audience_counts, names=audience_ranges,
                    title="관객수별 영화 분포")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # 장르 분석
    if 'genres' in kobis_df.columns and not kobis_df['genres'].isna().all():
        st.subheader("🎭 장르별 성과 분석")
        
        # 장르 데이터 처리
        genre_data = []
        for _, row in kobis_df.iterrows():
            if pd.notna(row['genres']):
                genres = str(row['genres']).split(',')
                for genre in genres:
                    genre = genre.strip()
                    if genre:  # 빈 문자열 제외
                        genre_data.append({
                            'genre': genre,
                            'audiCnt': row['audiCnt'] if pd.notna(row['audiCnt']) else 0,
                            'salesAmt': row['salesAmt'] if pd.notna(row['salesAmt']) else 0
                        })
        
        if genre_data:
            genre_df = pd.DataFrame(genre_data)
            genre_summary = genre_df.groupby('genre').agg({
                'audiCnt': ['sum', 'mean', 'count'],
                'salesAmt': 'sum'
            }).round(0)
            
            genre_summary.columns = ['총관객수', '평균관객수', '영화수', '총매출']
            genre_summary = genre_summary.sort_values('총관객수', ascending=False).head(8)
            genre_summary = genre_summary.reset_index()
            
            fig = px.bar(genre_summary, x='genre', y='총관객수',
                        title="장르별 총 관객수",
                        color='총관객수',
                        color_continuous_scale='Reds')
            fig.update_layout(xaxis_title="장르", yaxis_title="총 관객수")
            st.plotly_chart(fig, use_container_width=True)

def show_global_analysis(tmdb_df):
    st.header("🌍 글로벌 영화 트렌드")
    
    if tmdb_df.empty:
        st.warning("⚠️ 분석할 글로벌 영화 데이터가 없습니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⭐ 평점 TOP 10")
        top_rated = tmdb_df.nlargest(10, 'vote_average')[['title', 'vote_average', 'vote_count', 'year']].copy()
        top_rated['순위'] = range(1, len(top_rated) + 1)
        top_rated['평점'] = top_rated['vote_average'].round(1)
        top_rated['투표수'] = top_rated['vote_count'].apply(lambda x: f"{x:,}")
        
        display_df = top_rated[['순위', 'title', '평점', '투표수']].copy()
        display_df.columns = ['순위', '영화명', '평점', '투표수']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🔥 인기도 TOP 10")
        top_popular = tmdb_df.nlargest(10, 'popularity')[['title', 'popularity', 'vote_average', 'year']].copy()
        top_popular['순위'] = range(1, len(top_popular) + 1)
        top_popular['인기도'] = top_popular['popularity'].round(1)
        top_popular['평점'] = top_popular['vote_average'].round(1)
        
        display_df = top_popular[['순위', 'title', '인기도', '평점']].copy()
        display_df.columns = ['순위', '영화명', '인기도', '평점']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 언어별 분석
    if 'original_language' in tmdb_df.columns:
        st.subheader("🌐 언어별 영화 분포")
        
        lang_analysis = tmdb_df.groupby('original_language').agg({
            'title': 'count',
            'vote_average': 'mean',
            'popularity': 'mean'
        }).reset_index()
        lang_analysis.columns = ['언어', '영화수', '평균평점', '평균인기도']
        lang_analysis = lang_analysis.sort_values('영화수', ascending=False).head(10)
        
        fig = px.bar(lang_analysis, x='언어', y='영화수',
                    title="언어별 영화 제작 수",
                    color='평균평점',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

def show_insights(kobis_df, tmdb_df):
    st.header("💡 데이터 인사이트 리포트")
    
    # 인사이트 박스들
    insights = []
    
    if not kobis_df.empty:
        # 한국 영화 인사이트
        total_movies = len(kobis_df)
        blockbuster_count = len(kobis_df[kobis_df['audiAcc'] >= 10000000])
        blockbuster_rate = (blockbuster_count / total_movies * 100) if total_movies > 0 else 0
        
        insights.append({
            "title": "🎬 한국 영화 천만 관객 달성률",
            "content": f"최근 3년간 **{blockbuster_rate:.1f}%**의 영화가 천만 관객을 돌파했습니다. "
                      f"총 {total_movies}편 중 {blockbuster_count}편이 메가히트를 기록했네요!"
        })
        
        # 계절성 분석
        if 'openDt' in kobis_df.columns and not kobis_df['openDt'].isna().all():
            kobis_df['month'] = kobis_df['openDt'].dt.month
            summer_movies = len(kobis_df[kobis_df['month'].isin([6, 7, 8])])
            total_with_date = len(kobis_df.dropna(subset=['openDt']))
            summer_rate = (summer_movies / total_with_date * 100) if total_with_date > 0 else 0
            
            insights.append({
                "title": "🌞 여름 시즌 개봉 선호도",
                "content": f"전체 영화의 **{summer_rate:.1f}%**가 여름(6-8월)에 개봉됩니다. "
                          f"여름 휴가철이 영화 산업의 황금기라는 것을 확인할 수 있어요!"
            })
    
    if not tmdb_df.empty:
        # 글로벌 트렌드
        high_rated = len(tmdb_df[tmdb_df['vote_average'] >= 8.0])
        total_tmdb = len(tmdb_df)
        quality_rate = (high_rated / total_tmdb * 100) if total_tmdb > 0 else 0
        
        insights.append({
            "title": "⭐ 글로벌 고품질 영화 비율",
            "content": f"글로벌 상위 영화 중 **{quality_rate:.1f}%**가 8점 이상의 고평점을 받았습니다. "
                      f"품질 경쟁이 점점 치열해지고 있다는 신호네요!"
        })
        
        # 언어 다양성
        if 'original_language' in tmdb_df.columns:
            unique_languages = tmdb_df['original_language'].nunique()
            insights.append({
                "title": "🌍 언어 다양성 확산",
                "content": f"글로벌 차트에 **{unique_languages}개 언어**의 영화가 등장했습니다. "
                          f"더 이상 영어 영화만의 시대가 아니라는 것을 보여주네요!"
            })
    
    # 인사이트 표시
    for i, insight in enumerate(insights):
        st.markdown(f"""
        <div class="insight-box">
            <h4 style="margin-top: 0; color: #FF6B6B;">{insight['title']}</h4>
            <p style="margin-bottom: 0; font-size: 1.1rem;">{insight['content']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 데이터 요약
    st.markdown("---")
    st.subheader("📋 데이터 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🇰🇷 한국 영화 데이터**")
        if not kobis_df.empty:
            st.write(f"• 총 영화 수: **{len(kobis_df):,}편**")
            st.write(f"• 분석 기간: **{kobis_df['year'].min():.0f} - {kobis_df['year'].max():.0f}년**")
            st.write(f"• 총 누적 관객: **{kobis_df['audiAcc'].sum():,.0f}명**")
            st.write(f"• 평균 상영관: **{kobis_df['scrnCnt'].mean():.0f}개**")
        else:
            st.write("데이터 없음")
    
    with col2:
        st.markdown("**🌍 글로벌 영화 데이터**")
        if not tmdb_df.empty:
            st.write(f"• 총 영화 수: **{len(tmdb_df):,}편**")
            st.write(f"• 분석 기간: **{tmdb_df['year'].min():.0f} - {tmdb_df['year'].max():.0f}년**")
            st.write(f"• 평균 평점: **{tmdb_df['vote_average'].mean():.1f}/10**")
            st.write(f"• 평균 인기도: **{tmdb_df['popularity'].mean():.1f}**")
        else:
            st.write("데이터 없음")

if __name__ == "__main__":
    main()