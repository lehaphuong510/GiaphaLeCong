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
        return df_phu["Vai vế"].dropna().tolist()
    except Exception:
        return ["VỢ", "CHỒNG", "VỢ KẾ"]

def add_vai_ve_new(new_val):
    df_phu = conn.read(spreadsheet=SHEET_URL, worksheet="Data phụ")
    new_df = pd.DataFrame([{"Vai vế": new_val.upper()}])
    updated_df = pd.concat([df_phu, new_df], ignore_index=True)
    conn.update(spreadsheet=SHEET_URL, worksheet="Data phụ", data=updated_df)

try:
    st.image("cover gia pha.jpg", use_container_width=True)
except Exception:
    st.title("📝 Kê Khai Thông Tin Gia Phả")

vai_ve_options = get_vai_ve_list() + ["Tạo mới..."]

with st.form("form_gia_pha"):
    st.subheader("1. Kê Khai Chính")
    ten_chinh = st.text_input("Họ Tên*")
    gt_chinh = st.selectbox("Giới tính", ["NAM", "NỮ", "LGBTQ+"], key="gt_c")
    c1, c2 = st.columns(2)
    ns_chinh = c1.text_input("Năm sinh", placeholder="VD: 1950")
    nm_chinh = c2.text_input("Năm mất", placeholder="VD: 2020")
    
    st.markdown("---")
    st.subheader("2. Bạn Đời")
    so_luong_bd = st.number_input("Số lượng", 0, 5, 0)
    ban_doi_list = []
    for i in range(so_luong_bd):
        st.write(f"**Bạn đời {i+1}**")
        t_bd = st.text_input(f"Họ tên Bạn đời {i+1}")
        gt_bd = st.selectbox(f"Giới tính {i+1}", ["NAM", "NỮ", "LGBTQ+"], key=f"gt_bd_{i}")
        
        col_vv1, col_vv2 = st.columns(2)
        vv_chon = col_vv1.selectbox(f"Vai vế", vai_ve_options, key=f"vv_chon_{i}")
        vv_moi = col_vv2.text_input(f"Nếu tạo mới, nhập vào đây:", key=f"vv_moi_{i}")
        
        c3, c4 = st.columns(2)
        ns_bd = c3.text_input(f"Năm sinh {i+1}")
        nm_bd = c4.text_input(f"Năm mất {i+1}")
        ban_doi_list.append({"ten": t_bd, "gt": gt_bd, "vv_chon": vv_chon, "vv_moi": vv_moi, "ns": ns_bd, "nm": nm_bd})

    submit = st.form_submit_button("🚀 Gửi")

if submit and ten_chinh:
    batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M')}_{ten_chinh.replace(' ', '').upper()}"
    data_raw = []
    
    # Định dạng năm
    ns_c = str(ns_chinh).strip()
    nm_c = str(nm_chinh).strip()
    nam_chinh_str = f"{ns_c} - {nm_c}" if ns_c or nm_c else ""
    
    data_raw.append({
        "Batch_ID": batch_id, "Họ tên": ten_chinh.strip().upper(), "Giới tính": gt_chinh,
        "Năm sinh - Năm mất": nam_chinh_str, "Mối quan hệ với người chính": "NGƯỜI CHÍNH",
        "Người chính": ten_chinh.strip().upper(), "Trạng Thái": "Chờ duyệt"
    })
    
    for bd in ban_doi_list:
        if bd["ten"]:
            vv_final = bd["vv_moi"].strip().upper() if bd["vv_chon"] == "Tạo mới..." and bd["vv_moi"] else bd["vv_chon"]
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
            
    df_new = pd.DataFrame(data_raw)
    df_existing = conn.read(spreadsheet=SHEET_URL, worksheet="Data Raw", usecols=list(df_new.columns))
    conn.update(spreadsheet=SHEET_URL, worksheet="Data Raw", data=pd.concat([df_existing, df_new], ignore_index=True))
    st.success("Đã gửi thành công!")
