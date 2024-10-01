import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import glob
from getSheet import getSheet
import logging
from dash import Dash, dcc, html, Input, Output

# Set up logging
logging.basicConfig(filename=f"logs/summary_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.log", 
                    level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

# Function to clean the data
def cleanData(df):
    logging.info("Cleaning data...")
    try:
        df['Total cost'] = df['Total cost'].replace('[$,]', '', regex=True).astype(float)
        current_year = dt.datetime.now().year
        df['Date'] = pd.to_datetime(df['Date'] + ' ' + str(current_year), format='%b %d %Y', errors='coerce')

        # Handle missing or invalid data
        if df['Total cost'].isnull().sum() > 0:
            raise ValueError("Total cost contains NaN values after conversion.")
        
        if df['Date'].isnull().sum() > 0:
            logging.warning(f"{df['Date'].isnull().sum()} invalid dates found and dropped.")
            df = df.dropna(subset=['Date'])
        
        logging.info(f"Data cleaning complete. {df.shape[0]} rows processed.")
    except Exception as e:
        logging.error(f"Error cleaning data: {e}")
    return df


# Sub-functions for visualizations
def createBarChart(df):
    numeric_cols = df.select_dtypes(include='number').columns
    grouped_df = df.groupby('Primary Category')[numeric_cols].sum().reset_index()
    return px.bar(
        grouped_df, 
        x='Primary Category', 
        y='Total cost', 
        title="Total Expenses by Primary Category",
        labels={'Total cost': 'Total Cost ($)'},
        text='Total cost'
    )

def createPieChart(df):
    return px.pie(
        df, 
        values='Total cost', 
        names='Secondary Category', 
        title="Distribution of Expenses by Secondary Category"
    )

def createTimeSeriesChart(df):
    daily_summary = df.groupby(df['Date'].dt.strftime('%Y-%m-%d'))['Total cost'].sum().reset_index()
    daily_summary['7-Day MA'] = daily_summary['Total cost'].rolling(window=7).mean()  # 7-day moving average
    fig = px.line(
        daily_summary, 
        x='Date', 
        y='Total cost', 
        title="Daily Expense Trends",
        markers=True
    )
    fig.add_scatter(x=daily_summary['Date'], y=daily_summary['7-Day MA'], mode='lines', name='7-Day MA')
    return fig

def createHeatmap(df):
    return px.density_heatmap(
        df, 
        x='Primary Category', 
        y=df['Date'].dt.day_name(), 
        z='Total cost', 
        title="Spending Frequency by Category and Day of the Week",
        labels={'Total cost': 'Total Cost ($)', 'Date': 'Day of Week'}
    )

def createHistogram(df):
    return px.histogram(
        df, 
        x='Total cost', 
        title="Distribution of Expense Amounts",
        nbins=20,
        labels={'Total cost': 'Total Cost ($)'}
    )

def createGaugeChart(total_spent, monthly_budget):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_spent,
        title={'text': "Monthly Spending"},
        gauge={'axis': {'range': [None, monthly_budget]}, 'bar': {'color': "red"}}
    ))

# Function to create the dashboard
def createDashboard(df, monthly_budget=1000):  # Default monthly budget of $1000
    # Filter out essentials for bar chart
    no_essentials = df[df["Secondary Category"] != "Essential"]

    # Create visualizations
    bar_fig = createBarChart(no_essentials)
    pie_fig = createPieChart(df)
    time_series_fig = createTimeSeriesChart(df)
    heatmap_fig = createHeatmap(df)
    histogram_fig = createHistogram(df)

    # Calculate total spent for gauge chart
    total_spent = df['Total cost'].sum()
    gauge_fig = createGaugeChart(total_spent, monthly_budget)

    return bar_fig, pie_fig, time_series_fig, heatmap_fig, histogram_fig, gauge_fig

# Function to clean data and create the summary dashboard
def createSummary(df):
    df = cleanData(df)
    return createDashboard(df)

# Initialize Dash app
app = Dash(__name__)

# Example usage
if __name__ == '__main__':
    getSheet()
    df = pd.read_csv(glob.glob("data/current/*")[0])
    bar_fig, pie_fig, time_series_fig, heatmap_fig, histogram_fig, gauge_fig = createSummary(df)

    # Set up layout
    app.layout = html.Div(children=[
        html.H1(children='Expense Tracker Dashboard'),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in df['Primary Category'].unique()] + [{'label': 'All', 'value': 'All'}],
            value='All',
            clearable=False
        ),
        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='pie-chart'),
        dcc.Graph(id='time-series-chart'),
        dcc.Graph(id='heatmap-chart'),
        dcc.Graph(id='histogram-chart'),
        dcc.Graph(id='gauge-chart'),
        html.Div(children=[
            html.H2('Summary Tables'),
            html.Div(id='summary-tables'),
        ]),
    ])

    @app.callback(
        Output('bar-chart', 'figure'),
        Output('pie-chart', 'figure'),
        Output('time-series-chart', 'figure'),
        Output('heatmap-chart', 'figure'),
        Output('histogram-chart', 'figure'),
        Output('gauge-chart', 'figure'),
        Output('summary-tables', 'children'),
        Input('category-dropdown', 'value')
    )
    def update_dashboard(selected_category):
        if selected_category == "All":
            filtered_df = df
        else:
            filtered_df = df[df['Primary Category'] == selected_category]
        bar_fig = createBarChart(filtered_df)
        pie_fig = createPieChart(filtered_df)
        time_series_fig = createTimeSeriesChart(filtered_df)
        heatmap_fig = createHeatmap(filtered_df)
        histogram_fig = createHistogram(filtered_df)

        total_spent = filtered_df['Total cost'].sum()
        gauge_fig = createGaugeChart(total_spent, 2000)  # Assuming a budget of $1000

        total_count = filtered_df.shape[0]
        summary_table = html.Table(children=[
            html.Tr(children=[html.Th("Total Spent"), html.Td(f"${total_spent:,.2f}")]),
            html.Tr(children=[html.Th("Total Transactions"), html.Td(total_count)])])
        
        return bar_fig, pie_fig, time_series_fig, heatmap_fig, histogram_fig, gauge_fig, summary_table

    app.run_server()
