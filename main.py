import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="S&P 500 Demand Zone Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .demand-zone {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .not-demand-zone {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_sp500_tickers():
    """
    Fetch S&P 500 ticker symbols from Wikipedia with fallback
    """
    try:
        # Primary method: Wikipedia
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse the table
        tables = pd.read_html(response.text)
        sp500_table = tables[0]  # First table contains the S&P 500 data
        
        # Extract ticker symbols
        tickers = sp500_table['Symbol'].tolist()
        
        # Clean tickers (remove any special characters)
        tickers = [ticker.strip().replace('.', '-') for ticker in tickers if ticker.strip()]
        
        st.success(f"✅ Successfully fetched {len(tickers)} S&P 500 tickers from Wikipedia")
        return tickers
        
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch from Wikipedia: {str(e)}")
        
        # Fallback: Use a predefined list of major S&P 500 stocks
        fallback_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK-B', 'LLY', 'V', 'TSM',
            'UNH', 'XOM', 'JPM', 'JNJ', 'PG', 'MA', 'HD', 'CVX', 'AVGO', 'KO',
            'PEP', 'COST', 'MRK', 'ABBV', 'BAC', 'PFE', 'TMO', 'ACN', 'DHR', 'VZ',
            'ADBE', 'NFLX', 'CRM', 'CMCSA', 'DIS', 'NEE', 'PM', 'TXN', 'RTX', 'QCOM',
            'HON', 'LOW', 'UPS', 'IBM', 'INTU', 'MS', 'SPGI', 'GS', 'CAT', 'DE'
        ]
        st.info(f"🔄 Using fallback list of {len(fallback_tickers)} major S&P 500 stocks")
        return fallback_tickers

