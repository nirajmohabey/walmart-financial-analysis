# 🏪 Walmart Financial Analysis Dashboard

A comprehensive financial analysis suite for **Walmart Inc. (WMT)** featuring interactive visualizations, detailed ratio calculations, and real-time insights.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

## ✨ Features

### 📊 **Comprehensive Financial Analysis**
- **20+ Financial Ratios**: Liquidity, profitability, leverage, and efficiency metrics
- **Dynamic Insights**: Real-time calculations and trend analysis
- **Risk Assessment**: Altman Z-Score and Piotroski F-Score models
- **Peer Comparisons**: Benchmark against Target, Costco, and Amazon

### 🎯 **Interactive Dashboard**
- **Real-time Metrics**: Revenue, Net Income, Current Ratio, ROE with live updates
- **Visual Analytics**: Interactive charts and graphs with contextual interpretations
- **Dynamic Insights**: Data-driven interpretations based on actual analysis results
- **Multiple Views**: Overview, liquidity, profitability, leverage, efficiency, and risk analysis

### ⚡ **Advanced Features**
- **Optimized Data Loading**: Excel file processing with intelligent caching
- **Smart Scaling**: Automatic detection and formatting of financial data (billions/millions)
- **Trend Analysis**: Historical performance tracking with volatility analysis
- **DuPont Analysis**: ROE breakdown into profitability, efficiency, and leverage components

## 🚀 Quick Start

### 1. **Clone the Repository**
```bash
git clone https://github.com/nirajmohabey/walmart-financial-analysis.git
cd walmart-financial-analysis
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Run Complete Analysis**
```bash
python main.py
```

### 4. **Launch Interactive Dashboard**
```bash
streamlit run src/streamlit/app.py
```

The dashboard will be available at `http://localhost:8501`

## 📁 Project Structure

```
walmart-financial-analysis/
├── 📄 main.py                 # Main launcher script
├── 📁 src/
│   ├── 📁 analysis/          # Core analysis logic
│   │   └── analysis.py       # Main analysis engine
│   ├── 📁 core/              # Data loading and calculations
│   │   ├── data_loader.py    # Optimized Excel data loader
│   │   └── ratio_calculator.py # Financial ratio calculations
│   └── 📁 streamlit/         # Interactive dashboard
│       └── app.py            # Streamlit web application
├── 📁 data/                  # Financial data files
│   └── Financial Statements (wmt).xlsx
├── 📁 output/                # Analysis results
│   ├── walmart_financial_ratios.csv
│   ├── analysis_summary.json
│   └── analysis_summary.txt
├── 📁 logs/                  # Log files and cache
└── 📄 requirements.txt       # Python dependencies
```

## 📈 Analysis Capabilities

### **Financial Metrics**
- **Liquidity**: Current Ratio, Quick Ratio, Cash Ratio
- **Profitability**: ROA, ROE, Net Profit Margin, Gross Profit Margin
- **Leverage**: Debt-to-Equity, Debt Ratio, Interest Coverage
- **Efficiency**: Asset Turnover, Inventory Turnover, Receivables Turnover

### **Advanced Analytics**
- **Risk Assessment**: Bankruptcy prediction and financial quality scoring
- **Trend Analysis**: Historical performance with volatility metrics
- **Peer Benchmarking**: Competitive analysis against industry leaders
- **Dynamic Insights**: Real-time interpretations based on actual data patterns

## 🛠️ Technical Stack

- **Python 3.8+**: Core programming language
- **Streamlit**: Interactive web dashboard framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

## 📊 Dashboard Sections

1. **📋 Overview**: Company summary with key metrics and insights
2. **🔍 Dynamic Insights**: Real-time performance monitoring
3. **💧 Liquidity Analysis**: Short-term financial health assessment
4. **💰 Profitability Analysis**: Revenue and profit efficiency metrics
5. **⚖️ Leverage Analysis**: Debt management and financial risk
6. **⚡ Efficiency Analysis**: Asset utilization and operational performance
7. **🔍 DuPont Analysis**: ROE component breakdown
8. **🛡️ Risk Assessment**: Financial stability and quality scoring
9. **🏆 Peer Comparison**: Industry benchmarking and competitive analysis
10. **📈 Ratio Trends**: Interactive trend visualization

## 🔧 Requirements

See `requirements.txt` for complete dependency list:
- streamlit
- pandas
- numpy
- plotly
- openpyxl

## 📄 Output Files

The analysis generates:
- **📊 CSV File**: All calculated financial ratios with historical data
- **📋 JSON Summary**: Structured key insights and metrics
- **📝 Text Summary**: Human-readable analysis report
- **🌐 Interactive Dashboard**: Real-time exploration interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Niraj Mohabey** - [GitHub](https://github.com/nirajmohabey)

---

⭐ **Star this repository** if you found it helpful!