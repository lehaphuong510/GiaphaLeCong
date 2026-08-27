import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
import uuid
from datetime import datetime

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

# Đã chỉnh cấu hình Cây gia phả xếp tầng (Hierarchical)
config = Config(width="100%", height=700, directed=True, physics=False, hierarchical=True, direction="UD")

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

if st.sidebar.button("🔄 CẬP NHẬT DỮ LIỆU MỚI NHẤT", use_container_width=True):
    st.cache_data.clear() 
    st.rerun()
st.sidebar.markdown("---")

if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

if not st.session_state["admin_logged_in"]:
    pass_input = st.sidebar.text_input("Nhập mật khẩu Admin:", type="password")
    if st.sidebar.button("Đăng nhập") or pass_input:
        if pass_input.strip() == "010663": 
            st.session_state["admin_logged_in"] = True
            st.rerun() 
        elif pass_input != "":
            st.sidebar.error("Sai mật khẩu, vui lòng thử lại!")

if st.session_state["admin_logged_in"]:
    st.sidebar.success("Đã mở khóa Admin!")
    if st.sidebar.button("Đăng xuất"):
        st.session_state["admin_logged_in"] = False
        st.rerun()
        
    # Đã đảo vị trí "Thêm Người Trực Tiếp" lên đầu tiên
    admin_menu = st.sidebar.radio("Chức năng", ["📝 Thêm Người Trực Tiếp", "📋 Duyệt Dữ Liệu", "✏️ Chỉnh Sửa Dữ Liệu"])
    
    if admin_menu == "📝 Thêm Người Trực Tiếp":
        st.subheader("📝 THÊM NGƯỜI VÀO GIA PHẢ")
        
        try:
            df_phu = conn.read(spreadsheet=SHEET_URL, worksheet="Data phụ")
            vai_ve_options = [""] + df_phu["Vai vế"].dropna().tolist() + ["Tạo mới..."]
        except Exception:
            vai_ve_options = ["", "VỢ", "CHỒNG", "VỢ KẾ", "Tạo mới..."]

        # Cơ chế Reset Form an toàn tuyệt đối
        if "form_key" not in st.session_state:
            st.session_state.form_key = 0
        fk = st.session_state.form_key
            
        st.subheader("1. Thông tin người trung tâm")
        ten_chinh = st.text_input("Họ Tên*", key=f"tc_{fk}")
        gt_chinh = st.selectbox("Giới tính", ["NAM", "NỮ", "LGBTQ+"], key=f"gtc_{fk}")
        c1, c2 = st.columns(2)
        ns_chinh = c1.text_input("Năm sinh", placeholder="VD: 1950", key=f"nsc_{fk}")
        nm_chinh = c2.text_input("Năm mất (nếu có, không rõ ghi 'Không rõ')", placeholder="VD: 2020 hoặc Không rõ", key=f"nmc_{fk}")
        
        st.markdown("---")
        st.subheader("2. Thông tin Cha Mẹ Ruột")
        ten_cha = st.text_input("Họ và Tên Cha", key=f"tcha_{fk}")
        col_cha1, col_cha2 = st.columns(2)
        ns_cha = col_cha1.text_input("Năm sinh Cha", key=f"nscha_{fk}")
        nm_cha = col_cha2.text_input("Năm mất Cha (nếu có, không rõ ghi 'Không rõ')", key=f"nmcha_{fk}")
        
        ten_me = st.text_input("Họ và Tên Mẹ", key=f"tme_{fk}")
        col_me1, col_me2 = st.columns(2)
        ns_me = col_me1.text_input("Năm sinh Mẹ", key=f"nsme_{fk}")
        nm_me = col_me2.text_input("Năm mất Mẹ (nếu có, không rõ ghi 'Không rõ')", key=f"nmme_{fk}")
        
        st.markdown("---")
        st.subheader("3. Thông tin Bạn Đời")
        so_luong_bd = st.number_input("Số lượng Bạn đời", 0, 5, 0, key=f"slbd_{fk}")
        ban_doi_list = []
        for i in range(so_luong_bd):
            st.write(f"**Bạn đời {i+1}**")
            t_bd = st.text_input(f"Họ tên Bạn đời {i+1}", key=f"tbd_{i}_{fk}")
            gt_bd = st.selectbox(f"Giới tính Bạn đời {i+1}", ["NAM", "NỮ", "LGBTQ+"], key=f"gtbd_{i}_{fk}")
            
            col_vv1, col_vv2 = st.columns(2)
            vv_chon = col_vv1.selectbox(f"Vai vế", vai_ve_options, key=f"vvc_{i}_{fk}")
            vv_moi = col_vv2.text_input(f"Nếu tạo mới, nhập vào đây:", key=f"vvm_{i}_{fk}")
            
            c3, c4 = st.columns(2)
            ns_bd = c3.text_input(f"Năm sinh Bạn đời {i+1}", key=f"nsbd_{i}_{fk}")
            nm_bd = c4.text_input(f"Năm mất Bạn đời {i+1} (nếu có, không rõ ghi 'Không rõ')", key=f"nmbd_{i}_{fk}")
            ban_doi_list.append({"ten": t_bd, "gt": gt_bd, "vv_chon": vv_chon, "vv_moi": vv_moi, "ns": ns_bd, "nm": nm_bd})
            
        st.markdown("---")
        st.subheader("4. Thông tin Con Cái")
        so_luong_con = st.number_input("Số lượng Con cái", 0, 15, 0, key=f"slc_{fk}")
        con_cai_list = []
        for i in range(so_luong_con):
            st.write(f"**Con cái {i+1}**")
            t_con = st.text_input(f"Họ tên Con {i+1}", key=f"tcon_{i}_{fk}")
            gt_con = st.selectbox(f"Giới tính Con {i+1}", ["NAM", "NỮ", "LGBTQ+"], key=f"gtcon_{i}_{fk}")
            
            c5, c6 = st.columns(2)
            ns_con = c5.text_input(f"Năm sinh Con {i+1}", key=f"nscon_{i}_{fk}")
            nm_con = c6.text_input(f"Năm mất Con {i+1} (nếu có, không rõ ghi 'Không rõ')", key=f"nmcon_{i}_{fk}")
            con_cai_list.append({"ten": t_con, "gt": gt_con, "ns": ns_con, "nm": nm_con})
            
        # Thay vì form_submit_button, chúng ta dùng nút bấm thông thường
        submit_admin = st.button("🚀 Gửi dữ liệu")
        
        if submit_admin and ten_chinh:
            batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M')}_{ten_chinh.replace(' ', '').upper()}_ADMIN"
            data_raw = []
            
            ns_c = str(ns_chinh).strip()
            nm_c = str(nm_chinh).strip()
            nam_chinh_str = f"{ns_c} - {nm_c}" if ns_c or nm_c else ""
            
            data_raw.append({
                "Batch_ID": batch_id, "Họ tên": ten_chinh.strip().upper(), "Giới tính": gt_chinh,
                "Năm sinh - Năm mất": nam_chinh_str, "Mối quan hệ với người chính": "NGƯỜI CHÍNH",
                "Người chính": ten_chinh.strip().upper(), "Trạng Thái": "Chờ duyệt"
            })
            
            if ten_cha:
                ns_cha_str = str(ns_cha).strip()
                nm_cha_str = str(nm_cha).strip()
                nam_cha_final = f"{ns_cha_str} - {nm_cha_str}" if ns_cha_str or nm_cha_str else ""
                data_raw.append({
                    "Batch_ID": batch_id, "Họ tên": ten_cha.strip().upper(), "Giới tính": "NAM",
                    "Năm sinh - Năm mất": nam_cha_final, "Mối quan hệ với người chính": "CHA", 
                    "Người chính": ten_chinh.strip().upper(), "Trạng Thái": "Chờ duyệt"
                })
                
            if ten_me:
                ns_me_str = str(ns_me).strip()
                nm_me_str = str(nm_me).strip()
                nam_me_final = f"{ns_me_str} - {nm_me_str}" if ns_me_str or nm_me_str else ""
                data_raw.append({
                    "Batch_ID": batch_id, "Họ tên": ten_me.strip().upper(), "Giới tính": "NỮ",
                    "Năm sinh - Năm mất": nam_me_final, "Mối quan hệ với người chính": "MẸ", 
                    "Người chính": ten_chinh.strip().upper(), "Trạng Thái": "Chờ duyệt"
                })
            
            for bd in ban_doi_list:
                if bd["ten"]:
                    vv_final = bd["vv_moi"].strip().upper() if bd["vv_chon"] == "Tạo mới..." and bd["vv_moi"] else str(bd["vv_chon"])
                    if bd["vv_chon"] == "Tạo mới..." and bd["vv_moi"]:
                        try:
                            df_phu_update = pd.concat([df_phu, pd.DataFrame([{"Vai vế": vv_final}])], ignore_index=True)
                            conn.update(spreadsheet=SHEET_URL, worksheet="Data phụ", data=df_phu_update)
                        except Exception: 
                            pass
                        
                    ns_b = str(bd['ns']).strip()
                    nm_b = str(bd['nm']).strip()
                    nam_bd_str = f"{ns_b} - {nm_b}" if ns_b or nm_b else ""
                    
                    data_raw.append({
                        "Batch_ID": batch_id, "Họ tên": bd["ten"].strip().upper(), "Giới tính": bd["gt"],
                        "Vai vế": vv_final, "Năm sinh - Năm mất": nam_bd_str,
                        "Mối quan hệ với người chính": "BẠN ĐỜI", "Người chính": ten_chinh.strip().upper(), "Trạng Thái": "Chờ duyệt"
                    })
                    
            for con in con_cai_list:
                if con["ten"]:
                    ns_con_str = str(con['ns']).strip()
                    nm_con_str = str(con['nm']).strip()
                    nam_con_final = f"{ns_con_str} - {nm_con_str}" if ns_con_str or nm_con_str else ""
                    data_raw.append({
                        "Batch_ID": batch_id, "Họ tên": con["ten"].strip().upper(), "Giới tính": con["gt"],
                        "Năm sinh - Năm mất": nam_con_final, "Mối quan hệ với người chính": "CON", 
                        "Người chính": ten_chinh.strip().upper(), "Trạng Thái": "Chờ duyệt"
                    })
                    
            df_new = pd.DataFrame(data_raw)
            
            st.cache_data.clear()
            df_existing = conn.read(spreadsheet=SHEET_URL, worksheet="Data Raw")
            df_existing = df_existing.loc[:, ~df_existing.columns.str.contains('^Unnamed')]
            conn.update(spreadsheet=SHEET_URL, worksheet="Data Raw", data=pd.concat([df_existing, df_new], ignore_index=True))
            
            # Reset Form sau khi thành công
            st.session_state.form_key += 1
            st.success("Đã ghi nhận! Ba hãy qua tab 'Duyệt Dữ Liệu' để đẩy chính thức lên cây nhé.")
            st.rerun()
            
        elif submit_admin and not ten_chinh:
            st.error("Vui lòng điền Họ tên người trung tâm!")

    elif admin_menu == "📋 Duyệt Dữ Liệu":
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
                    cols_to_show = [c for c in ["Họ tên", "Mối quan hệ với người chính", "Vai vế", "Giới tính", "Năm sinh - Năm mất"] if c in df_batch.columns]
                    st.dataframe(df_batch[cols_to_show])
                    
                    if st.button("✅ Duyệt lô này", key=f"btn_{batch}"):
                        row_chinh = df_batch[df_batch["Mối quan hệ với người chính"] == "NGƯỜI CHÍNH"]
                        
                        if not row_chinh.empty:
                            nguoi_chinh = row_chinh.iloc[0]
                            ten_chinh = nguoi_chinh["Họ tên"]
                            gt_chinh = nguoi_chinh["Giới tính"]
                            
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
                                
                            conn.update(spreadsheet=SHEET_URL, worksheet="Data Gia Phả", data=df_gia_pha)
                            df_raw.loc[df_raw["Batch_ID"] == batch, "Trạng Thái"] = "Đã duyệt"
                            conn.update(spreadsheet=SHEET_URL, worksheet="Data Raw", data=df_raw)
                            
                            st.success("Đã duyệt thành công và cấp ID tự động!")
                            st.rerun()

    elif admin_menu == "✏️ Chỉnh Sửa Dữ Liệu":
        st.subheader("✏️ Bảng Chỉnh Sửa Thông Tin Nhanh")
        st.info("💡 Hướng dẫn: Click đúp vào ô bất kỳ để sửa. Sửa xong nhớ bấm nút 'Lưu thay đổi' ở bên dưới!")
        
        try:
            df_hien_tai = conn.read(spreadsheet=SHEET_URL, worksheet="Data Gia Phả")
            df_chinh_sua = st.data_editor(
                df_hien_tai, 
                use_container_width=True,
                num_rows="dynamic", 
                disabled=["ID"] 
            )
            
            if st.button("💾 Lưu thay đổi"):
                conn.update(spreadsheet=SHEET_URL, worksheet="Data Gia Phả", data=df_chinh_sua)
                st.success("Đã cập nhật thay đổi thành công! Qua trang Cây Gia Phả để xem kết quả nha.")
                st.rerun()
                
        except Exception as e:
            st.error("Có lỗi khi tải dữ liệu. Vui lòng kiểm tra lại.")
