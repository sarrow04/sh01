import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import japanize_matplotlib

# --- 関数定義 ---

def create_correlation_network(df, threshold):
    """
    DataFrameから相関ネットワークグラフを生成する関数
    """
    # 数値データのみを抽出
    numeric_df = df.select_dtypes(include=np.number)
    
    # 相関行列を計算
    corr_matrix = numeric_df.corr()
    
    # グラフオブジェクトを生成
    G = nx.Graph()
    
    # 相関行列からエッジを追加
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > threshold:
                # 正の相関か負の相関かを 'sign' として追加
                G.add_edge(corr_matrix.columns[i], corr_matrix.columns[j], 
                           weight=abs(corr_value), 
                           sign=np.sign(corr_value))
    return G

def draw_graph(G, threshold):
    """
    NetworkXグラフオブジェクトを描画し、matplotlibのfigureを返す関数
    """
    if not G or not G.nodes():
        st.warning("閾値を超える相関が見つかりませんでした。閾値を下げてみてください。")
        return None

    # グラフの描画設定
    fig, ax = plt.subplots(figsize=(16, 16))
    pos = nx.spring_layout(G, k=0.8, seed=42) # ノードの配置を計算
    
    # エッジ（線）の太さと色を決定
    weights = [G[u][v]['weight'] * 5 for u, v in G.edges()]
    edge_colors = ['red' if G[u][v]['sign'] > 0 else 'blue' for u, v in G.edges()]
    
    # グラフの描画
    nx.draw_networkx(
        G, pos, ax=ax,
        with_labels=True, 
        node_color='skyblue', 
        node_size=3000, 
        font_size=14,
        font_family='IPAexGothic', 
        width=weights, 
        edge_color=edge_colors
    )
    
    # タイトルと凡例
    ax.set_title(f'相関ネットワーク (閾値: {threshold:.2f})', fontsize=20)
    ax.text(0.01, 0.01, '赤線: 正の相関 / 青線: 負の相関', transform=ax.transAxes, fontsize=14, verticalalignment='bottom')
    
    return fig

# --- Streamlit アプリケーションのUI部分 ---

# ページの基本設定
st.set_page_config(layout="wide") 
st.title('相関ネットワーク分析アプリ 📊')
st.write('CSVファイルをアップロードすると、データ間の相関関係をネットワークグラフとして可視化します。')

# サイドバーに設定項目をまとめる
st.sidebar.header('⚙️ 設定')

# 1. ファイルアップローダー
uploaded_file = st.sidebar.file_uploader(
    "分析したいCSVファイルをアップロード", type='csv'
)

# 2. 相関の閾値を決めるスライダー
correlation_threshold = st.sidebar.slider(
    'グラフに表示する相関の閾値',
    min_value=0.1, max_value=1.0, value=0.5, step=0.05
)

# --- メイン処理 ---

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        st.subheader('読み込みデータ（先頭5行）')
        st.dataframe(df.head())

        # 分析可能な数値列があるかチェック
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(numeric_cols) < 2:
            st.error("エラー: 分析可能な数値データ列が2つ以上ありません。CSVファイルを確認してください。")
        else:
            st.info(f"分析対象の数値列: `{'`, `'.join(numeric_cols)}`")
            
            # 分析実行ボタン
            if st.button('相関ネットワークを生成！', type="primary"):
                with st.spinner('グラフを生成中です...'):
                    # 1. 相関ネットワークを生成
                    graph_data = create_correlation_network(df, correlation_threshold)
                    
                    # 2. グラフを描画
                    figure = draw_graph(graph_data, correlation_threshold)
                    
                    # 3. Streamlitでグラフを表示
                    if figure is not None:
                        st.pyplot(figure)
                        st.success('グラフが正常に生成されました！')

    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
else:
    st.info('👆 サイドバーからCSVファイルをアップロードして分析を開始してください。')
