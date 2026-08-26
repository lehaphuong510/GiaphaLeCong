import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="Gia Phả Lê Công", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- KHU VỰC PUBLIC: CÂY GIA PHẢ ---
try:
    st.image("cover gia pha.jpg", use_container_width=True)
except:
    st.title("🌳 Gia Phả Lê Công")

df_gia_pha = conn.read(worksheet="Data Gia Phả")

nodes = []
edges = []

for _, row in df_gia_pha.iterrows():
    nam_mat = str(row.get("Năm sinh - Năm mất", "")).split("-")[-1].strip()
    is_dead = bool(nam_mat)
    vai_ve = str(row.get("Vai vế", "")).upper()
    
    # Phân loại Sống / Mất và Ly dị
    if is_dead:
        color = "#A9A9A9" # Xám
        label = f"🕊️ {row['Họ tên']}"
    elif vai_ve == "ĐÃ LY DỊ":
        color = "#D3D3D3" # Xám mờ
        label = row['Họ tên']
    else:
        color = "#ADD8E6" if row["Giới tính"] == "NAM" else "#FFB6C1" if row["Giới tính"] == "NỮ" else "#DDA0DD"
        label = row['Họ tên']
        
    nodes.append(Node(id=row["ID"], label=label, color=color, shape="box"))
    
    if pd.notna(row.get("ID_Cha")):
        edges.append(Edge(source=row["ID_Cha"], target=row["ID"], label="Cha - Con"))
    if pd.notna(row.get("ID_Bạn đời")):
        edges.append(Edge(source=row["ID_Bạn đời"], target=row["ID"], label="Bạn đời", dashes=True))

config = Config(width="100%", height=600, directed=True, physics=True, hierarchical=False)

col1, col2 = st.columns([3, 1])
with col1:
    clicked_node = agraph(nodes=nodes, edges=edges, config=config)

with col2:
    if clicked_node:
        person_info = df_gia_pha[df_gia_pha["ID"] == clicked_node].iloc[0]
        st.info(f"**Họ tên:** {person_info['Họ tên']}\n\n**Năm:** {person_info['Năm sinh - Năm mất']}\n\n**Vai vế:** {person_info['Vai vế']}")
    else:
        st.write("👈 Click vào một người để xem chi tiết")

# --- KHU VỰC ADMIN (CÓ PASS) ---
st.sidebar.title("🔐 Dành cho Quản trị")
pass_input = st.sidebar.text_input("Nhập mật khẩu Admin:", type="password")

if pass_input == "010663":
    st.sidebar.success("Đã mở khóa Admin!")
    admin_menu = st.sidebar.radio("Chức năng", ["Duyệt Dữ Liệu", "Thêm Người Trực Tiếp"])
    
    if admin_menu == "Duyệt Dữ Liệu":
        st.subheader("Danh sách chờ duyệt")
        df_raw = conn.read(worksheet="Data Raw")
        df_cho_duyet = df_raw[df_raw["Trạng Thái"] == "Chờ duyệt"]
        st.dataframe(df_cho_duyet)
        
    elif admin_menu == "Thêm Người Trực Tiếp":
        st.subheader("Form nhập liệu Admin")
        st.write("(Sử dụng cấu trúc form tương tự App 1)")
