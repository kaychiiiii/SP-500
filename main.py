import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import yfinance as yf

st.title('S&P 500 Web App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (using the Python library `yfinance`).
* Data source: [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()

# Sidebar - Sector selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())

with st.sidebar:
    container = st.container()
    if st.checkbox('Select all'):
        selected_sector = container.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)
    else:
        selected_sector = container.multiselect('Sector', sorted_sector_unique)

# Filter the data
df_selected_sector = df[ df['GICS Sector'].isin(selected_sector) ]

st.header('Display Companies in Selector Sector(s)')
st.write('Data Dimensions: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector.sort_values(['GICS Sector', 'Symbol']))

if len(selected_sector) == 0:
    st.warning('Please select at least one Sector!')

# Download the data
def filedownload(df):
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html = True)

# Retrieving only the first 10 companies
# To minimize time taken to generate the plots
first10 = list(df_selected_sector['Symbol'])[:10]

# Following https://pypi.org/project/yfinance/
# Pass exception if no Sectors have been selected
try:
    snp_data = yf.download(
        tickers = first10,
        period = 'ytd',
        interval = '1d',
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )
except Exception:
    pass

# Plot closing prices
def price_plot(symbol_list):
    for symbol in symbol_list:
        df2 = pd.DataFrame(snp_data[symbol].Close)
        df2['Date'] = df2.index
        plt.style.use('default')
        plt.plot(df2.Date, df2.Close, label = symbol)
        plt.legend(loc = 0)
        plt.xticks(rotation = 90)
        plt.xlabel('Date')
        plt.ylabel('Closing Price')
    return st.pyplot()

st.set_option('deprecation.showPyplotGlobalUse', False)

# Sidebar - Company selection
sorted_symbol_unique = sorted(first10)
# Pass exception if no Sectors have been selected
try:
    selected_symbol = st.sidebar.multiselect('Company', sorted_symbol_unique, sorted_symbol_unique[0])
    if st.button('Show Plots'):
        st.header('Stock Closing Price')
        price_plot(list(selected_symbol))
except Exception:
    pass
