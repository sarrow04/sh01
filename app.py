import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import japanize_matplotlib
import io

# --- 関数定義 (ここは変更なし) ---

def create_correlation_network(df, threshold):
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return None # 分析対象がない場合はNoneを返す
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

# --- Streamlit アプリケーションのUI部分 ---

st.set_page_config(layout="wide") 
st.title('相関ネットワーク分析アプリ 📊')
st.write('数値データを含むCSVファイルをアップロードすると、データ間の相関関係をネットワークグラフとして可視化します。')

st.sidebar.header('⚙️ 設定')

uploaded_file = st.sidebar.file_uploader(
    "分析したいCSVファイルをアップロード", type='csv'
)

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

        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(numeric_cols) < 2:
            st.error("エラー: 分析可能な数値データ列が2つ以上ありません。CSVファイルを確認してください。")
        else:
            st.info(f"分析対象の数値列: `{'`, `'.join(numeric_cols)}`")
            
            if st.button('相関ネットワークを生成！', type="primary"):
                with st.spinner('グラフを生成中です...'):
                    graph_data = create_correlation_network(df, correlation_threshold)
                    figure = draw_graph(graph_data, correlation_threshold)
                    
                    if figure is not None:
                        st.pyplot(figure)
                        st.success('グラフが正常に生成されました！')
                        
                        # --- ▼▼▼ ここからダウンロード機能 ▼▼▼ ---
                        
                        # グラフをメモリ上のバイナリデータとして保存
                        buf = io.BytesIO()
                        figure.savefig(buf, format="png", bbox_inches='tight')
                        
                        # ダウンロードボタンを設置
                        st.download_button(
                            label="グラフをPNG形式でダウンロード",
                            data=buf,
                            file_name="correlation_network.png",
                            mime="image/png"
                        )

    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
else:
    st.info('👆 サイドバーからCSVファイルをアップロードして分析を開始してください。')
