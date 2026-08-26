# Thêm lựa chọn "Chỉnh Sửa" vào Menu
    admin_menu = st.sidebar.radio("Chức năng", ["📋 Duyệt Dữ Liệu", "📝 Thêm Người Trực Tiếp", "✏️ Chỉnh Sửa Dữ Liệu"])
    
    # ... (Giữ nguyên phần code của 📋 Duyệt Dữ Liệu) ...
    # ... (Giữ nguyên phần code của 📝 Thêm Người Trực Tiếp) ...

    # --- THÊM ĐOẠN CODE NÀY XUỐNG DƯỚI CÙNG ---
    elif admin_menu == "✏️ Chỉnh Sửa Dữ Liệu":
        st.subheader("✏️ Bảng Chỉnh Sửa Thông Tin Nhanh")
        st.info("💡 Hướng dẫn: Click đúp vào ô bất kỳ để sửa. Sửa xong nhớ bấm nút 'Lưu thay đổi' ở bên dưới!")
        
        try:
            # Kéo data hiện tại về
            df_hien_tai = conn.read(spreadsheet=SHEET_URL, worksheet="Data Gia Phả")
            
            # Hiển thị bảng cho phép chỉnh sửa trực tiếp (ẩn cột ID đi cho đỡ rối mắt)
            df_chinh_sua = st.data_editor(
                df_hien_tai, 
                use_container_width=True,
                num_rows="dynamic", # Cho phép thêm/xóa dòng luôn nếu thích
                disabled=["ID"] # Khóa cột ID lại, không cho sửa để tránh hỏng cây
            )
            
            # Nút lưu dữ liệu
            if st.button("💾 Lưu thay đổi"):
                # Ghi đè dữ liệu mới lên Google Sheet
                conn.update(spreadsheet=SHEET_URL, worksheet="Data Gia Phả", data=df_chinh_sua)
                st.success("Đã cập nhật thay đổi thành công! Qua trang Cây Gia Phả để xem kết quả nha.")
                st.rerun()
                
        except Exception as e:
            st.error("Có lỗi khi tải dữ liệu. Vui lòng kiểm tra lại.")
