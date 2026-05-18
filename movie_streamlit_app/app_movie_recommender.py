import ast
import hashlib
import html
import re
from collections import Counter
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import joblib
import streamlit as st
from deep_translator import GoogleTranslator
from scipy.sparse import csr_matrix, hstack
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, normalize

st.set_page_config(
    page_title="Hệ thống gợi ý phim",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            --main-color: #0f7774;
            --main-light: #e8f7f6;
            --main-soft: #f2fbfa;
            --text-dark: #153332;
            --text-muted: #5f7473;
            --border-soft: rgba(15, 119, 116, 0.18);
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 119, 116, 0.13), transparent 30%),
                linear-gradient(180deg, #ffffff 0%, #f4fbfa 45%, #eef8f7 100%);
            color: var(--text-dark);
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }
        .hero {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 1.7rem 1.8rem;
            background:
                linear-gradient(135deg, rgba(15,119,116,0.96), rgba(28,151,147,0.90)),
                linear-gradient(180deg, #ffffff, #f4fbfa);
            border: 1px solid rgba(15,119,116,0.22);
            box-shadow: 0 16px 38px rgba(15,119,116,0.18);
            margin-bottom: 1.1rem;
        }
        .hero:before {
            content: "";
            position: absolute;
            width: 260px;
            height: 260px;
            right: -80px;
            top: -100px;
            border-radius: 999px;
            background: rgba(255,255,255,0.18);
            pointer-events: none;
        }
        .hero-title {
            font-size: 2.25rem;
            font-weight: 850;
            margin: 0;
            letter-spacing: 0.2px;
            color: #ffffff;
        }
        .section-title {
            font-size: 1.18rem;
            font-weight: 800;
            margin: 0.4rem 0 0.8rem 0;
            color: var(--text-dark);
        }
        .netflix-card {
            background: rgba(255,255,255,0.94);
            border: 1px solid var(--border-soft);
            border-radius: 24px;
            padding: 1rem;
            box-shadow: 0 12px 28px rgba(15,119,116,0.12);
            margin-bottom: 1rem;
        }
        .poster-fallback {
            width: 100%;
            min-height: 320px;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                linear-gradient(180deg, rgba(15,119,116,0.14), rgba(255,255,255,0.96)),
                linear-gradient(135deg, #dff5f4, #ffffff);
            color: var(--main-color);
            font-size: 4rem;
            border: 1px solid rgba(15,119,116,0.16);
        }
        .movie-title {
            font-size: 1.45rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
            color: var(--text-dark);
        }
        .movie-meta {
            color: var(--text-muted);
            line-height: 1.75;
            font-size: 0.97rem;
        }
        .pill {
            display: inline-block;
            margin-right: 0.45rem;
            margin-top: 0.45rem;
            padding: 0.34rem 0.72rem;
            background: rgba(15,119,116,0.10);
            color: var(--main-color);
            border: 1px solid rgba(15,119,116,0.20);
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 650;
        }
        .overview-box {
            margin-top: 0.85rem;
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: var(--main-soft);
            border: 1px solid var(--border-soft);
            color: var(--text-dark);
            line-height: 1.7;
        }
        .search-box {
            border-radius: 24px;
            padding: 1rem;
            background: rgba(255,255,255,0.96);
            border: 1px solid var(--border-soft);
            box-shadow: 0 12px 30px rgba(15,119,116,0.12);
        }
        .info-box {
            border-radius: 20px;
            padding: 1rem 1.05rem;
            background: rgba(255,255,255,0.96);
            border: 1px solid var(--border-soft);
            color: var(--text-dark);
            box-shadow: 0 10px 24px rgba(15,119,116,0.09);
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.96);
            border: 1px solid var(--border-soft);
            border-radius: 18px;
            padding: 0.8rem;
            box-shadow: 0 8px 20px rgba(15,119,116,0.08);
        }
        div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {
            color: var(--text-dark) !important;
        }
        .stTextInput input, .stTextArea textarea {
            background: #ffffff !important;
            color: var(--text-dark) !important;
            border-radius: 14px !important;
            border: 1px solid rgba(15,119,116,0.30) !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--main-color) !important;
            box-shadow: 0 0 0 1px rgba(15,119,116,0.30) !important;
        }
        .stButton > button {
            border-radius: 14px !important;
            border: 1px solid rgba(15,119,116,0.45) !important;
            background: var(--main-color) !important;
            color: white !important;
            font-weight: 700 !important;
        }
        .stButton > button:hover {
            border-color: #0a5f5c !important;
            background: #0a5f5c !important;
            color: white !important;
        }
        section[data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid rgba(15,119,116,0.16);
        }
        .stRadio label, .stSlider label, .stToggle label, .stTextInput label, .stTextArea label {
            color: var(--text-dark) !important;
            font-weight: 650;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🎬 Hệ thống gợi ý phim</div>
    </div>
    """,
    unsafe_allow_html=True,
)

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

SHOW_COLS = [
    "ID",
    "Movie_Title",
    "Release_Year",
    "Weighted_Rating",
    "Genre",
    "Director",
    "Stars",
    "Countries_of_origin",
    "Overview",
    "Poster_URL",
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

# File assets đã được build sẵn bằng build_assets.py.
# Đặt file này cùng thư mục với app để Streamlit chỉ load, không build lại mô hình.
ASSETS_PATH = "movie_recommender_assets.joblib"


@st.cache_resource(show_spinner=False)
def load_sbert_model() -> SentenceTransformer:
    return SentenceTransformer(SBERT_MODEL_NAME)


@st.cache_data(show_spinner=False)
def translate_text_cached(text: str, target: str = "vi") -> str:
    text = str(text).strip()
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception:
        return "[Không dịch được - hãy kiểm tra Internet]"


def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_name_token(name: str) -> str:
    name = str(name).strip().lower()
    name = re.sub(r"[-/]", " ", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.replace(" ", "_")


def try_parse_list_string(text):
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
    if pd.isna(text):
        return ""
    text = str(text).strip()
    if text.lower() in {"", "nan", "unknown", "no description"}:
        return ""
    return normalize_text(text)


def preprocess_tag_list(values, mode="name") -> List[str]:
    cleaned = []
    for v in values:
        token = normalize_name_token(v) if mode == "name" else normalize_text(v)
        if token:
            cleaned.append(token)
    return list(dict.fromkeys(cleaned))


def minmax_scale_safe(series) -> pd.Series:
    s = pd.Series(series).astype(float)
    min_v = s.min()
    max_v = s.max()
    if pd.isna(min_v) or pd.isna(max_v):
        return pd.Series(np.zeros(len(s)), index=s.index)
    if max_v == min_v:
        return pd.Series(np.ones(len(s)), index=s.index)
    return (s - min_v) / (max_v - min_v)


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


@st.cache_data(show_spinner=False)
def prepare_data(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    if file_name.lower().endswith(".csv"):
        df = pd.read_csv(BytesIO(file_bytes))
    elif file_name.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(BytesIO(file_bytes))
    else:
        raise ValueError("Chỉ hỗ trợ file CSV hoặc Excel.")

    df = df.copy()
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


@st.cache_resource(show_spinner=True)
def build_recommender(file_hash: str, file_bytes: bytes, file_name: str):
    df = prepare_data(file_bytes, file_name)
    model = load_sbert_model()

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
        show_progress_bar=False,
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

    return {
        "df": df,
        "sbert_model": model,
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
        "file_hash": file_hash,
    }


@st.cache_resource(show_spinner=False)
def load_prebuilt_assets(assets_path: str = ASSETS_PATH) -> Dict:
    """Load recommender đã được build sẵn, sau đó nạp SBERT để dùng cho truy vấn mô tả."""
    assets = joblib.load(assets_path)

    # Không lưu trực tiếp object SentenceTransformer vào file joblib để tránh file quá nặng.
    # Khi app chạy, chỉ cần load model một lần và cache lại bằng Streamlit.
    if "sbert_model" not in assets:
        assets["sbert_model"] = load_sbert_model()

    return assets


def find_movie_candidates(df: pd.DataFrame, movie_title: str, max_suggestions: int = 12) -> pd.DataFrame:
    query = str(movie_title).strip().lower()
    exact_matches = df[df["Movie_Title_norm"] == query].copy()
    if not exact_matches.empty:
        return exact_matches.sort_values(by=["Weighted_Rating", "Release_Year"], ascending=[False, False])

    partial_matches = df[df["Movie_Title_norm"].str.contains(query, regex=False, na=False)].copy()
    if not partial_matches.empty:
        return partial_matches.sort_values(by=["Weighted_Rating", "Release_Year"], ascending=[False, False]).head(max_suggestions)
    return partial_matches


def resolve_movie_query(df: pd.DataFrame, movie_title: str, release_year: Optional[int] = None):
    query = str(movie_title).strip().lower()
    candidates = df[df["Movie_Title_norm"] == query].copy()
    if release_year is not None:
        candidates_year = candidates[candidates["Release_Year"] == release_year].copy()
        if not candidates_year.empty:
            candidates = candidates_year

    if candidates.empty:
        candidates = df[df["Movie_Title_norm"].str.contains(query, regex=False, na=False)].copy()
        if release_year is not None and not candidates.empty:
            candidates_year = candidates[candidates["Release_Year"] == release_year].copy()
            if not candidates_year.empty:
                candidates = candidates_year

    if candidates.empty:
        return None, None

    candidates = candidates.sort_values(by=["Weighted_Rating", "Release_Year"], ascending=[False, False])
    chosen_idx = candidates.index[0]
    return chosen_idx, candidates


def transform_multilabel_query(raw_text, mlb, mode="name", allowed_set=None):
    items = split_multivalue(raw_text)
    items = preprocess_tag_list(items, mode=mode)
    if allowed_set is not None:
        items = [x for x in items if x in allowed_set]
    row = mlb.transform([items])
    return csr_matrix(row), items


def build_query_vector(assets: Dict, genre="", overview="", director="", stars="", countries_of_origin=""):
    Xq_genre, genre_items = transform_multilabel_query(genre, assets["mlb_genre"], mode="text")
    Xq_director, director_items = transform_multilabel_query(
        director, assets["mlb_director"], mode="name", allowed_set=set(assets["mlb_director"].classes_)
    )
    Xq_stars, stars_items = transform_multilabel_query(
        stars, assets["mlb_stars"], mode="name", allowed_set=set(assets["mlb_stars"].classes_)
    )
    Xq_origin, origin_items = transform_multilabel_query(
        countries_of_origin, assets["mlb_origin"], mode="name"
    )

    overview_clean = preprocess_overview(overview)
    overview_emb = assets["sbert_model"].encode([overview_clean], convert_to_numpy=True, normalize_embeddings=True)
    Xq_overview = csr_matrix(overview_emb)

    active = {}
    if genre_items:
        active["genre"] = WEIGHTS["genre"]
    if overview_clean:
        active["overview"] = WEIGHTS["overview"]
    if director_items:
        active["director"] = WEIGHTS["director"]
    if stars_items:
        active["stars"] = WEIGHTS["stars"]
    if origin_items:
        active["countries_of_origin"] = WEIGHTS["countries_of_origin"]

    if not active:
        raise ValueError("Bạn cần nhập ít nhất một trường: Genre / Overview / Director / Stars / Country.")

    weight_sum = sum(active.values())
    active = {k: v / weight_sum for k, v in active.items()}

    blocks = []
    blocks.append(normalize(Xq_genre, norm="l2") * active["genre"] if "genre" in active else csr_matrix((1, assets["X_genre"].shape[1])))
    blocks.append(normalize(Xq_overview, norm="l2") * active["overview"] if "overview" in active else csr_matrix((1, assets["X_overview"].shape[1])))
    blocks.append(normalize(Xq_director, norm="l2") * active["director"] if "director" in active else csr_matrix((1, assets["X_director"].shape[1])))
    blocks.append(normalize(Xq_stars, norm="l2") * active["stars"] if "stars" in active else csr_matrix((1, assets["X_stars"].shape[1])))
    blocks.append(normalize(Xq_origin, norm="l2") * active["countries_of_origin"] if "countries_of_origin" in active else csr_matrix((1, assets["X_origin"].shape[1])))

    Xq = hstack(blocks, format="csr")
    return normalize(Xq, norm="l2", copy=False)


def recommend_movies_hybrid(
    assets: Dict,
    movie_title: str,
    release_year=None,
    top_n=10,
    candidate_pool=50,
    alpha_similarity=0.8,
    beta_weighted_rating=0.2
):
    df = assets["df"]
    chosen_idx, candidates = resolve_movie_query(df, movie_title, release_year)
    if chosen_idx is None:
        return None, None, None

    selected_movie = df.loc[[chosen_idx], [c for c in SHOW_COLS if c in df.columns]].copy().reset_index(drop=True)

    n_neighbors = min(candidate_pool + 1, len(df))
    distances, indices = assets["nn_model"].kneighbors(assets["X_all"][chosen_idx], n_neighbors=n_neighbors)
    distances = distances.ravel()
    indices = indices.ravel()

    candidate_indices, cosine_scores = [], []
    for dist, idx in zip(distances, indices):
        if idx == chosen_idx:
            continue
        candidate_indices.append(idx)
        cosine_scores.append(1 - dist)
        if len(candidate_indices) == candidate_pool:
            break

    candidate_df = df.loc[candidate_indices, [c for c in SHOW_COLS if c in df.columns]].copy()
    candidate_df["CosineSimilarity"] = cosine_scores
    candidate_df["Weighted_Rating_Norm"] = minmax_scale_safe(candidate_df["Weighted_Rating"])
    candidate_df["FinalScore"] = (
        alpha_similarity * candidate_df["CosineSimilarity"] +
        beta_weighted_rating * candidate_df["Weighted_Rating_Norm"]
    )
    candidate_df = candidate_df.sort_values(
        by=["FinalScore", "CosineSimilarity", "Weighted_Rating", "Release_Year"],
        ascending=[False, False, False, False],
    ).head(top_n).reset_index(drop=True)
    return candidate_df, candidates, selected_movie


def recommend_by_query_rerank(
    assets: Dict,
    genre="",
    overview="",
    director="",
    stars="",
    countries_of_origin="",
    top_n=10,
    candidate_pool=50,
    alpha_similarity=0.7,
    beta_weighted_rating=0.3
):
    Xq = build_query_vector(assets, genre, overview, director, stars, countries_of_origin)
    df = assets["df"]
    n_neighbors = min(candidate_pool, len(df))
    distances, indices = assets["nn_model"].kneighbors(Xq, n_neighbors=n_neighbors)
    distances = distances.ravel()
    indices = indices.ravel()

    candidate_df = df.loc[indices, [c for c in SHOW_COLS if c in df.columns]].copy()
    candidate_df["CosineSimilarity"] = 1 - distances
    candidate_df["Weighted_Rating_Norm"] = minmax_scale_safe(candidate_df["Weighted_Rating"])
    candidate_df["FinalScore"] = (
        alpha_similarity * candidate_df["CosineSimilarity"] +
        beta_weighted_rating * candidate_df["Weighted_Rating_Norm"]
    )
    candidate_df = candidate_df.sort_values(
        by=["FinalScore", "CosineSimilarity", "Weighted_Rating", "Release_Year"],
        ascending=[False, False, False, False],
    ).head(top_n).reset_index(drop=True)
    return candidate_df


def format_field(value) -> str:
    if pd.isna(value):
        return "Không có"
    text = str(value).strip()
    return text if text else "Không có"


def get_file_hash(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()


def poster_or_fallback(poster_url: str):
    if poster_url:
        st.image(poster_url, use_container_width=True)
    else:
        st.markdown('<div class="poster-fallback">🎬</div>', unsafe_allow_html=True)


def render_movie_card(row: pd.Series, rank: Optional[int] = None, show_translation: bool = True):
    title = format_field(row.get("Movie_Title"))
    year = row.get("Release_Year")
    year_text = str(int(year)) if pd.notna(year) else "N/A"
    genre = format_field(row.get("Genre"))
    director = format_field(row.get("Director"))
    stars = format_field(row.get("Stars"))
    origin = format_field(row.get("Countries_of_origin"))
    overview = format_field(row.get("Overview"))
    weighted_rating = row.get("Weighted_Rating")
    weighted_text = f"{weighted_rating:.2f}" if pd.notna(weighted_rating) else "N/A"
    cosine = row.get("CosineSimilarity")
    cosine_text = f"{cosine:.3f}" if pd.notna(cosine) else None
    final_score = row.get("FinalScore")
    final_text = f"{final_score:.3f}" if pd.notna(final_score) else None
    poster_url = format_field(row.get("Poster_URL"))
    poster_url = "" if poster_url == "Không có" else poster_url

    translated = ""
    if show_translation and overview not in {"", "Không có"}:
        translated = translate_text_cached(overview, target="vi")

    with st.container():
        st.markdown('<div class="netflix-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2.25], vertical_alignment="top")
        with c1:
            poster_or_fallback(poster_url)
        with c2:
            header = f"#{rank} · {title}" if rank is not None else title
            st.markdown(f'<div class="movie-title">{html.escape(header)}</div>', unsafe_allow_html=True)

            pills = [f"📅 {year_text}", f"⭐ Rating: {weighted_text}"]
            if cosine_text is not None:
                pills.append(f"🎯 Similarity: {cosine_text}")
            if final_text is not None:
                pills.append(f"🏆 Final: {final_text}")

            st.markdown("".join([f'<span class="pill">{html.escape(p)}</span>' for p in pills]), unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="movie-meta" style="margin-top:0.75rem;">
                    <b>Genre:</b> {html.escape(genre)}<br>
                    <b>Director:</b> {html.escape(director)}<br>
                    <b>Stars:</b> {html.escape(stars)}<br>
                    <b>Country:</b> {html.escape(origin)}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="overview-box"><b>Overview (EN):</b><br>{html.escape(overview)}</div>',
                unsafe_allow_html=True,
            )
            if translated:
                st.markdown(
                    f'<div class="overview-box"><b>Dịch tiếng Việt:</b><br>{html.escape(translated)}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)


def render_movie_cards(result_df: pd.DataFrame, show_translation: bool = True):
    if result_df is None or result_df.empty:
        st.warning("Chưa có kết quả để hiển thị.")
        return
    for idx, row in result_df.iterrows():
        render_movie_card(row, rank=idx + 1, show_translation=show_translation)


with st.sidebar:
    st.header("⚙️ Cấu hình")
    candidate_pool = st.slider("Candidate pool", 20, 100, 50, 5)
    top_n = st.slider("Số phim gợi ý", 5, 20, 10, 1)
    alpha_similarity = st.slider("Trọng số Similarity", 0.0, 1.0, 0.8, 0.05)
    beta_default = round(1.0 - alpha_similarity, 2)
    beta_weighted_rating = st.slider("Trọng số Weighted Rating", 0.0, 1.0, beta_default, 0.05)
    show_translation = st.toggle("Dịch overview sang tiếng Việt", value=True)


try:
    assets = load_prebuilt_assets(ASSETS_PATH)
    st.success("Đã tải xong mô hình.")
except FileNotFoundError:
    st.error(
        f"Không tìm thấy file `{ASSETS_PATH}`. "
        "Hãy chạy lệnh: `python build_assets.py --data <duong_dan_file_du_lieu>` trước."
    )
    st.stop()
except Exception as exc:
    st.error(f"Không thể tải mô hình đã build sẵn: {exc}")
    st.stop()

df = assets["df"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Số phim", f"{len(df):,}")
m2.metric("Số genre", f"{len(assets['mlb_genre'].classes_):,}")
m3.metric("Director hợp lệ", f"{len(assets['mlb_director'].classes_):,}")
m4.metric("Stars giữ lại", f"{len(assets['mlb_stars'].classes_):,}")

mode = st.radio(
    "Chọn chế độ gợi ý",
    ["Gợi ý theo tên phim", "Gợi ý theo thuộc tính / mô tả"],
    horizontal=True,
)

left, right = st.columns([1.35, 0.85], vertical_alignment="top")

with left:
    st.markdown('<div class="section-title">🔎 Nhập nội dung phim cần tìm kiếm</div>', unsafe_allow_html=True)
    st.markdown('<div class="search-box">', unsafe_allow_html=True)

    if mode == "Gợi ý theo tên phim":
        st.markdown("### 🍿 Nhập nội dung phim cần tìm kiếm")
        movie_title = st.text_input(
            "Tên phim hoặc nội dung phim",
            placeholder="Ví dụ: Inception, Interstellar, The Batman...",
        )
        year_col1, year_col2 = st.columns([1, 1])
        with year_col1:
            release_year_input = st.text_input(
                "Năm phát hành (không bắt buộc)",
                placeholder="Ví dụ: 2014"
            )
        with year_col2:
            st.write("")
            submit = st.button("✨ Gợi ý theo tên phim", use_container_width=True)

        if movie_title:
            suggestions = find_movie_candidates(df, movie_title)
            if not suggestions.empty:
                preview_cols = [c for c in ["Movie_Title", "Release_Year", "Weighted_Rating"] if c in suggestions.columns]
                with st.expander("Xem ứng viên tìm thấy trong dữ liệu"):
                    st.dataframe(suggestions[preview_cols].head(10), use_container_width=True, hide_index=True)

        if submit:
            if not movie_title.strip():
                st.warning("Bạn cần nhập tên phim trước.")
            else:
                try:
                    year_value = int(release_year_input) if str(release_year_input).strip() else None
                except ValueError:
                    year_value = None

                results, matched, selected_movie = recommend_movies_hybrid(
                    assets,
                    movie_title=movie_title,
                    release_year=year_value,
                    top_n=top_n,
                    candidate_pool=candidate_pool,
                    alpha_similarity=alpha_similarity,
                    beta_weighted_rating=beta_weighted_rating,
                )

                if results is None:
                    st.error("Không tìm thấy phim phù hợp trong dữ liệu.")
                else:
                    st.session_state["results"] = results
                    st.session_state["selected_movie"] = selected_movie
                    st.session_state["matched"] = matched[[c for c in ["Movie_Title", "Release_Year", "Weighted_Rating"] if c in matched.columns]].head(10)
                    st.session_state["mode_used"] = mode

    else:
        st.markdown("### 🎯 Nhập nội dung phim cần tìm kiếm")
        st.caption("Bạn có thể nhập thể loại, mô tả nội dung, đạo diễn, diễn viên hoặc quốc gia.")
        genre = st.text_input("Genre", placeholder="Action|Sci-Fi hoặc Drama, Crime")
        director = st.text_input("Director", placeholder="Christopher Nolan")
        stars = st.text_input("Stars", placeholder="Leonardo DiCaprio|Joseph Gordon-Levitt")
        countries_of_origin = st.text_input("Country", placeholder="United States of America")
        overview = st.text_area(
            "Overview / mô tả nội dung",
            placeholder="Ví dụ: A thief enters dreams to steal secrets and is given a dangerous mission...",
            height=180,
        )
        submit = st.button("🚀 Tìm phim theo thuộc tính", use_container_width=True)

        if submit:
            try:
                results = recommend_by_query_rerank(
                    assets,
                    genre=genre,
                    overview=overview,
                    director=director,
                    stars=stars,
                    countries_of_origin=countries_of_origin,
                    top_n=top_n,
                    candidate_pool=candidate_pool,
                    alpha_similarity=alpha_similarity,
                    beta_weighted_rating=beta_weighted_rating,
                )
                st.session_state["results"] = results
                st.session_state["selected_movie"] = None
                st.session_state["matched"] = None
                st.session_state["mode_used"] = mode
            except Exception as exc:
                st.error(str(exc))

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">🧠 Mô hình & ý nghĩa điểm số</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-box">
            <b>Final</b> là điểm xếp hạng cuối cùng của phim gợi ý.<br><br>
            Công thức:
            <code>FinalScore = alpha × CosineSimilarity + beta × Weighted_Rating_Norm</code><br><br>
            - <b>Similarity</b>: phim giống nội dung tìm kiếm đến mức nào<br>
            - <b>Weighted_Rating_Norm</b>: điểm đánh giá phim, đã chuẩn hóa về khoảng 0 → 1<br>
            - <b>Final</b>: kết hợp giữa <i>độ giống</i> và <i>độ hay/chất lượng</i><br><br>
            Ví dụ phim có Similarity cao nhưng rating thấp thì Final có thể không cao bằng phim vừa giống vừa có rating tốt.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">💡</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-box">
            - Muốn phim giống một phim cụ thể: dùng <b>Gợi ý theo tên phim</b>.<br>
            - Chỉ có ý tưởng nội dung: dùng <b>Gợi ý theo thuộc tính / mô tả</b>.<br>
            - Bật dịch để xem <b>Overview tiếng Việt</b> cho phim được chọn và phim gợi ý.
        </div>
        """,
        unsafe_allow_html=True,
    )


if st.session_state.get("selected_movie") is not None:
    st.markdown('<div class="section-title">🎥 Chi tiết phim bạn dùng để tìm</div>', unsafe_allow_html=True)
    selected_df = st.session_state["selected_movie"]
    if not selected_df.empty:
        render_movie_card(selected_df.iloc[0], rank=None, show_translation=show_translation)

if "results" in st.session_state:
    result_df = st.session_state["results"]
    st.markdown('<div class="section-title">🍿 Danh sách phim gợi ý</div>', unsafe_allow_html=True)
    render_movie_cards(result_df, show_translation=show_translation)

    with st.expander("Xem bảng dữ liệu kết quả"):
        st.dataframe(result_df, use_container_width=True, hide_index=True)
