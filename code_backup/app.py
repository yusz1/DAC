import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 设置页面配置
st.set_page_config(page_title="交互式数据分析", layout="wide", initial_sidebar_state="expanded")

# 读取Excel文件
@st.cache_data
def load_data():
    df = pd.read_excel('data/test_data.xlsx')
    return df

def main():
    # 侧边栏设置
    st.sidebar.title("控制面板")
    
    try:
        df = load_data()
        
        # 数据基本信息
        with st.expander("📊 数据基本信息", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"总行数: {len(df)}")
                st.info(f"总列数: {len(df.columns)}")
            with col2:
                st.info(f"数值型列数: {len(df.select_dtypes(include=['float64', 'int64']).columns)}")
                st.info(f"分类型列数: {len(df.select_dtypes(include=['object']).columns)}")
        
        # 数据预览和过滤
        st.subheader("🔍 数据预览与过滤")
        
        # 列选择
        selected_columns = st.multiselect(
            "选择要显示的列：",
            options=df.columns.tolist(),
            default=df.columns.tolist()[:5]
        )
        
        # 行数选择
        n_rows = st.slider("显示行数：", min_value=5, max_value=len(df), value=10)
        
        # 显示筛选后的数据
        st.dataframe(df[selected_columns].head(n_rows))
        
        # 数据分析部分
        st.subheader("📈 数据分析")
        
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            # 图表类型选择
            chart_type = st.selectbox(
                "选择图表类型：",
                ["直方图", "箱线图", "散点图", "折线图", "条形图"]
            )
            
            # 选择要分析的列
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                x_col = st.selectbox("选择 X 轴数据：", numeric_cols)
                
                if chart_type == "散点图":
                    y_col = st.selectbox("选择 Y 轴数据：", numeric_cols)
                
                # 颜色分组（可选）
                categorical_cols = df.select_dtypes(include=['object']).columns
                color_col = st.selectbox("选择分组列（可选）：", ['无'] + list(categorical_cols))
                
        with col2:
            # 根据选择创建相应的图表
            if chart_type == "直方图":
                fig = px.histogram(df, x=x_col, color=None if color_col=='无' else color_col,
                                 title=f"{x_col}的分布")
            elif chart_type == "箱线图":
                fig = px.box(df, y=x_col, color=None if color_col=='无' else color_col,
                           title=f"{x_col}的箱线图")
            elif chart_type == "散点图":
                fig = px.scatter(df, x=x_col, y=y_col, color=None if color_col=='无' else color_col,
                               title=f"{x_col} vs {y_col}")
            elif chart_type == "折线图":
                fig = px.line(df, x=df.index, y=x_col, color=None if color_col=='无' else color_col,
                            title=f"{x_col}的趋势")
            elif chart_type == "条形图":
                fig = px.bar(df, x=df.index, y=x_col, color=None if color_col=='无' else color_col,
                           title=f"{x_col}的条形图")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 数据统计
        st.subheader("📊 数据统计")
        with st.expander("查看统计信息"):
            if len(numeric_cols) > 0:
                selected_col_stats = st.selectbox("选择要统计的列：", numeric_cols)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("平均值", f"{df[selected_col_stats].mean():.2f}")
                with col2:
                    st.metric("中位数", f"{df[selected_col_stats].median():.2f}")
                with col3:
                    st.metric("标准差", f"{df[selected_col_stats].std():.2f}")
                
                st.write("详细统计信息：")
                st.write(df[selected_col_stats].describe())
        
        # 数据下载
        st.subheader("💾 数据导出")
        if st.button("导出当前数据为CSV"):
            csv = df[selected_columns].to_csv(index=False)
            st.download_button(
                label="点击下载",
                data=csv,
                file_name=f'data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
            
    except Exception as e:
        st.error(f"发生错误：{str(e)}")
        
if __name__ == "__main__":
    main()