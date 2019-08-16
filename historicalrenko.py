import time
import os
import json
import datetime as dt
from iqoptionapi.stable_api import IQ_Option
from argparse import ArgumentParser
import pandas as pd
import userdata
import pyrenko

## How to use python renko.py -a USDJPY -i 300

parser = ArgumentParser()
parser.add_argument("-a", "--asset", dest="asset", required=True,
                    help="Pass the asset:(EURUSD, AUDUSD, XEMUSD-l ...)", metavar="ASSET")

parser.add_argument("-i", "--interval", dest="interval", required=False,
                    help="Pass interval in seconds: [1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,'all']", metavar="TIME")

parser.add_argument("-f", "--file-sufix", dest="filesufix", required=False,
                    help="Pass sufix to file ", metavar="SUFIX")

args = parser.parse_args()

asset = args.asset or "USDJPY"
interval = args.interval or 60
sufix = args.filesufix or ""

## AUTH
user = userdata.mainUser
Iq = IQ_Option(user["username"],user["password"])

ticks=[]

for i in range(2):
    candles=[]
    candles=Iq.get_candles(asset, int(interval), 1000, time.time())
    cds = []
    for candle in list(candles):
        cd_handle = {}
        if candle["open"]:
            cd_handle['open'] = candle["open"]
            cd_handle['high'] = candle["max"]
            cd_handle['low'] = candle["min"]
            cd_handle['close'] = candle["close"]
            cd_handle['created_at'] = dt.datetime.fromtimestamp(candle["from"]).isoformat()
            cd_handle['timestamp'] = candle["from"]
            cd_handle['volume'] = candle["volume"]
            cds.append(cd_handle)

    ticks = cds + ticks
    end_from_time = int(cds[0]["timestamp"]) - 1

try:
    df = pd.DataFrame(ticks)
    # Get optimal brick size based
    optimal_brick = pyrenko.renko().set_brick_size(auto = True, HLC_history = df[["high", "low", "close"]])

    # Build Renko chart
    renko_obj_atr = pyrenko.renko()
    renko_obj_atr.set_brick_size(auto = False, brick_size = optimal_brick)
    renko_obj_atr.build_history(prices = df.close)

    print('Renko bar prices: ', renko_obj_atr.get_renko_prices())
    print('Renko bar directions: ', renko_obj_atr.get_renko_directions())
    print('Renko bar evaluation: ', renko_obj_atr.evaluate())


    if len(renko_obj_atr.get_renko_prices()) > 1:
        renko_obj_atr.set_chart_title(asset)
        renko_obj_atr.plot_renko()
except IOError:
    print("I/O error")
