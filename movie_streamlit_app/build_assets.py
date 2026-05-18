import ast
import argparse
import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, normalize


REQUIRED_COLS = [
    "Movie_Title",
    "Genre",
    "Director",
    "Stars",
    "Overview",
    "Release_Year",
    "Weighted_Rating",
    "Countries_of_origin",
]

WEIGHTS = {
    "genre": 0.4,
    "overview": 0.4,
    "director": 0.05,
    "stars": 0.05,
    "countries_of_origin": 0.1,
}

SBERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
POSTER_CANDIDATE_COLS = [
    "Poster_URL", "Poster", "poster", "poster_url", "poster_path",
    "Image_URL", "image_url", "Backdrop_URL", "backdrop_url"
]


def normalize_text(text: str) -> str:
    """Chuẩn hóa văn bản: chuyển về chữ thường, bỏ ký tự đặc biệt và khoảng trắng thừa."""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_name_token(name: str) -> str:
    """Chuẩn hóa tên riêng như đạo diễn/diễn viên/quốc gia thành một token thống nhất."""
    name = str(name).strip().lower()
    name = re.sub(r"[-/]", " ", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.replace(" ", "_")


def try_parse_list_string(text):
    """Thử chuyển chuỗi dạng "['Action', 'Drama']" thành list Python."""
    if pd.isna(text):
        return None
    text = str(text).strip()
    if not text:
        return None
    if text.startswith("[") and text.endswith("]"):
        try:
            value = ast.literal_eval(text)
            if isinstance(value, list):
                return [str(x).strip() for x in value if str(x).strip()]
        except Exception:
            return None
    return None


def split_multivalue(text: str) -> List[str]:
    """Tách một ô dữ liệu có một/nhiều giá trị thành danh sách các giá trị riêng lẻ."""
    if pd.isna(text):
        return []

    parsed = try_parse_list_string(text)
    if parsed is not None:
        raw_items = parsed
    else:
        text = str(text).strip()
        if text == "":
            return []
        if "|" in text:
            raw_items = text.split("|")
        elif "," in text:
            raw_items = text.split(",")
        else:
            raw_items = [text]

    cleaned = []
    for item in raw_items:
        item = str(item).strip()
        if item.lower() in {"", "nan", "unknown", "none"}:
            continue
        cleaned.append(item)
    return cleaned


def preprocess_overview(text: str) -> str:
    """Làm sạch phần mô tả phim trước khi đưa vào SBERT."""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    if text.lower() in {"", "nan", "unknown", "no description"}:
        return ""
    return normalize_text(text)


def preprocess_tag_list(values, mode="name") -> List[str]:
    """Làm sạch danh sách nhãn và loại bỏ nhãn trùng lặp."""
    cleaned = []
    for v in values:
        token = normalize_name_token(v) if mode == "name" else normalize_text(v)
        if token:
            cleaned.append(token)
    return list(dict.fromkeys(cleaned))


def validate_df(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
    return len(missing_cols) == 0, missing_cols


def extract_poster_url(row) -> str:
    for col in POSTER_CANDIDATE_COLS:
        if col in row and pd.notna(row[col]):
            value = str(row[col]).strip()
            if not value:
                continue
            if value.startswith("http://") or value.startswith("https://"):
                return value
            if value.startswith("/"):
                return f"https://image.tmdb.org/t/p/w500{value}"
    return ""


def get_file_hash(data_path: Path) -> str:
    return hashlib.md5(data_path.read_bytes()).hexdigest()


def read_movie_data(data_path: Path) -> pd.DataFrame:
    if data_path.suffix.lower() == ".csv":
        return pd.read_csv(data_path)
    if data_path.suffix.lower() in {".xls", ".xlsx"}:
        return pd.read_excel(data_path)
    raise ValueError("Chỉ hỗ trợ file CSV hoặc Excel.")


def prepare_data(data_path: Path) -> pd.DataFrame:
    """Đọc dữ liệu phim, kiểm tra cột bắt buộc và tiền xử lý các cột cần dùng."""
    df = read_movie_data(data_path).copy()

    ok, missing = validate_df(df)
    if not ok:
        raise ValueError(f"Thiếu cột dữ liệu bắt buộc: {missing}")

    if "ID" not in df.columns:
        df.insert(0, "ID", range(1, len(df) + 1))

    df["Movie_Title"] = df["Movie_Title"].astype(str).fillna("")
    df["Movie_Title_norm"] = df["Movie_Title"].apply(normalize_text)
    df["Overview"] = df["Overview"].fillna("").astype(str)
    df["Overview_clean"] = df["Overview"].apply(preprocess_overview)

    for col in ["Genre", "Director", "Stars", "Countries_of_origin"]:
        df[col] = df[col].fillna("").astype(str)

    if "Poster_URL" not in df.columns:
        df["Poster_URL"] = ""

    df["Poster_URL"] = df.apply(extract_poster_url, axis=1)

    df["Genre_list"] = df["Genre"].apply(split_multivalue).apply(lambda x: preprocess_tag_list(x, mode="text"))
    df["Director_list"] = df["Director"].apply(split_multivalue).apply(lambda x: preprocess_tag_list(x, mode="name"))
    df["Stars_list"] = df["Stars"].apply(split_multivalue).apply(lambda x: preprocess_tag_list(x, mode="name"))
    df["Countries_of_origin_list"] = df["Countries_of_origin"].apply(split_multivalue).apply(lambda x: preprocess_tag_list(x, mode="name"))

    director_counter = Counter()
    for items in df["Director_list"]:
        director_counter.update(items)
    valid_directors = {name for name, cnt in director_counter.items() if cnt >= 3}

    star_counter = Counter()
    for items in df["Stars_list"]:
        star_counter.update(items)
    top_300_stars = {name for name, _ in star_counter.most_common(300)}

    df["Director_list_f"] = df["Director_list"].apply(lambda items: [x for x in items if x in valid_directors])
    df["Stars_list_f"] = df["Stars_list"].apply(lambda items: [x for x in items if x in top_300_stars])

    df["Weighted_Rating"] = pd.to_numeric(df["Weighted_Rating"], errors="coerce")
    df["Release_Year"] = pd.to_numeric(df["Release_Year"], errors="coerce")
    df["Weighted_Rating"] = df["Weighted_Rating"].fillna(df["Weighted_Rating"].median())

    return df.reset_index(drop=True)


def build_assets(data_path: Path):
    """Build toàn bộ vector đặc trưng và KNN một lần, sau đó trả về assets để lưu."""
    df = prepare_data(data_path)
    model = SentenceTransformer(SBERT_MODEL_NAME)

    mlb_genre = MultiLabelBinarizer()
    X_genre = csr_matrix(mlb_genre.fit_transform(df["Genre_list"]))

    mlb_director = MultiLabelBinarizer()
    X_director = csr_matrix(mlb_director.fit_transform(df["Director_list_f"]))

    mlb_stars = MultiLabelBinarizer()
    X_stars = csr_matrix(mlb_stars.fit_transform(df["Stars_list_f"]))

    mlb_origin = MultiLabelBinarizer()
    X_origin = csr_matrix(mlb_origin.fit_transform(df["Countries_of_origin_list"]))

    overview_texts = df["Overview_clean"].fillna("").astype(str).tolist()
    overview_embeddings = model.encode(
        overview_texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    X_overview = csr_matrix(overview_embeddings)

    X_genre_n = normalize(X_genre, norm="l2", copy=True)
    X_director_n = normalize(X_director, norm="l2", copy=True)
    X_stars_n = normalize(X_stars, norm="l2", copy=True)
    X_origin_n = normalize(X_origin, norm="l2", copy=True)
    X_overview_n = normalize(X_overview, norm="l2", copy=True)

    X_all = hstack(
        [
            X_genre_n * WEIGHTS["genre"],
            X_overview_n * WEIGHTS["overview"],
            X_director_n * WEIGHTS["director"],
            X_stars_n * WEIGHTS["stars"],
            X_origin_n * WEIGHTS["countries_of_origin"],
        ],
        format="csr",
    )
    X_all = normalize(X_all, norm="l2", copy=False)

    nn_model = NearestNeighbors(metric="cosine", algorithm="brute")
    nn_model.fit(X_all)

    # Không lưu object SentenceTransformer vào file joblib để file nhẹ và ít lỗi hơn.
    return {
        "df": df,
        "sbert_model_name": SBERT_MODEL_NAME,
        "mlb_genre": mlb_genre,
        "mlb_director": mlb_director,
        "mlb_stars": mlb_stars,
        "mlb_origin": mlb_origin,
        "X_genre": X_genre,
        "X_director": X_director,
        "X_stars": X_stars,
        "X_origin": X_origin,
        "X_overview": X_overview,
        "X_all": X_all,
        "nn_model": nn_model,
        "file_hash": get_file_hash(data_path),
        "weights": WEIGHTS,
    }


def main():
    parser = argparse.ArgumentParser(description="Build sẵn assets cho MovieMate AI.")
    parser.add_argument("--data", required=True, help="Đường dẫn file dữ liệu phim CSV/XLSX.")
    parser.add_argument("--output", default="movie_recommender_assets.joblib", help="Tên file assets đầu ra.")
    args = parser.parse_args()

    data_path = Path(args.data)
    output_path = Path(args.output)

    if not data_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {data_path}")

    print(f"Đang đọc dữ liệu: {data_path}")
    assets = build_assets(data_path)

    print(f"Đang lưu assets vào: {output_path}")
    joblib.dump(assets, output_path, compress=3)

    print("Hoàn tất.")
    print(f"Số phim: {len(assets['df']):,}")
    print(f"Số genre: {len(assets['mlb_genre'].classes_):,}")
    print(f"Số director hợp lệ: {len(assets['mlb_director'].classes_):,}")
    print(f"Số stars giữ lại: {len(assets['mlb_stars'].classes_):,}")


if __name__ == "__main__":
    main()
