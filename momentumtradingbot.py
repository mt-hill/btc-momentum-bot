#!/usr/bin/env python
# coding: utf-8

# In[55]:


import websocket
import json
import pandas as pd
from binance import Client
import time
from datetime import datetime, timedelta


# In[45]:


api_key = '6HpIsqHafNXaeeHvp7ZFCKCKT0KZUGvOPUkrSTrDIUuOIBxcNjWQBLy1kYyK2WfG'
api_secret = 'XrbUb0b8LlfqeUh9FaqM0bGCP2ew0gW6IhKDPSf9Awjh1WPGjwmS8Cn0L5xJl0WO'
client = Client(api_key, api_secret)


# In[54]:


csv_file_path = 'orders.csv'


# In[46]:


endpoint = 'wss://stream.binance.com:9443/ws'


# In[47]:


our_msg = json.dumps({
    "method": "SUBSCRIBE",
    "params": ['btcusdt@kline_1h'],
    "id": 1
})


# In[48]:


def gettime():    
    timestart = datetime.now() - timedelta(hours=12)
    timeend = timestart + timedelta(seconds=1)
    return str(timestart), str(timeend)


# In[49]:


def get12hprice():
    timestart, timeend = gettime()
    frame = pd.DataFrame(client.get_historical_klines('BTCUSDT',
                                                     '1s',
                                                     timestart,
                                                     timeend))
    value = frame.iloc[:,4:5]
    return float(value.iloc[0,0])


# In[50]:


in_position = False


# In[66]:


def on_open(ws):
    ws.send(our_msg)

def on_message(ws, message):
    global df, in_position, orderqty, buyprice
    out = json.loads(message)
    thprice = get12hprice()
    df = pd.DataFrame(out['k'],index=[pd.to_datetime(out['E'],
                                            unit='ms')])[['c']]
    df['Price (12h ago)'] = thprice
    df['Diff(%)'] = float(df.c)/float(thprice) -1
    df = df.rename(columns={'c': 'Price(Now)'})
    print(df)
    
    if not in_position and float(df['diff']) >= 0.016:
        buyprice = float(df.c)
        buyorder = buy()
        buyorder.to_csv('allorders.csv',mode='a',header=False)
        in_position = True
        print('bought')
        
    if in_position:        
        if float(df.c) >= buyprice * 1.0084:
            sellorder = sell()
            sellorder.to_csv('allorders.csv',mode='a',header=False)
            in_position = False
            print('profit: '+ str(float(df.c) - buyprice))
        elif float(df.c) <= buyprice * 0.94:
            sellorder = sell()
            sellorder.to_csv('allorders.csv',mode='a',header=False)
            in_position = False
            print('loss: ' + str(float(df.c) - buyprice))


# In[65]:


ws = websocket.WebSocketApp(endpoint, on_message=on_message,
                           on_open=on_open)
ws.run_forever()


# In[42]:


def buy():
    order = client.create_order(symbol='BTC',
                                side='BUY',
                                type='MARKET',
                                qty='quoteOrderQty')
    return order


# In[43]:


def sell():
    order = client.create_order(symbol='BTC',
                                side='SELL',
                                type='MARKET',
                                qty='quoteOrderQty')
    return order


# In[ ]:




