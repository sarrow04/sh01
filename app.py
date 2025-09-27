import streamlit as st

st.title("ライブラリのインポートテスト")
st.write("これからライブラリを一つずつ読み込みます...")

try:
    st.write("streamlit OK")
    
    import pandas as pd
    st.write("✅ pandas OK")
    
    import numpy as np
    st.write("✅ numpy OK")
    
    import networkx as nx
    st.write("✅ networkx OK")
    
    import matplotlib.pyplot as plt
    st.write("✅ matplotlib OK")
    
    # ↓↓↓ おそらく、この次の行で処理が止まっている可能性が高い ↓↓↓
    import japanize_matplotlib
    st.write("✅ japanize_matplotlib OK")
    
    st.success("すべてのライブラリの読み込みに成功しました！")
    st.balloons()

except Exception as e:
    st.error(f"以下のライブラリの読み込みでエラーが発生しました: {e}")
