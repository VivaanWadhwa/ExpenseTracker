import pandas as pd
import datetime as dt
import plotly.express as px
import glob
from getSheet import getSheet

# Function to clean the data
def cleanData(df):
    # Clean 'Total cost' column by removing $ signs and commas
    df['Total cost'] = df['Total cost'].replace('[$,]', '', regex=True).astype(float)

    # Convert 'Date' column to datetime format (assuming the year is current year)
    current_year = dt.datetime.now().year
    df['Date'] = pd.to_datetime(df['Date'] + ' ' + str(current_year), format='%b %d %Y', errors='coerce')

    # Debugging: check for invalid dates
    print("Invalid dates after conversion:", df['Date'].isnull().sum())
    
    return df

# Function to create the dashboard
def createDashboard(df):
    # Summarize by primary and secondary categories
    primary_summary = df.groupby('Primary Category')['Total cost'].sum().reset_index()
    secondary_summary = df.groupby('Secondary Category')['Total cost'].sum().reset_index()
    
    # Filter out essentials for the bar chart
    no_essentials = df[df["Secondary Category"] != "Essential"]
    
    # Ensure there are no missing date entries
    df = df.dropna(subset=['Date'])

    # Convert 'Date' to daily period and then back to string
    df['Day'] = df['Date'].dt.strftime('%Y-%m-%d')  # Convert to string format
    
    # Debugging: print out the first few rows of daily_summary
    daily_summary = df.groupby('Day')['Total cost'].sum().reset_index()
    print("Daily Summary Head:")
    print(daily_summary.head())

    # Create bar, pie, and time series figures
    category_summary = no_essentials.groupby('Primary Category', as_index=False)['Total cost'].sum()

    # Create the bar chart with the grouped data
    bar_fig = px.bar(
        category_summary, 
        x='Primary Category', 
        y='Total cost', 
        title='Total Expenses by Primary Category', 
        color='Primary Category', 
        labels={'Total cost': 'Total Cost ($)'}, 
        text='Total cost'  # Show total spent on each category
    )

    # Update layout to position the text on top of each bar
    bar_fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

    
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
    print("Initial DataFrame Head:")
    print(df.head())  # Check the initial DataFrame
    df = cleanData(df)
    createDashboard(df)

# Example usage
if __name__ == '__main__':
    getSheet()
    df = pd.read_csv(glob.glob("data/current/*")[0])
    createSummary(df)
