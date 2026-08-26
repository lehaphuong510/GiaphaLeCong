import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Nhập Liệu Gia Phả", page_icon="📝")
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vimdVQHFju63qniRp1XMXZW4unPTZkABw1ezYmo_MKI/edit?usp=sharing"

def get_vai_ve_list():
    try:
        df_phu = conn.read(spreadsheet=SHEET_URL, worksheet="Data phụ")
        return [""] + df_phu["Vai vế"].dropna().tolist()
    except Exception:
        return ["", "VỢ", "CHỒNG", "VỢ KẾ"]

def add_vai_ve_new(new_val):
    try:
        df_phu = conn.read(spreadsheet=SHEET_URL, worksheet="Data phụ")
        new_df = pd.DataFrame([{"Vai vế": new_val.upper()}])
        updated_df = pd.concat([df_phu, new_df], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, worksheet="Data phụ", data=updated_df)
    except Exception:
        pass

try:
    st.image("cover gia pha.jpg", use_container_width=True)
except Exception:
    st.title("📝 THÊM NGƯỜI VÀO GIA PHẢ")

vai_ve_options = get_vai_ve_list() + ["Tạo mới..."]

with st.form("form_gia_pha"):
    st.subheader("1. Thông tin người trung tâm")
    ten_chinh = st.text_input("Họ Tên*")
    gt_chinh = st.selectbox("Giới tính", ["NAM", "NỮ", "LGBTQ+"], key="gt_c")
    c1, c2 = st.columns(2)
    ns_chinh = c1.text_input("Năm sinh", placeholder="VD: 1950")
    nm_chinh = c2.text_input("Năm mất (nếu có, không rõ ghi 'Không rõ')", placeholder="VD: 2020 hoặc Không rõ")
    
    st.markdown("---")
    st.subheader("2. Thông tin Cha Mẹ Ruột")
    ten_cha = st.text_input("Họ và Tên Cha")
    col_cha1, col_cha2 = st.columns(2)
    ns_cha = col_cha1.text_input("Năm sinh Cha")
    nm_cha = col_cha2.text_input("Năm mất Cha (nếu có, không rõ ghi 'Không rõ')")
    
    ten_me = st.text_input("Họ và Tên Mẹ")
    col_me1, col_me2 = st.columns(2)
    ns_me = col_me1.text_input("Năm sinh Mẹ")
    nm_me = col_me2.text_input("Năm mất Mẹ (nếu có, không rõ ghi 'Không rõ')")
    
    st.markdown("---")
    st.subheader("3. Thông tin Bạn Đời")
    so_luong_bd = st.number_input("Số lượng Bạn đời", 0, 5, 0)
    ban_doi_list = []
    for i in range(so_luong_bd):
        st.write(f"**Bạn đời {i+1}**")
        t_bd = st.text_input(f"Họ tên Bạn đời {i+1}")
        gt_bd = st.selectbox(f"Giới tính Bạn đời {i+1}", ["NAM", "NỮ", "LGBTQ+"], key=f"gt_bd_{i}")
        
        col_vv1, col_vv2 = st.columns(2)
        vv_chon = col_vv1.selectbox(f"Vai vế", vai_ve_options, key=f"vv_chon_{i}")
        vv_moi = col_vv2.text_input(f"Nếu tạo mới, nhập vào đây:", key=f"vv_moi_{i}")
        
        c3, c4 = st.columns(2)
        ns_bd = c3.text_input(f"Năm sinh Bạn đời {i+1}")
        nm_bd = c4.text_input(f"Năm mất Bạn đời {i+1} (nếu có, không rõ ghi 'Không rõ')")
        ban_doi_list.append({"ten": t_bd, "gt": gt_bd, "vv_chon": vv_chon, "vv_moi": vv_moi, "ns": ns_bd, "nm": nm_bd})
        
    st.markdown("---")
    st.subheader("4. Thông tin Con Cái")
    so_luong_con = st.number_input("Số lượng Con cái", 0, 15, 0)
    con_cai_list = []
    for i in range(so_luong_con):
        st.write(f"**Con cái {i+1}**")
        t_con = st.text_input(f"Họ tên Con {i+1}")
        gt_con = st.selectbox(f"Giới tính Con {i+1}", ["NAM", "NỮ", "LGBTQ+"], key=f"gt_con_{i}")
        
        c5, c6 = st.columns(2)
        ns_con = c5.text_input(f"Năm sinh Con {i+1}")
        nm_con = c6.text_input(f"Năm mất Con {i+1} (nếu có, không rõ ghi 'Không rõ')")
        con_cai_list.append({"ten": t_con, "gt": gt_con, "ns": ns_con, "nm": nm_con})

    submit = st.form_submit_button("🚀 Gửi dữ liệu")

if submit and ten_chinh:
    batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M')}_{ten_chinh.replace(' ', '').upper()}"
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
                add_vai_ve_new(vv_final)
                
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
            
    # 1. Thêm dòng này để XÓA SẠCH TRÍ NHỚ TRƯỚC KHI ĐỌC:
    st.cache_data.clear() 
            
    # 2. Đọc dữ liệu mới nhất từ Sheet
    df_existing = conn.read(spreadsheet=SHEET_URL, worksheet="Data Raw")
    df_existing = df_existing.loc[:, ~df_existing.columns.str.contains('^Unnamed')]
            
    # 3. Ghi đè lên Sheet
    conn.update(spreadsheet=SHEET_URL, worksheet="Data Raw", data=pd.concat([df_existing, df_new], ignore_index=True))
    st.success("Đã ghi nhận! Ba hãy qua tab 'Duyệt Dữ Liệu' để đẩy chính thức lên cây nhé.")
    df_existing = conn.read(spreadsheet=SHEET_URL, worksheet="Data Raw", usecols=list(df_new.columns))
    conn.update(spreadsheet=SHEET_URL, worksheet="Data Raw", data=pd.concat([df_existing, df_new], ignore_index=True))
    st.success("Đã gửi thông tin thành công! Cảm ơn bạn đã đóng góp cho Gia phả.")
