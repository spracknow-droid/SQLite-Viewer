import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="SQLite Viewer", layout="wide")

st.title("📊 SQLite Table & View Explorer")

# 1. 파일 업로드
uploaded_file = st.sidebar.file_uploader("SQLite DB 파일을 업로드하세요", type=["db", "sqlite", "sqlite3"])

if uploaded_file is not None:
    # 임시 파일 저장 혹은 직접 연결 (sqlite3는 파일 경로가 필요함)
    with open("temp.db", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    conn = sqlite3.connect("temp.db")
    
    # 2. 테이블과 뷰 목록을 한꺼번에 가져오는 쿼리
    # type IN ('table', 'view')를 사용하여 둘 다 추출합니다.
    query = "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%';"
    objects_df = pd.read_sql(query, conn)

    if not objects_df.empty:
        # 사이드바에서 선택 (테이블인지 뷰인지 표시)
        objects_df['display_name'] = objects_df.apply(lambda x: f"[{x['type'].upper()}] {x['name']}", axis=1)
        
        selected_display = st.sidebar.selectbox("항목 선택", objects_df['display_name'])
        selected_name = objects_df[objects_df['display_name'] == selected_display]['name'].values[0]
        selected_type = objects_df[objects_df['display_name'] == selected_display]['type'].values[0]

        st.subheader(f"📍 {selected_type.capitalize()}: {selected_name}")

        # 3. 데이터 불러오기
        try:
            data_df = pd.read_sql(f"SELECT * FROM {selected_name}", conn)
            
            # 데이터 요약 정보 (행/열 개수)
            st.caption(f"Total Rows: {data_df.shape[0]} | Total Columns: {data_df.shape[1]}")
            
            # 데이터 표 출력
            st.dataframe(data_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    else:
        st.warning("DB 내에 테이블이나 뷰가 존재하지 않습니다.")
    
    conn.close()
else:
    st.info("왼쪽 사이드바에서 SQLite DB 파일을 업로드해 주세요.")
