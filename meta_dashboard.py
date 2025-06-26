import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("ads_data.xlsx")
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df.rename(columns={
        'amount_spent_(ngn)': 'amount_spent',
        'cpc_(cost_per_link_click)': 'cpc',
        'ctr_(all)': 'ctr',
        'ad_set_name.1': 'ad_set_name_full'
    }, inplace=True)
    
    df = df.drop(index=0)
    
    for col in ['results', 'reach', 'impressions', 'cost_per_result',
                'amount_spent', 'link_clicks', 'frequency', 'cpc', 'ctr']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['day'] = pd.to_datetime(df['day'], errors='coerce')
    df['reporting_starts'] = pd.to_datetime(df['reporting_starts'], errors='coerce')
    df['reporting_ends'] = pd.to_datetime(df['reporting_ends'], errors='coerce')
    
    return df

df = load_data()

# Sidebar filters
st.sidebar.title("Filter Data")
campaigns = st.sidebar.multiselect("Campaign Name", df['campaign_name'].dropna().unique(), default=None)
adsets = st.sidebar.multiselect("Ad Set Name", df['ad_set_name_full'].dropna().unique(), default=None)

filtered_df = df.copy()
if campaigns:
    filtered_df = filtered_df[filtered_df['campaign_name'].isin(campaigns)]
if adsets:
    filtered_df = filtered_df[filtered_df['ad_set_name_full'].isin(adsets)]

# KPIs
st.title("📊 Meta Ads Performance Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Spend (₦)", f"{filtered_df['amount_spent'].sum():,.0f}")
col2.metric("Total Results", int(filtered_df['results'].sum()))
col3.metric("Avg. CTR (%)", f"{filtered_df['ctr'].mean():.2f}")

# Charts
st.subheader("Spend vs Results (Bubble Chart)")
fig = px.scatter(filtered_df, x='amount_spent', y='results',
                 size='impressions', color='campaign_name',
                 hover_data=['ad_set_name_full', 'ad_name', 'cpc', 'ctr'],
                 title="Spend vs Results")
st.plotly_chart(fig, use_container_width=True)

st.subheader("CTR Distribution")
fig2 = px.histogram(filtered_df, x='ctr', nbins=30, title='CTR (%) Histogram')
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Daily Results Trend")
if 'day' in filtered_df.columns:
    time_data = filtered_df.groupby('day').agg({'results': 'sum', 'amount_spent': 'sum'}).reset_index()
    fig3 = px.line(time_data, x='day', y='results', title="Results Over Time")
    st.plotly_chart(fig3, use_container_width=True)

# Ad Set Performance Table
st.subheader("Ad Set Performance Summary")
adset_summary = filtered_df.groupby('ad_set_name_full').agg({
    'amount_spent': 'sum',
    'results': 'sum',
    'impressions': 'sum',
    'link_clicks': 'sum'
}).reset_index()
adset_summary['ctr (%)'] = (adset_summary['link_clicks'] / adset_summary['impressions']) * 100
adset_summary['cost_per_result'] = adset_summary['amount_spent'] / adset_summary['results']
st.dataframe(adset_summary.sort_values('cost_per_result'), use_container_width=True)

# Export button
st.download_button(
    label="Download Summary",
    data=adset_summary.to_csv(index=False).encode('utf-8'),
    file_name="meta_adset_summary.csv",
    mime="text/csv"
)
