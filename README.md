# 🎬 IMDb Movie Trends Analytics & Content-Based Recommendation System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=Tableau&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

## 📌 Giới thiệu dự án
[cite_start]Dự án này tập trung phân tích xu hướng điện ảnh giai đoạn 2020-2025 dựa trên bộ dữ liệu hơn 63.000 bản ghi từ nền tảng IMDb[cite: 8, 331, 332]. [cite_start]Dự án được triển khai nhằm giải quyết hai bài toán chính: trực quan hóa thị trường điện ảnh và xây dựng hệ thống gợi ý phim (Content-Based Filtering)[cite: 61, 69].

**Thành viên thực hiện - Nhóm 3:**
* [cite_start]Trần Lê Diễm My [cite: 15, 16]
* [cite_start]Đặng Ngọc Nhi [cite: 17]
* [cite_start]*Đơn vị:* Khoa Thương mại điện tử, Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE)[cite: 1, 2, 4].

## 🎯 Các tính năng nổi bật
* [cite_start]**Phân tích thị trường (Data Analytics):** Xây dựng 5 dashboard trực quan hóa dữ liệu theo thời gian, thể loại, quốc gia, đạo diễn và diễn viên[cite: 77, 294, 295, 296, 297].
* [cite_start]**Hệ thống gợi ý phim (Recommender System):** Ứng dụng mô hình ngôn ngữ lớn SBERT để xử lý ngữ nghĩa phần tóm tắt phim[cite: 69]. [cite_start]Sử dụng thuật toán KNN và độ đo Cosine Similarity để truy xuất phim tương đồng[cite: 69, 208].
* [cite_start]**Cơ chế xếp hạng lại (Hybrid Reranking):** Kết hợp độ tương đồng nội dung và chỉ số Weighted Rating (chất lượng đánh giá) để đưa ra Top 10 phim gợi ý tối ưu nhất[cite: 111, 238, 315].
* [cite_start]**Triển khai (Deployment):** Ứng dụng web tương tác được xây dựng bằng Streamlit, cho phép tìm kiếm phim bằng tên hoặc truy vấn tự do[cite: 70, 71].

## 🛠️ Công nghệ sử dụng
* [cite_start]**Thu thập dữ liệu:** Python (Selenium, BeautifulSoup, Requests)[cite: 101, 286].
* [cite_start]**Xử lý dữ liệu:** Pandas, NumPy[cite: 83, 321].
* [cite_start]**Trực quan hóa:** Tableau [cite: 108, 325].
* [cite_start]**Machine Learning:** Scikit-learn, Sentence-Transformers (SBERT)[cite: 323, 324].
* [cite_start]**Triển khai:** Streamlit[cite: 112, 327].

## 📊 1. Trực quan hóa dữ liệu (Dashboards)
[cite_start]Dự án cung cấp cái nhìn toàn cảnh và chi tiết về thị trường phim thông qua các phân tích về quy mô, doanh thu, điểm đánh giá và cơ cấu thể loại[cite: 1193].

**🔗 [Xem Dashboard tại đây](https://public.tableau.com/app/profile/ng.c.nhi.ng/viz/TranLeDiemMy_DangNgocNhi/Story1)**

> `<img src="assets\01_overview_dashboard.png" width="800">`

## 🤖 2. Hệ thống gợi ý phim (Recommendation Engine)
[cite_start]Kiến trúc hệ thống được chia làm 2 giai đoạn chính[cite: 304]:
1. [cite_start]**Truy xuất ứng viên (Retrieval):** Mã hóa Multi-hot cho các thuộc tính phân loại (thể loại, đạo diễn, diễn viên, quốc gia) và SBERT cho văn bản[cite: 196, 941, 946]. [cite_start]Lọc top 50 ứng viên gần nhất bằng KNN[cite: 975].
2. [cite_start]**Xếp hạng lại (Reranking):** Sắp xếp lại danh sách ứng viên dựa trên điểm tổng hợp `FinalScore` với trọng số: 80% độ tương đồng nội dung (Similarity) và 20% chất lượng phim (Weighted Rating)[cite: 251, 258, 1013].

> `<img src="assets/streamlit_app.png" width="800">`

## 📂 Cấu trúc thư mục (Repository Structure)
```text
├── data/
│   ├── raw/                 # Dữ liệu cào từ IMDb ban đầu
│   └── processed/           # Dữ liệu sau khi làm sạch 
├── notebooks/
│   ├── 01. Thu thập dữ liệu.ipynb
│   ├── 02_Tiền xử lý dữ liệu.ipynb
│   ├── 03_Vẽ chart.ipynb
│   └── 04_Hệ thống đề xuất.ipynb
├── movie_streamlit_app/
│   └── app_movie_recommender.py               # Source code giao diện Streamlit
├── assets/
│   └── ...                  # Hình ảnh minh họa cho README
├── requirements.txt
└── README.md