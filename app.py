import os
import streamlit as st
import data_processing as dp
import charts as ch

# Page configuration
st.set_page_config(
    page_title="Gaming Sessions Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom minimal CSS for clean typography & spacing
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { margin-bottom: 0.5rem; font-weight: 600; font-size: 1.8rem; }
    h3 { margin-top: 0rem; margin-bottom: 0.5rem; font-size: 1.2rem; font-weight: 500; }
    .top-game-card {
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        background-color: rgba(150, 150, 150, 0.08);
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .top-game-rank { font-weight: 700; color: #6366F1; font-size: 1.1rem; }
    .top-game-name { font-weight: 600; font-size: 1.05rem; }
    .top-game-hours { font-weight: 500; opacity: 0.85; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data_cached(source, genre_map_path="genre_map.json"):
    return dp.load_data(source, genre_map_path=genre_map_path)


def render_plotly_chart(fig):
    """Renders Plotly chart supporting both newer and legacy Streamlit versions without warnings."""
    try:
        st.plotly_chart(fig, width="stretch")
    except (TypeError, ValueError):
        st.plotly_chart(fig, use_container_width=True)


def main():
    st.title("Gaming Sessions Dashboard 🎮")

    # File resolution (User Upload > sessionist_export.csv > sample_export.csv)
    uploaded_file = st.file_uploader("Upload CSV export (Optional)", type=["csv"], help="Upload your Sessionist CSV export")

    default_csv = "sessionist_export.csv" if os.path.exists("sessionist_export.csv") else "sample_export.csv"
    data_source = uploaded_file if uploaded_file is not None else default_csv

    try:
        df = load_data_cached(data_source)
    except Exception as e:
        st.error(f"Error loading session data: {str(e)}")
        st.stop()

    if df.empty:
        st.warning("No session data found in the provided CSV file.")
        st.stop()

    # Shared color map for consistent game colors across charts
    all_games = df["Game Name"].unique().tolist()
    game_color_map = ch.get_game_color_map(all_games)

    # ------------------ ROW 1 ------------------
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Top 3 Games (This Month)")
        top_3_df = dp.get_top_n_games_current_month(df, n=3)
        if top_3_df.empty:
            st.info("No session records for the current month.")
        else:
            for idx, (_, row) in enumerate(top_3_df.iterrows(), start=1):
                g_name = row["Game Name"]
                g_hrs = row["Duration_Hours"]
                st.markdown(
                    f"""
                    <div class="top-game-card">
                        <div>
                            <span class="top-game-rank">#{idx}</span> &nbsp;
                            <span class="top-game-name">{g_name}</span>
                        </div>
                        <div class="top-game-hours">{g_hrs:.2f} hrs</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col2:
        st.subheader("Playtime Share (All-Time)")
        share_df = dp.get_playtime_share_all_games(df)
        donut_fig = ch.build_donut(share_df, game_color_map=game_color_map)
        render_plotly_chart(donut_fig)

    st.markdown("---")

    # ------------------ ROW 2 ------------------
    col3, col4 = st.columns([1, 1])

    with col3:
        st.subheader("Playtime by Genre (This Month)")
        genre_series = dp.get_genre_playtime_current_month(df)
        radar_fig = ch.build_radar(genre_series)
        render_plotly_chart(radar_fig)

    with col4:
        st.subheader("Summary Metrics")
        m_col1, m_col2, m_col3 = st.columns(3)
        month_hrs = dp.get_total_playtime(df, period="month")
        week_hrs = dp.get_total_playtime(df, period="week")
        streak_days = dp.get_longest_streak_current_month(df)

        with m_col1:
            st.metric("Month Total", f"{month_hrs:.1f} hrs")
        with m_col2:
            st.metric("Week Total", f"{week_hrs:.1f} hrs")
        with m_col3:
            st.metric("Longest Streak", f"{streak_days} days")

    st.markdown("---")

    # ------------------ ROW 3 ------------------
    col5, col6 = st.columns([1, 1])

    with col5:
        hourly_series = dp.get_sessions_by_hour(df)
        hour_fig = ch.build_hour_histogram(hourly_series)
        render_plotly_chart(hour_fig)

    with col6:
        weekday_series = dp.get_sessions_by_weekday(df)
        weekday_fig = ch.build_weekday_histogram(weekday_series)
        render_plotly_chart(weekday_fig)


if __name__ == "__main__":
    main()
