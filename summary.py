import pandas as pd
import datetime as dt
import plotly.express as px
import glob
from getSheet import getSheet

# Function to clean the data
def cleanData(df):
    # Clean 'Total cost' column
    df['Total cost'] = df['Total cost'].replace('[$,]', '', regex=True).astype(float)

    # Convert 'Date' column to datetime format (assuming it's already in 'YYYY-MM-DD')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')

    return df

# Function to create the dashboard
def createDashboard(df):

    # Summarize by primary and secondary categories
    primary_summary = df.groupby('Primary Category')['Total cost'].sum().reset_index()
    secondary_summary = df.groupby('Secondary Category')['Total cost'].sum().reset_index()
    no_essentials = df[df["Secondary Category"] != "Essential"]
    
    # Convert 'Date' to daily period and then back to string
    df['Day'] = df['Date'].dt.strftime('%Y-%m-%d')  # Convert to string format
    daily_summary = df.groupby('Day')['Total cost'].sum().reset_index()

    # Debugging: check if daily_summary is correct
    print(daily_summary)

    # Create bar, pie, and time series figures
    bar_fig = px.bar(no_essentials, x='Primary Category', y='Total cost', 
                     title='Expenses by Primary Category', color='Primary Category', 
                     labels={'Total cost': 'Total Cost ($)'})
    
    pie_fig = px.pie(secondary_summary, names='Secondary Category', values='Total cost', 
                     title='Expenses by Secondary Category')

    time_series_fig = px.line(daily_summary, x='Day', y='Total cost', 
                              title='Daily Expense Trends', markers=True, 
                              labels={'Total cost': 'Total Cost ($)'})

    # Save figures as images
    bar_fig.write_image("images/bar_fig.svg")
    pie_fig.write_image("images/pie_fig.svg")
    time_series_fig.write_image("images/time_series_fig.svg")

# Function to clean data and create the summary dashboard
def createSummary(df):
    print(df)
    df = cleanData(df)
    createDashboard(df)

# Example usage
if __name__ == '__main__':
    # getSheet()
    df = pd.read_excel(glob.glob("data/current/*")[0])
    createSummary(df)
