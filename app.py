import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(
    page_title="Clinical Genomics Variant Registry",
    page_icon="🧬",
    layout="wide"
)

@st.cache_data
def load_data():
    conn = sqlite3.connect("data/genomics_registry.db")
    query = "SELECT * FROM variant_registry"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Database not found or could not be loaded. Please run 'scripts/generate_genomic_data.py' first. Error: {e}")
    st.stop()

st.sidebar.header("🔍 Clinical Filters")

selected_genes = st.sidebar.multiselect(
    "Filter by Gene Target",
    options=sorted(df["gene"].unique()),
    default=sorted(df["gene"].unique())
)

selected_acmg = st.sidebar.multiselect(
    "Filter by ACMG Classification",
    options=sorted(df["acmg_classification"].unique()),
    default=sorted(df["acmg_classification"].unique())
)

filtered_df = df[
    (df["gene"].isin(selected_genes)) & 
    (df["acmg_classification"].isin(selected_acmg))
]

st.title("🧬 Clinical Genomics Variant Registry & Analytics")
st.markdown("Centralized molecular intelligence platform for tracking Next-Generation Sequencing (NGS) variants, ACMG classifications, and laboratory turnaround efficiencies.")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tests Analyzed", f"{len(filtered_df):,}")

with col2:
    pathogenic_count = len(filtered_df[filtered_df["acmg_classification"].str.contains("Pathogenic", na=False)])
    st.metric("Pathogenic / Likely Path.", f"{pathogenic_count:,}")

with col3:
    avg_tat = filtered_df["turnaround_days"].mean() if not filtered_df.empty else 0
    st.metric("Avg. Lab Turnaround", f"{avg_tat:.1f} Days")

with col4:
    unique_genes_count = filtered_df["gene"].nunique()
    st.metric("Active Gene Targets", f"{unique_genes_count}")

st.markdown("---")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📊 ACMG Pathogenicity Distribution")
    if not filtered_df.empty:
        acmg_counts = filtered_df["acmg_classification"].value_counts().reset_index()
        acmg_counts.columns = ["Classification", "Count"]
        
        fig_pie = px.pie(
            acmg_counts, 
            names="Classification", 
            values="Count", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

with chart_col2:
    st.subheader("🔥 Top Detected Variants")
    if not filtered_df.empty:
        top_variants = filtered_df.groupby(["gene", "variant_nomenclature"]).size().reset_index(name="Frequency")
        top_variants = top_variants.sort_values(by="Frequency", ascending=False).head(8)
        top_variants["Label"] = top_variants["gene"] + ": " + top_variants["variant_nomenclature"]
        
        fig_bar = px.bar(
            top_variants, 
            x="Frequency", 
            y="Label", 
            orientation="h",
            color="Frequency",
            color_continuous_scale="Viridis"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

st.markdown("---")

st.subheader("📋 Patient Variant Registry & Audit Trail")

search_query = st.text_input("Search by Patient ID or BioSample ID:", "")

display_df = filtered_df
if search_query:
    display_df = display_df[
        display_df["patient_id"].str.contains(search_query, case=False, na=False) |
        display_df["biosample_id"].str.contains(search_query, case=False, na=False)
    ]

st.dataframe(
    display_df[[
        "patient_id", "biosample_id", "gene", "variant_nomenclature", 
        "acmg_classification", "collection_date", "report_date", "turnaround_days"
    ]],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.caption("Clinical Genomics Intelligence Dashboard • Built with Streamlit, Pandas, and SQLite")