import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load the file
df = pd.read_excel("ads_data.xlsx")  # or .csv

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Rename some columns for ease
df.rename(columns={
    'amount_spent_(ngn)': 'amount_spent',
    'cost_per_result': 'cost_per_result',
    'cpc_(cost_per_link_click)': 'cpc',
    'ctr_(all)': 'ctr',
    'link_clicks': 'link_clicks',
    'results': 'results'
}, inplace=True)

# Convert relevant fields to numeric
for col in ['amount_spent', 'cost_per_result', 'cpc', 'ctr', 'results', 'link_clicks', 'reach', 'impressions']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert dates
df['day'] = pd.to_datetime(df['day'], errors='coerce')

# Basic stats
print(df.describe())

# Campaign-level summary
campaign_summary = df.groupby('campaign_name').agg({
    'amount_spent': 'sum',
    'results': 'sum',
    'link_clicks': 'sum',
    'impressions': 'sum',
    'reach': 'sum'
})
campaign_summary['ctr'] = (campaign_summary['link_clicks'] / campaign_summary['impressions']) * 100
campaign_summary['cost_per_result'] = campaign_summary['amount_spent'] / campaign_summary['results']
print(campaign_summary)

# Daily trend of results
daily = df.groupby('day').agg({
    'results': 'sum',
    'amount_spent': 'sum'
}).reset_index()

plt.figure(figsize=(10, 5))
sns.lineplot(data=daily, x='day', y='results', label='Results')
sns.lineplot(data=daily, x='day', y='amount_spent', label='Amount Spent')
plt.title("Daily Trends of Results and Spend")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Cost per result by ad set
adset_cost = df.groupby('ad_set_name').agg({
    'amount_spent': 'sum',
    'results': 'sum'
})
adset_cost['cost_per_result'] = adset_cost['amount_spent'] / adset_cost['results']
adset_cost = adset_cost.sort_values('cost_per_result')

plt.figure(figsize=(10, 6))
adset_cost['cost_per_result'].plot(kind='barh', color='skyblue')
plt.title("Cost Per Result by Ad Set")
plt.xlabel("NGN")
plt.tight_layout()
plt.show()

# Bubble Chart with Plotly
fig = px.scatter(df,
                 x="amount_spent", y="results",
                 size="impressions", color="campaign_name",
                 hover_data=["ad_set_name", "ad_name", "cpc", "ctr"])
fig.update_layout(title="Campaign Performance Overview")
fig.show()

# Export campaign summary to Excel
campaign_summary.to_excel("campaign_summary_export.xlsx")
