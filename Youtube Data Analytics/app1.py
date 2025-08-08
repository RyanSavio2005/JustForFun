import streamlit as st
import pandas as pd
import tempfile
import os
from fetch_info import get_video_info, get_all_videos_from_playlist
from ml_model import get_trained_model_and_vectorizer, predict_category_from_text
from youtube_api import YOUTUBE_API_KEY
from jinja2 import Environment, FileSystemLoader
import altair as alt

st.set_page_config(page_title="YouTube Upload Date Finder (Full)", layout="wide")
st.title("📅 YouTube Upload Date Finder — Full Package")

st.markdown("""
Features included:
- Fetch metadata (pytube / youtube-dl fallback / YouTube Data API optional)
- Playlist support
- Thumbnail previews
- Whisper transcription (optional) to improve ML classification
- Category prediction (simple TF-IDF + Naive Bayes)
- Charts, filtering, and HTML report export (thumbnails included)
""")

urls_input = st.text_area("Paste YouTube video or playlist URLs (one per line):", height=200)
urls = [u.strip() for u in urls_input.splitlines() if u.strip()]

use_transcription = st.checkbox("Use audio transcription (Whisper) to improve classification", value=False)
use_api = st.checkbox("Prefer YouTube Data API when available", value=bool(YOUTUBE_API_KEY))
st.sidebar.markdown("### Options")
st.sidebar.write(f"YouTube Data API key present: {'Yes' if bool(YOUTUBE_API_KEY) else 'No'}")

@st.cache_resource
def load_model():
    return get_trained_model_and_vectorizer()

model, vectorizer = load_model()

if st.button("Fetch Video Info"):
    if not urls:
        st.warning("Please paste at least one URL.")
    else:
        all_info = []
        progress = st.progress(0)
        total_steps = len(urls)
        step = 0
        
        for url in urls:
            # Playlist?
            if "playlist" in url or "list=" in url:
                vids = get_all_videos_from_playlist(url)
                for v in vids:
                    info = get_video_info(v, prefer_api=use_api)
                    if "error" not in info:
                        if use_transcription:
                            info["transcript"] = info.get("transcript", "")
                        info["predicted_category"] = predict_category_from_text(
                            info.get("title", "") + " " + info.get("description", "") + " " + info.get("transcript", ""),
                            model, vectorizer
                        )
                        all_info.append(info)
            else:
                info = get_video_info(url, prefer_api=use_api)
                if "error" not in info:
                    if use_transcription:
                        info["transcript"] = info.get("transcript", "")
                    info["predicted_category"] = predict_category_from_text(
                        info.get("title", "") + " " + info.get("description", "") + " " + info.get("transcript", ""),
                        model, vectorizer
                    )
                    all_info.append(info)
            step += 1
            progress.progress(min(step / total_steps, 1.0))
        
        df = pd.DataFrame(all_info)
        st.success(f"Fetched metadata for {len(df)} videos")

        if df.empty:
            st.info("No valid video data found.")
        else:
            # Convert date and views to right types
            df['publish_date'] = pd.to_datetime(df['publish_date'], errors='coerce')
            df['views'] = pd.to_numeric(df.get('views', pd.Series()), errors='coerce')

            st.subheader("Thumbnails & Basic Info")
            cols = st.columns(2)
            for idx, row in df.iterrows():
                with cols[idx % 2]:
                    st.image(row.get('thumbnail_url', 'default_thumbnail.png'), width=320)  # Default image if missing
                    st.markdown(f"**{row.get('title', 'No Title Available')}**")
                    st.markdown(f"*{row.get('author', 'Unknown Author')}* • {row['publish_date'].date() if pd.notnull(row['publish_date']) else 'unknown'}")
                    st.markdown(f"Views: {int(row['views']) if pd.notnull(row['views']) else 'N/A'}")
                    st.markdown("---")

            st.subheader("Video Data Table")
            st.dataframe(df)

            # Keyword filter
            st.subheader("🔍 Keyword filter")
            keyword = st.text_input("Enter keyword to filter title/description/transcript:")
            if keyword:
                mask = df['title'].str.contains(keyword, case=False, na=False) | \
                       df['description'].str.contains(keyword, case=False, na=False) | \
                       df.get('transcript', pd.Series()).str.contains(keyword, case=False, na=False)
                filtered = df[mask]
                st.write(f"Found {len(filtered)} matching videos")
                st.dataframe(filtered)
            else:
                filtered = df

            # Charts
            if 'views' in df.columns and df['publish_date'].notna().any():
                st.subheader("📈 Views vs Upload Date")
                chart = alt.Chart(df).mark_circle(size=60).encode(
                    x='publish_date:T',
                    y='views:Q',
                    tooltip=['title', 'views', 'publish_date']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

            if 'predicted_category' in df.columns:
                st.subheader("🧠 Predicted Category Distribution")
                cat_chart = alt.Chart(df).mark_bar().encode(
                    x='predicted_category:N',
                    y='count():Q',
                    tooltip=['predicted_category']
                )
                st.altair_chart(cat_chart, use_container_width=True)

            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "youtube_video_data.csv", "text/csv")

            # HTML report generation
            if st.button("🖨️ Generate HTML report (with thumbnails)"):
                env = Environment(loader=FileSystemLoader("templates"))
                template = env.get_template("report_template.html")
                html = template.render(videos=df.fillna('').to_dict(orient='records'))
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
                tmp.write(html.encode('utf-8'))
                tmp.flush()
                tmp.close()
                st.success("HTML report generated successfully!")

