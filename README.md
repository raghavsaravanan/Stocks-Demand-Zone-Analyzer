# 📈 S&P 500 Demand Zone Stock Screener

A fully functional web app that analyzes the entire S&P 500 using technical indicators to identify long-term buying opportunities in demand zones.

## 🔍 Features

- Live S&P 500 ticker retrieval
- RSI calculation (adjustable)
- Demand zone detection (distance from 30-day low)
- Weekly & monthly return filters
- Volume filter
- Interactive stock charts for top results
- Adjustable UI using Streamlit sliders

## 🧪 Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io)
- **Backend**: Python + `yfinance`, `pandas`, `ta`, `numpy`
- **Charts**: `matplotlib` or `plotly`
- **Deployment**: Streamlit Cloud

## 🚀 Try the App Live

👉 [Click here to run the app](https://your-streamlit-cloud-url) *(update after deploying)*

## 🛠️ Setup Instructions

```bash
git clone https://github.com/yourusername/stock-demand-screener.git
cd stock-demand-screener
pip install -r requirements.txt
streamlit run app.py
