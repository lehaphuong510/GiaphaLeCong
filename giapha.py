import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
import uuid

st.set_page_config(page_title="Gia Phả Lê Công", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vimdVQHFju63qniRp1XMXZW4unPTZkABw1ezYmo_MKI/edit?usp=sharing"

def generate_id():
    return f"P_{uuid.uuid4().hex[:6].upper()}"

# --- KHU VỰC PUBLIC: CÂY GIA PHẢ ---
try:
    st.image("cover gia pha.jpg", use_container_width=True)
except:
    st.title("🌳 Gia Phả Dòng Tộc")

try:
    df_gia_pha = conn.read(spreadsheet=SHEET_URL, worksheet="Data Gia Phả")
except Exception as e:
    st.error("Chưa đọc được Data Gia Phả. Vui lòng kiểm tra lại Google Sheet.")
    st.stop()

nodes = []
edges = []

if not df_gia_pha.empty:
    for _, row in df_gia_pha.iterrows():
        chuoi_nam = str(row.get("Năm sinh - Năm mất", ""))
        nam_mat = chuoi_nam.split("-")[-1].strip() if "-" in chuoi_nam else ""
        is_dead = bool(nam_mat)
        vai_ve = str(row.get("Vai vế", "")).upper()
        
        if is_dead:
            color = "#A9A9A9"
            label = f"🕊️ {row['Họ tên']}"
        elif vai_ve == "ĐÃ LY DỊ":
            color = "#D3D3D3"
            label = row['Họ tên']
        else:
            color = "#ADD8E6" if row["Giới tính"] == "NAM" else "#FFB6C1" if row["Giới tính"] == "NỮ" else "#DDA0DD"
            label = row['Họ tên']
            
        nodes.append(Node(id=str(row["ID"]), label=label, color=color, shape="box"))
        
        if pd.notna(row.get("ID_Cha")) and str(row.get("ID_Cha")).strip() != "":
            edges.append(Edge(source=str(row["ID_Cha"]), target=str(row["ID"]), label="Cha - Con"))
        if pd.notna(row.get("ID_Bạn đời")) and str(row.get("ID_Bạn đời")).strip() != "":
            edges.append(Edge(source=str(row["ID_Bạn đời"]), target=str(row["ID"]), label="Bạn đời", dashes=True))

config = Config(width="100%", height=600, directed=True, physics=True, hierarchical=False)

if nodes:
    col1, col2 = st.columns([3, 1])
    with col1:
        clicked_node = agraph(nodes=nodes, edges=edges, config=config)
    with col2:
        if clicked_node:
            person_info = df_gia_pha[df_gia_pha["ID"] == clicked_node].iloc[0]
            st.info(f"**Họ tên:** {person_info['Họ tên']}\n\n**Năm:** {person_info['Năm sinh - Năm mất']}\n\n**Vai vế:** {person_info.get('Vai vế', '')}")
        else:
            st.write("👈 Click vào một người để xem chi tiết")
else:
    st.info("Cây gia phả hiện chưa có dữ liệu. Hãy duyệt người đầu tiên!")

# --- KHU VỰC ADMIN (CÓ PASS) ---
st.sidebar.title("🔐 Dành cho Quản trị")

# 1. Khởi tạo bộ nhớ tạm để ghi nhận trạng thái Đăng nhập
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

# 2. Nếu chưa đăng nhập -> Hiện ô nhập Pass
if not st.session_state["admin_logged_in"]:
    pass_input = st.sidebar.text_input("Nhập mật khẩu Admin:", type="password")
    
    # Bấm nút hoặc nhấn Enter đều ăn lệnh
    if st.sidebar.button("Đăng nhập") or pass_input:
        if pass_input.strip() == "010663": # strip() để lỡ ba m gõ dư khoảng trắng vẫn nhận
            st.session_state["admin_logged_in"] = True
            st.rerun() # Tải lại trang để hiện menu Admin
        elif pass_input != "":
            st.sidebar.error("Sai mật khẩu, vui lòng thử lại!")

# 3. Nếu ĐÃ đăng nhập thành công -> Hiện Menu làm việc
if st.session_state["admin_logged_in"]:
    st.sidebar.success("Đã mở khóa Admin!")
    
    # Thêm nút Đăng xuất cho ngầu
    if st.sidebar.button("Đăng xuất"):
        st.session_state["admin_logged_in"] = False
        st.rerun()
        
    admin_menu = st.sidebar.radio("Chức năng", ["Duyệt Dữ Liệu", "Thêm Người Trực Tiếp"])
    
    if admin_menu == "Duyệt Dữ Liệu":
        st.subheader("📋 Danh sách chờ duyệt")
        df_raw = conn.read(spreadsheet=SHEET_URL, worksheet="Data Raw")
        df_cho_duyet = df_raw[df_raw["Trạng Thái"] == "Chờ duyệt"]
        
        if df_cho_duyet.empty:
            st.info("Hiện không có lô dữ liệu nào chờ duyệt.")
        else:
            batches = df_cho_duyet["Batch_ID"].unique()
            for batch in batches:
                with st.expander(f"📦 Lô dữ liệu: {batch}"):
                    df_batch = df_cho_duyet[df_cho_duyet["Batch_ID"] == batch]
                    st.dataframe(df_batch[["Họ tên", "Mối quan hệ với người chính", "Vai vế", "Giới tính", "Năm sinh - Năm mất"]])
                    
                    if st.button("✅ Duyệt lô này", key=f"btn_{batch}"):
                        row_chinh = df_batch[df_batch["Mối quan hệ với người chính"] == "NGƯỜI CHÍNH"]
                        
                        if not row_chinh.empty:
                            nguoi_chinh = row_chinh.iloc[0]
                            ten_chinh = nguoi_chinh["Họ tên"]
                            gt_chinh = nguoi_chinh["Giới tính"]
                            
                            # Kiểm tra xem người chính đã có trong Gia phả chưa
                            match_chinh = df_gia_pha[df_gia_pha["Họ tên"] == ten_chinh]
                            
                            if not match_chinh.empty:
                                idx_chinh = match_chinh.index[0]
                                main_id = df_gia_pha.at[idx_chinh, "ID"]
                                gt_chinh = df_gia_pha.at[idx_chinh, "Giới tính"]
                            else:
                                main_id = generate_id()
                                new_row_chinh = {
                                    "ID": main_id, "Họ tên": ten_chinh, "Giới tính": gt_chinh,
                                    "Năm sinh - Năm mất": nguoi_chinh.get("Năm sinh - Năm mất", ""),
                                    "Vai vế": "", "ID_Cha": "", "ID_Mẹ": "", "ID_Bạn đời": ""
                                }
                                df_gia_pha = pd.concat([df_gia_pha, pd.DataFrame([new_row_chinh])], ignore_index=True)
                                idx_chinh = df_gia_pha.index[-1]
                            
                            new_records = []
                            for _, row in df_batch.iterrows():
                                mqh = row["Mối quan hệ với người chính"]
                                if mqh == "NGƯỜI CHÍNH":
                                    continue
                                    
                                new_id = generate_id()
                                new_record = {
                                    "ID": new_id, "Họ tên": row["Họ tên"], "Giới tính": row["Giới tính"],
                                    "Năm sinh - Năm mất": row.get("Năm sinh - Năm mất", ""),
                                    "Vai vế": row.get("Vai vế", ""),
                                    "ID_Cha": "", "ID_Mẹ": "", "ID_Bạn đời": ""
                                }
                                
                                if mqh == "CHA":
                                    df_gia_pha.at[idx_chinh, "ID_Cha"] = new_id
                                elif mqh == "MẸ":
                                    df_gia_pha.at[idx_chinh, "ID_Mẹ"] = new_id
                                elif mqh == "BẠN ĐỜI":
                                    new_record["ID_Bạn đời"] = main_id
                                elif mqh == "CON":
                                    if gt_chinh == "NAM":
                                        new_record["ID_Cha"] = main_id
                                    elif gt_chinh == "NỮ":
                                        new_record["ID_Mẹ"] = main_id
                                        
                                new_records.append(new_record)
                                
                            if new_records:
                                df_gia_pha = pd.concat([df_gia_pha, pd.DataFrame(new_records)], ignore_index=True)
                                
                            # Cập nhật Google Sheets
                            conn.update(spreadsheet=SHEET_URL, worksheet="Data Gia Phả", data=df_gia_pha)
                            
                            df_raw.loc[df_raw["Batch_ID"] == batch, "Trạng Thái"] = "Đã duyệt"
                            conn.update(spreadsheet=SHEET_URL, worksheet="Data Raw", data=df_raw)
                            
                            st.success("Đã duyệt thành công và cấp ID tự động!")
                            st.rerun()
