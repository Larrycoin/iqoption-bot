import time
import os
import json
import datetime as dt
from iqoptionapi.stable_api import IQ_Option
from argparse import ArgumentParser
import pandas as pd
import userdata
import traceback
import time
from rethinkdb import RethinkDB
import urllib3
import copy as cp
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# config de banco
r = RethinkDB()
r.connect('localhost', 28015).repl()
iqdb = r.db('iqoption')
candlesTb = iqdb.table('candles')
## How to use python renko.py -a USDJPY -i 300

parser = ArgumentParser()
parser.add_argument("-a", "--asset", dest="asset", required=True,
                    help="Pass the asset:(EURUSD, AUDUSD, XEMUSD-l ...)", metavar="ASSET")

parser.add_argument("-i", "--interval", dest="interval", required=False,
                    help="Pass interval in seconds: [1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,'all']", metavar="TIME")


args = parser.parse_args()
asset = args.asset or "USDJPY"
interval = args.interval or 5

## AUTH
user = userdata.mainUser
Iq = IQ_Option(user["username"],user["password"])

def spread(bid,ask):
    porcento = ask / 100
    diferenca = ask - bid
    porcentagem = diferenca / porcento

    return round(porcentagem, 5)


def get_tickers():
    try:
        maxdict=5 # set max buffer you want to save
        size =5 # candles size [1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]

        if Iq.check_connect()==False:
            Iq.connect()#if not connect it will reconnect

            # update candles size
        if interval is not None:
            size=int(interval)

        Iq.start_candles_stream(asset,size,maxdict)
        candles=Iq.get_realtime_candles(asset,size)
        for candle in list(candles):
            cand = candles[candle]
            cd_handle = {}
            if "ask" in cand:
                cd_handle = {**cand}
                if "id" in cd_handle:
                    del cd_handle['id']
                if "phase" in cd_handle:
                    del cd_handle['phase']
                if "to" in cd_handle:
                    del cd_handle['to']
                if "at" in cd_handle:
                    cd_handle['id'] = cp.copy(cd_handle['at'])
                    del cd_handle['at']
                cd_handle['spread'] = spread(float(cand["bid"]), float(cand["ask"]))

                candlesTb.insert(cd_handle).run()
                # filter to avoid duplication
                # filter_predicate = {"at": cd_handle["at"]}
                # test = candlesTb.filter(filter_predicate).count().eq(0)
                # r.branch(test, candlesTb.insert(cd_handle), None).run()

    except Exception as e:
        print("Server Error.: " + str(e))
        print(traceback.format_exc())
        pass

# checa se é domingo e se esta entre as 18 e 24
def checkSunday(day, dayNumber):
    if dayNumber == 0 and day.hour in range(18, 23) and day.minute <= 59:
        return True
    return False

# se for sexta até as 18
def checkFriday(day , dayNumber):
    if dayNumber == 5 and day.hour in range(0, 17) and day.minute <= 59:
        return True
    return False

# se for de segunda a quinta
def checkMondayToFriday(day, dayNumber):
    if dayNumber <= 4 and dayNumber >= 1:
        return True
    return False

print('Iniciando')
while True:
    try:
        day = dt.datetime.now()
        dayNumber = day.isoweekday()
        # se for algum dia para trading ele inicia
        if checkSunday(day, dayNumber) or checkFriday(day , dayNumber) or checkMondayToFriday(day, dayNumber):
            get_tickers()
        else:
            print('fora do horario de trading')
            pass
    except Exception as e:
        print("Server Error - await 5 seconds.: " + str(e))
        print(traceback.format_exc())
        pass
