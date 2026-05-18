# 🎬 Global Film Analytics Dashboard

Một dashboard tương tác được thiết kế để phân tích xu hướng của thị trường điện ảnh toàn cầu giai đoạn 2020-2025, dựa trên bộ dữ liệu hơn 63.000 bản ghi từ IMDb. Báo cáo này giúp các nhà phân tích, nhà sản xuất và phát hành phim có cái nhìn toàn cảnh về bức tranh điện ảnh, từ đó đưa ra các quyết định chiến lược đầu tư, sản xuất và phân phối nội dung hiệu quả.

## 📈 Dashboard Preview

🔗 [Xem Dashboard tương tác trực tiếp tại đây](https://public.tableau.com/app/profile/ng.c.nhi.ng/viz/TranLeDiemMy_DangNgocNhi/Story1) 

*(Chèn ảnh tổng quan của Dashboard)*
![Dashboard Preview](assets/01_overview_dashboard.png)

## 📊 Key Features

* [cite_start]**Tổng quan thị trường (Overview):** Theo dõi biến động về tổng số phim, tổng doanh thu và điểm đánh giá trung bình qua các năm[cite: 2161].
* [cite_start]**Phân tích Thể loại (Genre Analytics):** Đánh giá hiệu suất của các thể loại dựa trên số lượng phát hành, doanh thu trung bình và mức độ quan tâm của khán giả[cite: 2241, 2248].
* [cite_start]**Phân tích Địa lý (Geographic Analytics):** Khám phá sự khác biệt và lợi thế cạnh tranh giữa các thị trường điện ảnh toàn cầu[cite: 2282, 2283].
* [cite_start]**Phân tích Nhân sự (Star & Director Analytics):** Đánh giá hiệu quả của đạo diễn và diễn viên thông qua số lượng phim tham gia, lượng bình chọn và điểm số trung bình[cite: 2301, 2396].
* **Bộ lọc tương tác đa chiều:** Cho phép lọc chéo dữ liệu linh hoạt theo Năm, Thể loại, Quốc gia, Đạo diễn và Diễn viên.

## 🧹 Data Preparation

Báo cáo được xây dựng trên bộ dữ liệu gốc cào từ IMDb. Quá trình làm sạch và chuyển đổi chuyên sâu được thực hiện thông qua file `02. Tiền xử lý dữ liệu.ipynb` với các bước chính:
* [cite_start]**Làm sạch và Chuẩn hóa:** Tách quốc gia phát hành khỏi cột ngày tháng [cite: 1874][cite_start], chuyển đổi thời lượng (`Runtime`) sang số phút [cite: 1994][cite_start], và chuẩn hóa doanh thu (`Gross`), số lượt đánh giá (`Votes`) về định dạng số để tính toán[cite: 1936, 2017].
* [cite_start]**Xử lý giá trị thiếu (Missing Values):** Thay thế dữ liệu thiếu hợp lý (ví dụ: điền thời lượng phim theo trung vị của từng thể loại [cite: 2040][cite_start], gán "Unknown" cho Đạo diễn/Diễn viên bị trống [cite: 2026]).
* [cite_start]**Kỹ thuật đặc trưng (Feature Engineering):** Tính toán chỉ số `Weighted_Rating` dựa trên thuật toán của IMDb nhằm tạo ra điểm đánh giá công bằng hơn dựa trên số lượng bình chọn[cite: 1949].
* [cite_start]**Tối ưu mô hình dữ liệu (Data Modeling):** Tách dữ liệu đa trị thành 5 bảng (Fact và Dimension tables) bao gồm `movies_main`, `movies_genre`, `movies_director`, `movies_stars`, và `movies_country` nhằm thiết lập Relationship chuẩn chỉnh, hỗ trợ trực quan hóa đa chiều[cite: 2096, 2097].

## 📁 Tools & Technologies

* **Trực quan hóa:** Tableau (Sử dụng biểu đồ bong bóng, treemap, heatmap, scatter plot).
* **Tiền xử lý dữ liệu:** Python (Pandas, Numpy, Regex) xử lý trên Jupyter Notebook.
* **Nguồn dữ liệu:** Nền tảng IMDb.

## 🧠 Data Insights

Dashboard hỗ trợ người dùng khám phá ra các Insight giá trị, được trình bày chi tiết trong báo cáo `DASHBOARD MOVIES.docx`:
* [cite_start]**Lợi thế Thể loại:** Action, Adventure và Animation là những nhóm dẫn dắt doanh thu phòng vé nhờ hiệu suất bình quân cực cao, trong khi Drama và Comedy đóng vai trò duy trì nguồn cung ổn định về số lượng[cite: 2246, 2248].
* [cite_start]**Sự phân hóa Địa lý:** Mỹ và Anh dẫn đầu tuyệt đối về quy mô phát hành, nhưng các nước Châu Á (như Nhật Bản với Anime, Trung Quốc với Action) lại thể hiện lợi thế rõ rệt về chất lượng đánh giá (Rating trung bình cao) trong các dòng phim ngách[cite: 2283, 2284].
* **Nghịch lý Nhân sự (Đạo diễn/Diễn viên):** Sản lượng phim tham gia cao không đồng nghĩa với chất lượng tốt. [cite_start]Có những nhân sự phủ sóng cực mạnh (đóng hàng chục phim) nhưng rating chỉ ở mức thấp, trong khi những người có chọn lọc lại thu hút lượng bình chọn và điểm đánh giá vượt trội[cite: 2304, 2307].

## 📂 Files Included

* `IMDb_Analytics_Dashboard.twb`  – File Project của Dashboard.
* `notebook/02. Tiền xử lý dữ liệu.ipynb` – Source code Python chứa toàn bộ logic làm sạch dữ liệu.
* `DASHBOARD MOVIES.pdf` – Báo cáo phân tích chuyên sâu các insight rút ra từ Dashboard.
* `assets/` – Hình ảnh giao diện thu nhỏ của báo cáo.