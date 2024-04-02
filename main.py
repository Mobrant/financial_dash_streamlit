import streamlit as st
from streamlit_option_menu import option_menu
from google.cloud import bigquery
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import os
import datetime as date
import yfinance as yf
from annotated_text import annotated_text
from google.oauth2 import service_account

st.set_page_config(layout="wide")

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

@st.cache_data(ttl=30000)
def get_prices():
    prices_query = """
    SELECT * FROM `eltde-417516.dbt_mbrant.core_prices` 
    """

    prices = client.query(prices_query)

        # Wait for the query to finish
    prices_df = prices.to_dataframe()
    return prices_df

@st.cache_data(ttl=30000)
def get_ins_trans():
    insiders_query = """
    SELECT * FROM `eltde-417516.dbt_mbrant.optimized_insiders_trans`
    WHERE PARSE_DATE('%m-%Y', formatted_date) >= PARSE_DATE('%m-%Y', '03-2023')
    """

    insiders = client.query(insiders_query)

        # Wait for the query to finish
    insiders_df = insiders.to_dataframe()
    return insiders_df

@st.cache_data(ttl=30000)
def get_ins_pur():
    insiders_query = """
    SELECT * FROM `eltde-417516.dbt_mbrant.core_ins_pur`
    """

    insiders = client.query(insiders_query)

        # Wait for the query to finish
    insiders_df = insiders.to_dataframe()
    return insiders_df

@st.cache_data(ttl=30000)
def get_ins_roster():
    insiders_query = """
    SELECT * FROM `eltde-417516.dbt_mbrant.core_ins_roster`
    """

    insiders = client.query(insiders_query)

        # Wait for the query to finish
    insiders_df = insiders.to_dataframe()
    return insiders_df

@st.cache_data(ttl=30000)
def get_analyst_change():
    analyst_query = """
    SELECT * FROM `eltde-417516.dbt_mbrant.core_analyst_change`
    WHERE date>='2023-03-30'
    """

    analysts = client.query(analyst_query)

        # Wait for the query to finish
    analysts = analysts.to_dataframe()
    return analysts

@st.cache_data(ttl=30000)
def get_analyst_rec():
    analyst_query = """
    SELECT * FROM `eltde-417516.dbt_mbrant.core_analyst_rec`
    """

    analysts = client.query(analyst_query)

        # Wait for the query to finish
    analysts = analysts.to_dataframe()
    return analysts

def get_div(stock):
    try:
        return stock['dividendRate']
    except:
        return '-'


config = {'displayModeBar': False}
prices_df=get_prices()
insiders_df=get_ins_trans()
insiders_pur_df=get_ins_pur()
insiders_roster_df=get_ins_roster()
analyst_change=get_analyst_change()
analyst_rec=get_analyst_rec()

c1, c2, c3 = st.columns([5,2,5])
user_input=c2.text_input('Enter Stock Symbol From S&P 500')

