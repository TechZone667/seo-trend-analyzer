
import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
import base64
import io

st.set_page_config(page_title="SEO Trend Analyzer", layout="wide")

st.markdown("""
    <style>
    .platform-icons {
        display: flex;
        justify-content: space-evenly;
        margin: 20px 0;
    }
    .platform-icons img {
        height: 40px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 SEO Trend Analyzer – Mobile Ready")
st.markdown("Analyze search interest and social relevance of products/services across Google & major platforms.")

st.markdown('<div class="platform-icons">'
            '<img src="https://upload.wikimedia.org/wikipedia/commons/4/4f/Google_Ads_logo.svg">'
            '<img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg">'
            '<img src="https://upload.wikimedia.org/wikipedia/en/9/9f/Twitter_bird_logo_2012.svg">'
            '<img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png">'
            '<img src="https://upload.wikimedia.org/wikipedia/en/7/75/YouTube_social_white_squircle.svg">'
            '<img src="https://upload.wikimedia.org/wikipedia/en/0/0a/TikTok_logo.svg">'
            '</div>', unsafe_allow_html=True)

keywords_input = st.text_input("Enter keywords (comma-separated):", "solar panels, electric bikes")
timeframe = st.selectbox("Select time range:", ["now 7-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y"])
region = st.text_input("Enter region code (e.g., US, GB, NG, IN, KE) or leave blank for worldwide:", "")

if st.button("Analyze"):
    try:
        st.info("Fetching trends from Google...")
        pytrends = TrendReq(hl='en-US', tz=360)

        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        pytrends.build_payload(keywords, timeframe=timeframe, geo=region)

        data = pytrends.interest_over_time()
        if not data.empty:
            st.subheader("📊 Interest Over Time")
            fig = px.line(data.reset_index(), x="date", y=keywords,
                          labels={"value": "Search Interest", "date": "Date"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected keywords/timeframe.")

        st.subheader("🔍 Related Queries")
        related_queries = pytrends.related_queries()
        for kw in keywords:
            st.markdown(f"**Keyword:** {kw}")
            suggestions = related_queries.get(kw, {}).get('top')
            if suggestions is not None and not suggestions.empty:
                st.dataframe(suggestions.head(10))
            else:
                st.write("No related queries found.")

        st.subheader("🌍 Regional Interest")
        region_data = pytrends.interest_by_region()
        if not region_data.empty:
            st.dataframe(region_data.sort_values(by=keywords[0], ascending=False).head(10))

        st.subheader("📤 Export Results")
        export_option = st.selectbox("Choose export format:", ["None", "CSV", "Excel"])
        if export_option != "None":
            export_buffer = io.BytesIO()
            if export_option == "CSV":
                data.to_csv(export_buffer)
                b64 = base64.b64encode(export_buffer.getvalue()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="seo_trends.csv">📥 Download CSV</a>'
            elif export_option == "Excel":
                with pd.ExcelWriter(export_buffer, engine='xlsxwriter') as writer:
                    data.to_excel(writer, index=False)
                b64 = base64.b64encode(export_buffer.getvalue()).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="seo_trends.xlsx">📥 Download Excel</a>'
            st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to fetch trends: {e}")
