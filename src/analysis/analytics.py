import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ingestion.database import NewsDatabase, Article

def get_sentiment_dataframe():
    """Pulls all processed articles from SQLite and returns them as a Pandas DataFrame."""
    db = NewsDatabase()
    with db.Session() as session:
        articles = session.query(Article).filter(
            Article.sentiment_label != "UNPROCESSED",
            Article.sentiment_label != "ERROR"
        ).all()
        
        if not articles:
            return None
        
        # Convert SQLAlchemy row objects into a list of plain dicts
        data = [{
            "date": a.date,
            "source": a.source,
            "sentiment": a.sentiment_label,
            "score": a.sentiment_score,
            "text": a.text[:80] + "..."
        } for a in articles]
        
        df = pd.DataFrame(data)
        
        # Parse dates properly so Plotly can sort them on the timeline
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values("date")
        
        return df

def render_analytics_dashboard():
    """Renders all Plotly charts into the Streamlit UI."""
    import streamlit as st
    
    st.subheader("📊 Market Sentiment Analytics")
    
    with st.spinner("Loading analytics data..."):
        df = get_sentiment_dataframe()
        
    if df is None or df.empty:
        st.warning("No processed articles found. Run ingestion first!")
        return

    # --- ROW 1: Summary KPIs ---
    total = len(df)
    pos = len(df[df["sentiment"] == "positive"])
    neg = len(df[df["sentiment"] == "negative"])
    neu = len(df[df["sentiment"] == "neutral"])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Articles", total)
    k2.metric("🟢 Positive", pos, f"{pos/total*100:.0f}%")
    k3.metric("🔴 Negative", neg, f"{neg/total*100:.0f}%")
    k4.metric("⚪ Neutral", neu, f"{neu/total*100:.0f}%")
    
    st.divider()
    
    # --- ROW 2: Distribution Pie + Source Bar ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Sentiment Distribution**")
        color_map = {"positive": "#22c55e", "negative": "#ef4444", "neutral": "#94a3b8"}
        fig_pie = px.pie(
            df, names="sentiment",
            color="sentiment",
            color_discrete_map=color_map,
            hole=0.4,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f8fafc",
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("**Articles by Source**")
        source_counts = df["source"].value_counts().reset_index()
        source_counts.columns = ["source", "count"]
        fig_bar = px.bar(
            source_counts, x="source", y="count",
            color="count",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#f8fafc",
            showlegend=False,
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- ROW 3: Sentiment Over Time ---
    st.markdown("**Market Sentiment Trend Over Time**")
    
    # Group by date and sentiment, count articles per day
    df["date_only"] = df["date"].dt.date
    timeline = df.groupby(["date_only", "sentiment"]).size().reset_index(name="count")
    
    fig_line = px.line(
        timeline, x="date_only", y="count",
        color="sentiment",
        color_discrete_map=color_map,
        markers=True,
    )
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f8fafc",
        xaxis=dict(gridcolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b"),
        legend_title="Sentiment",
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)
