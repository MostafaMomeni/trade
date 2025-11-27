import requests
import pandas as pd
import pyodbc
import numpy as np
from sklearn import metrics


server = "192.168.10.35"
database = "LiveTseDB"
username = "mostafa"
password = "mostafa1234"
driver = "ODBC Driver 18 for SQL Server"

conn_str = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)

query = """SELECT TOP (1000) [ID]
      ,[Namad]
      ,[StockID]
      ,[NotiTypeName]
      ,[NotiTypeID]
      ,[Time]
      ,[Date]
      ,[LastUpdate]
      ,[IsEvaluate]
      ,[MaxDay0]
      ,[MaxDay1]
      ,[MaxDay2]
      ,[MaxDay3]
      ,[MaxDayPercent0]
      ,[MaxDayPercent1]
      ,[MaxDayPercent2]
      ,[MaxDayPercent3]
      ,[OnEventPrice]
      ,[OnEventPricePercent]
      ,[YeserdayPrice]
      ,[MaxGain]
      ,[MaxGainPosition]
  FROM [LiveTseDB].[dbo].[Notifications]  WHERE [Date] >= '2025-10-05' and IsEvaluate = 1
ORDER BY [Date] ASC;
"""

df = pd.read_sql_query(query, conn)

df.drop(
    [
        "LastUpdate",
        "MaxDay0",
        "MaxDay1",
        "MaxDay2",
        "MaxDay3",
        "ID",
        "IsEvaluate",
        "Namad",
        "NotiTypeName",
        "MaxGainPosition",
        "OnEventPrice",
        "OnEventPricePercent",
        "Time",
        "MaxDayPercent0",
        "MaxDayPercent1",
        "MaxDayPercent2",
        "MaxDayPercent3",
    ],
    inplace=True,
    axis=1,
)

# df["Date"] = pd.to_datetime(df["Date"])
# df['Date'] = df['Date'].astype('int64') // 10**9 

df = df.iloc[:50 , :]

x = df.drop(["MaxGain"], axis=1)
y = df[["MaxGain"]]

url = "http://njweb:1234/predict"


for i in range(5):
    data = {
        "StockID": float(x.iloc[i].StockID),
        "NotiTypeID": [str(x.iloc[i].NotiTypeID)],
        "Date": str(x.iloc[i].Date),
        "YeserdayPrice": float(x.iloc[i].YeserdayPrice),
    }
    
    response = requests.post(url, json=data)
    print( y.iloc[i].values , response.json())



# url = "http://127.0.0.1:8000/predict"
# data = {
#         "StockID": 62235397452612911,
#         "NotiTypeID": ["686075F9-C00F-43B3-8F0D-A99F540B2BAB"],
#         "Date": 1759622400,
#         "YeserdayPrice": 263380,
# }

# response = requests.post(url, json=data)
# print(response.json())