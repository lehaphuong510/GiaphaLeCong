import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Nhập Liệu Gia Phả", page_icon="📝")

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def format_nam(nam_sinh, nam_mat):
    ns = str(nam_sinh).strip() if nam_sinh else ""
    nm = str(nam_mat).strip() if nam_mat else ""
    if ns or nm:
        return f"{ns} - {nm}"
    return ""

st.title("📝 Kê Khai Thông Tin Gia Phả")

with st.form("form_gia_pha"):
    st.subheader("1. Thông tin Người Kê Khai Chính")
    ten_chinh = st.text_input("Họ và Tên (Người chính)*")
    gioi_tinh_chinh = st.radio("Giới tính", ["NAM", "NỮ"], key="gt_chinh")
    col1, col2 = st.columns(2)
    ns_chinh = col1.text_input("Năm sinh (Người chính)", placeholder="VD: 1950")
    nm_chinh = col2.text_input("Năm mất (Nếu có)", placeholder="VD: 2020")
    
    st.markdown("---")
    st.subheader("2. Thông tin Cha Mẹ Ruột")
    ten_cha = st.text_input("Họ và Tên Cha")
    col_cha1, col_cha2 = st.columns(2)
    ns_cha = col_cha1.text_input("Năm sinh Cha")
    nm_cha = col_cha2.text_input("Năm mất Cha")
    
    ten_me = st.text_input("Họ và Tên Mẹ")
    col_me1, col_me2 = st.columns(2)
    ns_me = col_me1.text_input("Năm sinh Mẹ")
    nm_me = col_me2.text_input("Năm mất Mẹ")
    
    st.markdown("---")
    st.subheader("3. Thông tin Bạn Đời")
    so_luong_bd = st.number_input("Số lượng Bạn đời (Vợ/Chồng)", min_value=0, max_value=5, value=0)
    ban_doi_list = []
    # Dùng vòng lặp for để đẻ ra số lượng khung nhập liệu tùy theo con số user chọn
    for i in range(so_luong_bd):
        st.markdown(f"**Bạn đời {i+1}**")
        t_bd = st.text_input(f"Họ tên Bạn đời {i+1}")
        gt_bd = st.radio(f"Giới tính Bạn đời {i+1}", ["NAM", "NỮ"], key=f"gt_bd_{i}")
        c1, c2 = st.columns(2)
        ns_bd = c1.text_input(f"Năm sinh Bạn đời {i+1}")
        nm_bd = c2.text_input(f"Năm mất Bạn đời {i+1}")
        ban_doi_list.append({"ten": t_bd, "gt": gt_bd, "ns": ns_bd, "nm": nm_bd})
        
    st.markdown("---")
    st.subheader("4. Thông tin Con Cái")
    so_luong_con = st.number_input("Số lượng Con cái", min_value=0, max_value=15, value=0)
    con_cai_list = []
    for i in range(so_luong_con):
        st.markdown(f"**Con cái {i+1}**")
        t_con = st.text_input(f"Họ tên Con {i+1}")
        gt_con = st.radio(f"Giới tính Con {i+1}", ["NAM", "NỮ"], key=f"gt_con_{i}")
        c1, c2 = st.columns(2)
        ns_con = c1.text_input(f"Năm sinh Con {i+1}")
        nm_con = c2.text_input(f"Năm mất Con {i+1}")
        con_cai_list.append({"ten": t_con, "gt": gt_con, "ns": ns_con, "nm": nm_con})

    submit = st.form_submit_button("🚀 Gửi Thông Tin")

# --- KHI BẤM NÚT GỬI ---
if submit:
    if not ten_chinh:
        st.error("Vui lòng điền Họ tên Người chính!")
    else:
        # 1. Tạo Batch_ID
        ten_chinh_upper = ten_chinh.strip().upper()
        ten_khong_dau = ten_chinh_upper.replace(" ", "")
        batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M')}_{ten_khong_dau}"
        
        # 2. Gom dữ liệu theo chuẩn các cột của Tab "Data Raw"
        data_to_append = []
        
        # Người chính
        data_to_append.append({
            "Batch_ID": batch_id,
            "Họ tên": ten_chinh_upper,
            "Giới tính": gioi_tinh_chinh,
            "Năm sinh - Năm mất": format_nam(ns_chinh, nm_chinh),
            "Mối quan hệ với người chính": "NGƯỜI CHÍNH",
            "Người chính": ten_chinh_upper,
            "Trạng Thái": "Chờ duyệt"
        })
        
        # Cha
        if ten_cha:
            data_to_append.append({
                "Batch_ID": batch_id, "Họ tên": ten_cha.strip().upper(), "Giới tính": "NAM",
                "Năm sinh - Năm mất": format_nam(ns_cha, nm_cha),
                "Mối quan hệ với người chính": "CHA", "Người chính": ten_chinh_upper, "Trạng Thái": "Chờ duyệt"
            })
            
        # Mẹ
        if ten_me:
            data_to_append.append({
                "Batch_ID": batch_id, "Họ tên": ten_me.strip().upper(), "Giới tính": "NỮ",
                "Năm sinh - Năm mất": format_nam(ns_me, nm_me),
                "Mối quan hệ với người chính": "MẸ", "Người chính": ten_chinh_upper, "Trạng Thái": "Chờ duyệt"
            })
            
        # Bạn đời
        for bd in ban_doi_list:
            if bd["ten"]:
                data_to_append.append({
                    "Batch_ID": batch_id, "Họ tên": bd["ten"].strip().upper(), "Giới tính": bd["gt"],
                    "Năm sinh - Năm mất": format_nam(bd["ns"], bd["nm"]),
                    "Mối quan hệ với người chính": "BẠN ĐỜI", "Người chính": ten_chinh_upper, "Trạng Thái": "Chờ duyệt"
                })
                
        # Con cái
        for con in con_cai_list:
            if con["ten"]:
                data_to_append.append({
                    "Batch_ID": batch_id, "Họ tên": con["ten"].strip().upper(), "Giới tính": con["gt"],
                    "Năm sinh - Năm mất": format_nam(con["ns"], con["nm"]),
                    "Mối quan hệ với người chính": "CON", "Người chính": ten_chinh_upper, "Trạng Thái": "Chờ duyệt"
                })
        
        # 3. Nối Data và Đẩy lên Google Sheets
        df_new = pd.DataFrame(data_to_append)
        df_existing = conn.read(worksheet="Data Raw", usecols=list(df_new.columns))
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        
        conn.update(worksheet="Data Raw", data=df_updated)
        st.success(f"Đã gửi thành công! Mã lô của bạn: {batch_id}")