def fetch_stock_data(ticker, period="3mo"):
    """
    Fetch stock data for a given ticker
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        
        if data.empty or len(data) < 30:
            return None
            
        return data
        
    except Exception as e:
        return None

def calculate_indicators(df):
    """
    Calculate technical indicators for the given dataframe
    """
    try:
        # Check if we have enough data
        if len(df) < 30:
            return None
            
        # RSI
        rsi_indicator = RSIIndicator(close=df['Close'], window=14)
        rsi = rsi_indicator.rsi()
        
        # 30-day low
        low_30d = df['Low'].rolling(window=30).min()
        
        # Distance from 30-day low
        distance_from_low = ((df['Close'] - low_30d) / low_30d) * 100
        
        # Weekly change (5-day)
        weekly_change = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
        
        # Monthly change (21-day)
        monthly_change = ((df['Close'] - df['Close'].shift(21)) / df['Close'].shift(21)) * 100
        
        # Latest values with NaN checks
        latest_rsi = rsi.iloc[-1]
        latest_distance = distance_from_low.iloc[-1]
        latest_weekly = weekly_change.iloc[-1]
        latest_monthly = monthly_change.iloc[-1]
        latest_volume = df['Volume'].iloc[-1]
        latest_close = df['Close'].iloc[-1]
        latest_low_30d = low_30d.iloc[-1]
        
        # Check for NaN values
        if (pd.isna(latest_rsi) or pd.isna(latest_distance) or 
            pd.isna(latest_weekly) or pd.isna(latest_monthly) or
            pd.isna(latest_volume) or pd.isna(latest_close) or
            pd.isna(latest_low_30d)):
            return None
        
        return {
            'rsi': latest_rsi,
            'distance_from_low': latest_distance,
            'weekly_change': latest_weekly,
            'monthly_change': latest_monthly,
            'volume': latest_volume,
            'close': latest_close,
            'low_30d': latest_low_30d,
            'data': df
        }
        
    except Exception as e:
        return None

def analyze_stocks(tickers, rsi_threshold, distance_threshold, volume_threshold, max_workers=10):
    """
    Analyze stocks with concurrent processing
    """
    results = []
    
    with st.spinner("🔄 Fetching and analyzing stock data..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {executor.submit(fetch_stock_data, ticker): ticker for ticker in tickers}
            
            completed = 0
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                completed += 1
                
                try:
                    data = future.result()
                    if data is not None:
                        indicators = calculate_indicators(data)
                        if indicators is not None:
                            # Check if in demand zone
                            in_demand_zone = (
                                indicators['rsi'] <= rsi_threshold and
                                indicators['distance_from_low'] <= distance_threshold and
                                indicators['volume'] >= volume_threshold
                            )
                            
                            results.append({
                                'Ticker': ticker,
                                'Weekly_%': round(indicators['weekly_change'], 2),
                                'Monthly_%': round(indicators['monthly_change'], 2),
                                'RSI': round(indicators['rsi'], 2),
                                'Distance_from_Low_%': round(indicators['distance_from_low'], 2),
                                'Volume': int(indicators['volume']),
                                'Close': round(indicators['close'], 2),
                                'Low_30d': round(indicators['low_30d'], 2),
                                'In_Demand_Zone': in_demand_zone,
                                'data': indicators['data']
                            })
                
                except Exception as e:
                    pass
                
                # Update progress
                progress = completed / len(tickers)
                progress_bar.progress(progress)
                status_text.text(f"Processed {completed}/{len(tickers)} stocks...")
        
        progress_bar.empty()
        status_text.empty()
    
    return results

def plot_stock(ticker, data):
    """
    Create an interactive plot for a stock showing price and 30-day low
    """
    try:
        # Check if data is valid
        if data is None or data.empty or len(data) < 30:
            st.error(f"Insufficient data for {ticker}")
            return None
            
        # Create subplot with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Stock Price & 30-Day Low', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Price data
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        # 30-day low line
        low_30d = data['Low'].rolling(window=30).min()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=low_30d,
                mode='lines',
                name='30-Day Low',
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ),
            row=1, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color='#2ca02c',
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} - Technical Analysis',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            yaxis2_title='Volume',
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating plot for {ticker}: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 S&P 500 Demand Zone Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("⚙️ Analysis Parameters")
    
    # Threshold controls
    rsi_threshold = st.sidebar.slider(
        "RSI Threshold",
        min_value=10,
        max_value=50,
        value=40,
        help="Stocks with RSI below this value are considered oversold"
    )
    
    distance_threshold = st.sidebar.slider(
        "Distance from Low (%)",
        min_value=1,
        max_value=15,
        value=5,
        help="Maximum percentage above 30-day low to be in demand zone"
    )
    
    volume_threshold = st.sidebar.number_input(
        "Volume Threshold",
        min_value=100000,
        max_value=10000000,
        value=1000000,
        step=100000,
        help="Minimum volume required for analysis"
    )
    
    # Top N stocks to analyze
    top_n_options = [25, 50, 100]
    top_n = st.sidebar.selectbox(
        "Top N Stocks to Analyze",
        options=top_n_options,
        index=0,
        help="Number of stocks to analyze (top by market cap)"
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Analysis", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Fetch tickers
    tickers = fetch_sp500_tickers()
    
    if not tickers:
        st.error("❌ Failed to fetch ticker symbols. Please try again.")
        return
    
    # Limit to top N stocks
    tickers = tickers[:top_n]
    
    # Display current parameters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("RSI Threshold", f"≤ {rsi_threshold}")
    with col2:
        st.metric("Distance from Low", f"≤ {distance_threshold}%")
    with col3:
        st.metric("Volume Threshold", f"≥ {volume_threshold:,}")
    with col4:
        st.metric("Stocks to Analyze", len(tickers))
    
    # Analyze stocks
    results = analyze_stocks(tickers, rsi_threshold, distance_threshold, volume_threshold)
    
    if not results:
        st.warning("⚠️ No stock data could be fetched. Please check your internet connection and try again.")
        return
    
    # Create DataFrame
    df_results = pd.DataFrame(results)
    
    # Separate demand zone and other stocks
    demand_zone_stocks = df_results[df_results['In_Demand_Zone'] == True]
    other_stocks = df_results[df_results['In_Demand_Zone'] == False]
    
    # Display results
    st.header("📊 Analysis Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Stocks Analyzed", len(df_results))
    with col2:
        if len(df_results) > 0:
            demand_zone_percentage = (len(demand_zone_stocks) / len(df_results)) * 100
            st.metric("In Demand Zone", len(demand_zone_stocks), delta=f"{demand_zone_percentage:.1f}%")
        else:
            st.metric("In Demand Zone", 0, delta="0%")
    with col3:
        if len(df_results) > 0 and not df_results['RSI'].isna().all():
            avg_rsi = df_results['RSI'].mean()
            st.metric("Average RSI", f"{avg_rsi:.1f}")
        else:
            st.metric("Average RSI", "N/A")
    
    # Display demand zone stocks
    if len(demand_zone_stocks) > 0:
        st.subheader("🎯 Stocks in Demand Zone")
        
        # Format the demand zone dataframe for display
        display_df = demand_zone_stocks[['Ticker', 'Weekly_%', 'Monthly_%', 'RSI', 'Distance_from_Low_%', 'Volume', 'Close']].copy()
        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,}")
        display_df['Close'] = display_df['Close'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Plot the top demand zone stock
        if len(demand_zone_stocks) > 0:
            top_stock = demand_zone_stocks.iloc[0]
            st.subheader(f"📈 Chart: {top_stock['Ticker']} (Top Demand Zone Stock)")
            
            fig = plot_stock(top_stock['Ticker'], top_stock['data'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Display stock details
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("RSI", f"{top_stock['RSI']:.1f}")
                with col2:
                    st.metric("Distance from Low", f"{top_stock['Distance_from_Low_%']:.1f}%")
                with col3:
                    st.metric("Weekly Change", f"{top_stock['Weekly_%']:.1f}%")
                with col4:
                    st.metric("Volume", f"{top_stock['Volume']:,}")
    else:
        st.info("ℹ️ No stocks currently meet the demand zone criteria. Try adjusting the thresholds.")
    
    # Display all results in expandable section
    with st.expander("📋 View All Analyzed Stocks"):
        # Format the full dataframe for display
        full_display_df = df_results[['Ticker', 'Weekly_%', 'Monthly_%', 'RSI', 'Distance_from_Low_%', 'Volume', 'Close', 'In_Demand_Zone']].copy()
        full_display_df['Volume'] = full_display_df['Volume'].apply(lambda x: f"{x:,}")
        full_display_df['Close'] = full_display_df['Close'].apply(lambda x: f"${x:.2f}")
        full_display_df['In_Demand_Zone'] = full_display_df['In_Demand_Zone'].map({True: '✅ Yes', False: '❌ No'})
        
        st.dataframe(
            full_display_df,
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>💡 <strong>Demand Zone Criteria:</strong> RSI ≤ {} AND Distance from Low ≤ {}% AND Volume ≥ {:,}</p>
            <p>📊 Data source: Yahoo Finance | 📅 Last updated: {}</p>
        </div>
        """.format(
            rsi_threshold, 
            distance_threshold, 
            volume_threshold,
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 
