import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import japanize_matplotlib

# --- 関数定義 (ここは変更なし) ---

def create_correlation_network(df, threshold):
    numeric_df = df.select_dtypes(include=np.number)
    corr_matrix = numeric_df.corr()
    G = nx.Graph()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > threshold:
                G.add_edge(corr_matrix.columns[i], corr_matrix.columns[j], 
                           weight=abs(corr_value), sign=np.sign(corr_value))
    return G

def draw_graph(G, threshold):
    if not G or not G.nodes():
        st.warning("閾値を超える相関が見つかりませんでした。閾値を下げてみてください。")
        return None
    fig, ax = plt.subplots(figsize=(16, 16))
    pos = nx.spring_layout(G, k=0.8, seed=42)
    weights = [G[u][v]['weight'] * 5 for u, v in G.edges()]
    edge_colors = ['red' if G[u][v]['sign'] > 0 else 'blue' for u, v in G.edges()]
    nx.draw_networkx(
        G, pos, ax=ax, with_labels=True, node_color='skyblue', node_size=3000, 
        font_size=14, font_family='IPAexGothic', width=weights, edge_color=edge_colors
    )
    ax.set_title(f'相関ネットワーク (閾値: {threshold:.2f})', fontsize=20)
    ax.text(0.01, 0.01, '赤線: 正の相関 / 青線: 負の相関', transform=ax.transAxes, fontsize=14, verticalalignment='bottom')
    return fig

# --- ▼▼▼ ここから前処理関数を追加 ▼▼▼ ---

def preprocess_data(df, chars_to_remove):
    """
    指定された文字を削除し、列を数値に変換する関数
    """
    df_processed = df.copy()
    for col in df_processed.columns:
        # 列が文字列型の場合のみ処理
        if df_processed[col].dtype == 'object':
            # 指定された文字をすべて削除
            for char in chars_to_remove:
                df_processed[col] = df_processed[col].str.replace(char, '', regex=False)
            
            # 文字列から数値に変換を試みる
            # 変換できないものはNaN(欠損値)にする
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
            
    return df_processed

# --- Streamlit アプリケーションのUI部分 ---

st.set_page_config(layout="wide") 
st.title('相関ネットワーク分析アプリ 📊')
st.write('CSVファイルをアップロードすると、データ間の相関関係をネットワークグラフとして可視化します。')

st.sidebar.header('⚙️ 設定')

uploaded_file = st.sidebar.file_uploader(
    "分析したいCSVファイルをアップロード", type='csv'
)

# --- ▼▼▼ ここから前処理のUIを追加 ▼▼▼ ---
st.sidebar.markdown("---") # 区切り線
enable_preprocessing = st.sidebar.checkbox('前処理機能を有効にする')
chars_to_remove_input = ""
if enable_preprocessing:
    chars_to_remove_input = st.sidebar.text_input(
        'データから取り除きたい文字 (カンマ区切りで複数指定可)', 
        value='円,人,個,$,￥,,' # デフォルト値
    )

correlation_threshold = st.sidebar.slider(
    'グラフに表示する相関の閾値',
    min_value=0.1, max_value=1.0, value=0.5, step=0.05
)

# --- メイン処理 ---

if uploaded_file is not None:
    try:
        df_original = pd.read_csv(uploaded_file)
        df_to_process = df_original.copy()
        
        st.subheader('1. 読み込みデータ（オリジナル）')
        st.dataframe(df_original.head())

        # --- ▼▼▼ ここから前処理の実行部分を追加 ▼▼▼ ---
        if enable_preprocessing:
            st.subheader('2. 前処理後のデータ')
            chars_to_remove = [char.strip() for char in chars_to_remove_input.split(',')]
            df_to_process = preprocess_data(df_original, chars_to_remove)
            st.dataframe(df_to_process.head())
        
        # 分析可能な数値列があるかチェック
        numeric_cols = df_to_process.select_dtypes(include=np.number).columns.tolist()
        if len(numeric_cols) < 2:
            st.error("エラー: 分析可能な数値データ列が2つ以上ありません。前処理の設定やCSVファイルを確認してください。")
        else:
            st.info(f"分析対象の数値列: `{'`, `'.join(numeric_cols)}`")
            
            if st.button('相関ネットワークを生成！', type="primary"):
                with st.spinner('グラフを生成中です...'):
                    graph_data = create_correlation_network(df_to_process, correlation_threshold)
                    figure = draw_graph(graph_data, correlation_threshold)
                    if figure is not None:
                        st.pyplot(figure)
                        st.success('グラフが正常に生成されました！')

    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
else:
    st.info('👆 サイドバーからCSVファイルをアップロードして分析を開始してください。')
