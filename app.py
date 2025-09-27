import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import japanize_matplotlib

# --- アプリのUI部分 ---
st.title('相関ネットワーク分析アプリ 📊')
st.write("UIは表示されますか？") # 目印1

uploaded_file = st.sidebar.file_uploader(
    "CSVファイルをアップロードしてください", type='csv'
)
st.write("ファイルアップローダーは表示されますか？") # 目印2

# --- メイン処理 ---
if uploaded_file is not None:
    st.write("ファイルがアップロードされました。") # 目印3
    
    try:
        df = pd.read_csv(uploaded_file)
        st.write("✅ CSVの読み込みに成功") # 目印4
        st.dataframe(df.head())

        # 数値データがあるか確認
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(numeric_cols) < 2:
            st.error("エラー: 分析可能な数値データ列が2つ未満です。")
        else:
            st.write(f"✅ 分析対象の数値データ列: {numeric_cols}") # 目印5

            if st.button('グラフ生成開始！', type="primary"):
                st.write("グラフ生成ボタンが押されました。") # 目印6
                
                # 相関計算
                corr_matrix = df[numeric_cols].corr()
                st.write("✅ 相関行列の計算に成功") # 目印7

                # グラフ描画
                fig, ax = plt.subplots(figsize=(16, 16))
                st.write("✅ グラフ描画の準備完了 (subplots)") # 目印8
                
                # ここに本来の描画処理が入るが、今は省略して表示テスト
                ax.set_title("テストグラフ")
                ax.plot([0, 1], [0, 1]) # 簡単なテスト用直線をプロット
                
                st.pyplot(fig)
                st.write("✅ st.pyplot()の実行完了") # 目印9
                st.success("処理が完了しました！")

    except Exception as e:
        st.error(f"処理中にエラーが発生しました: {e}")
else:
    st.info('👆 サイドバーからCSVをアップロードしてください。')
