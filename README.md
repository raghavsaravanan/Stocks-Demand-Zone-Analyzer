# 📈 S&P 500 Demand Zone Analyzer

A comprehensive Streamlit web application that analyzes S&P 500 stocks for demand zone opportunities based on technical indicators.

## 🚀 Features

- **Live Data Fetching**: Automatically fetches current S&P 500 ticker symbols from Wikipedia with fallback
- **Technical Analysis**: Calculates RSI, 30-day lows, volume analysis, and price momentum
- **Demand Zone Detection**: Identifies stocks meeting oversold criteria with customizable thresholds
- **Interactive UI**: Adjustable parameters with real-time analysis updates
- **Concurrent Processing**: Fast analysis using ThreadPoolExecutor for multiple stocks
- **Interactive Charts**: Plotly-powered visualizations showing price action and 30-day lows
- **Responsive Design**: Modern, mobile-friendly interface

## 📊 Technical Indicators

- **RSI (14-day)**: Relative Strength Index for oversold detection
- **30-day Low**: Rolling minimum price over 30 trading days
- **Distance from Low**: Percentage above 30-day low
- **Weekly Change**: 5-day price momentum
- **Monthly Change**: 21-day price momentum
- **Volume Analysis**: Latest trading volume

## 🎯 Demand Zone Criteria

A stock is considered in a demand zone when:
- RSI ≤ 40 (adjustable)
- Distance from 30-day low ≤ 5% (adjustable)
- Volume ≥ 1,000,000 (adjustable)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## 📋 Requirements

- Python 3.8+
- Internet connection for live data fetching
- Required packages (see `requirements.txt`):
  - streamlit
  - pandas
  - numpy
  - yfinance
  - requests
  - ta (Technical Analysis library)
  - plotly
  - lxml
  - html5lib
  - beautifulsoup4

## 🎮 Usage

### Sidebar Controls
- **RSI Threshold**: Adjust the RSI level for oversold detection (10-50)
- **Distance from Low**: Set maximum percentage above 30-day low (1-15%)
- **Volume Threshold**: Minimum volume requirement (100K-10M)
- **Top N Stocks**: Choose how many stocks to analyze (25, 50, or 100)
- **Refresh Button**: Re-run analysis with current parameters

### Output Sections
1. **Summary Metrics**: Overview of analysis results
2. **Demand Zone Stocks**: Table of stocks meeting criteria
3. **Interactive Chart**: Price chart with 30-day low line for top stock
4. **Complete Results**: Expandable table with all analyzed stocks

## 🔧 Technical Details

### Architecture
- **Modular Design**: Separated into focused functions for maintainability
- **Caching**: 1-hour cache for ticker symbols to reduce API calls
- **Error Handling**: Graceful fallbacks for network issues and data problems
- **Concurrent Processing**: ThreadPoolExecutor for efficient multi-stock analysis

### Data Sources
- **S&P 500 Tickers**: Wikipedia (with fallback to major stocks)
- **Stock Data**: Yahoo Finance via yfinance
- **Technical Indicators**: Calculated using the `ta` library

### Performance Optimizations
- Concurrent data fetching
- Intelligent caching strategies
- Progress indicators for long operations
- Efficient DataFrame operations

## 🚨 Disclaimer

This application is for educational and research purposes only. It should not be considered as financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.

## 📈 Future Enhancements

- Additional technical indicators (MACD, Bollinger Bands, etc.)
- Historical demand zone analysis
- Export functionality for results
- Email alerts for new demand zone opportunities
- Backtesting capabilities
- Custom watchlist functionality

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## 📄 License

This project is open source and available under the MIT License. 