if user_input:
    col1, col2, col3 = st.columns([4,3,4])
    with col2:
        selected=option_menu(
            menu_title=None,
            options=["General","Insiders","Analysts"],
            orientation="horizontal",
            icons=["house","person","graph-up"],
            styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "15px"}, 
            "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#F9E6AC"},
            }

        )

    c4, c5, c6 = st.columns([1,4,1])
   
    if selected == "General":
        stock=yf.Ticker(f'{user_input.upper()}').info
        close=stock['previousClose']
        sector=stock['sector']
        name=stock['shortName']
        eps=stock['trailingEps']
        held_ins=stock['heldPercentInsiders']
        div=get_div(stock)
        shortRatio=stock['shortRatio']
        with c5.container(border=True):
            col7 , col8 , col9 = st.columns([2,1,1])
            with col7.container():

                st.subheader(f'{name} | {close}')
                annotated_text(("Sector", f'{sector}', "#fea") )
                prices_fil=prices_df.query(f"Ticker=='{user_input.upper()}'")
                prices_fil.sort_values(by='Date',inplace=True)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=prices_fil['Date'], y=prices_fil['Price'], fill='tonexty', line=dict(color='orange'))) # fill to trace0 y
                fig.update_layout(margin=dict(t=0.1, b=0),
                height=200,
                width=450,
                xaxis=dict(showgrid=False),  # Remove grid lines along x-axis
                yaxis=dict(showgrid=False),  # Remove grid lines along y-axis
                )

                st.plotly_chart(fig,config = config)
            with col8.container():
                st.text("")
                st.text("")
                st.text("")
                st.text("")
                st.text("")
                MC=round(stock['marketCap']/1000000000, 2)
                st.metric("Market Cap", f'{MC}B')
                st.metric("Dividend", f'{div}')

            with col9.container():
                st.text("")
                st.text("")
                st.text("")
                st.text("")
                st.text("")
                st.metric("Eps", f'{eps}')
                st.metric("Short Ratio", f'{shortRatio}')

    if selected == "Insiders":
        with c5.container(border=True):
                c7 , c8 , c9 = st.columns([3,2,2])
                with c7.container():
                    
                    genre = st.radio(
                    '',
                    ['Count','Shares'],
                    captions = ['Number of Transactions', "Number of Shares"],
                    horizontal = True)
                    if genre == 'Count':
                        insiders_df_fil=insiders_df.query(f"symbol=='{user_input.upper()}'")
                        fig = px.histogram(insiders_df_fil, x="formatted_date", y="cnt",
                        color='transaction_type', barmode='group',
                        height=350,
                        color_discrete_map={
                        "Sell": "#EE7261",
                        "Purchase": "#ADF9AC"})
                        fig.update_layout(margin=dict(t=0, b=0))
                        fig.update_xaxes(title="")
                        fig.update_yaxes(title="")
                        fig.update_layout(legend_title_text="")
                        st.plotly_chart(fig,config = config)
                    if genre == 'Shares':
                        insiders_df_fil=insiders_df.query(f"symbol=='{user_input.upper()}'")
                        fig = px.histogram(insiders_df_fil, x="formatted_date", y="quantity",
                        color='transaction_type', barmode='group',
                        height=350,
                        color_discrete_map={
                        "Sell": "#EE7261",
                        "Purchase": "#ADF9AC"})
                        fig.update_layout(margin=dict(t=0, b=0))
                        fig.update_xaxes(title="")
                        fig.update_yaxes(title="")
                        fig.update_layout(legend_title_text="")
                        st.plotly_chart(fig,config = config)

                    insiders_roster_df_fil=insiders_roster_df.query(f"symbol=='{user_input.upper()}'")
                    insiders_roster_df_fil=insiders_roster_df_fil[['name','position','shares_owned_directly']]
                    st.dataframe(
                            insiders_roster_df_fil,
                            column_config={
                                "name": "Name",
                                "position": "Position",
                                "shares_owned_directly": 'Shares Owned'
                                },
                                hide_index=True
                            )
                

                    
                with c9.container():
                    stock=yf.Ticker(f'{user_input.upper()}').info
                    held_ins=round(stock['heldPercentInsiders']*100,2)
                    SO=stock['sharesOutstanding']
                    value_ins=SO*held_ins/100
                    st.markdown('#')
                    st.markdown('#')
                    df_pie=insiders_df.query(f"symbol=='{user_input.upper()}'")
                    df_pie=df_pie[['transaction_type','cnt']]
                    df_pie=df_pie.groupby(['transaction_type'])['cnt'].sum().reset_index()
                    color_map = {
                    "Sell": "#EE7261",  
                    "Purchase": "#ADF9AC",  
                    }
                    colors = [color_map[transaction] for transaction in df_pie['transaction_type']]
                    fig = go.Figure(data=[go.Pie(labels=df_pie['transaction_type'], values=df_pie['cnt'], hole=.7,marker=dict(colors=colors))])
                    fig.update_layout(
                        title_text='Buy vs. Sell Percentages',
                        autosize=True,
                        width=350,
                        height=350)
                    st.plotly_chart(fig,config = config)

                    

                

            


                    


    if selected == "Analysts":
        with c5.container(border=True):
            c6 , c7  = st.columns([2,2])

            with c6.container():
                analyst_change_fil=analyst_change.query(f"symbol=='{user_input.upper()}'")
                analyst_change_fil=analyst_change_fil[['date','firm','from_grade','to_grade','action']]
                analyst_change_fil.sort_values('date',inplace=True, ascending=False)
                st.dataframe(
                            analyst_change_fil,
                                hide_index=True
                            )

            with c7.container():
                analyst_rec_fil=analyst_rec.query(f"symbol=='{user_input.upper()}'")
                analyst_rec_fil.sort_values('period',inplace=True, ascending=False)
                analyst_rec_fil['sort_field']=[1,4,3,2]
                analyst_rec_fil.sort_values('sort_field',inplace=True, ascending=True)
                fig = px.bar(analyst_rec_fil, x="period", y=["strong_buy", "buy", "hold","sell","strong_sell"], title=f'Recommendations for {user_input.upper()} stock over the past four months')
                fig.update_traces(width=0.2)
                fig.update_xaxes(title="")
                fig.update_yaxes(title="")
                fig.update_layout(legend_title_text="")
                st.plotly_chart(fig,config = config)
        






