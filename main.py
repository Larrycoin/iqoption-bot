import requests, json
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
import numpy as np
from argparse import ArgumentParser
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from threading import Thread
from sklearn.ensemble import BaggingClassifier
from iqoptionapi.stable_api import IQ_Option
import userdata
import traceback

## get args

parser = ArgumentParser()
parser.add_argument("-a", "--asset", dest="asset", required=True,
                    help="Pass the asset:(EURUSD, AUDUSD, XEMUSD-l ...)", metavar="ASSET")

parser.add_argument("-i", "--interval", dest="interval", required=False,
                    help="Pass interval in seconds: [1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,'all']", metavar="TIME")

parser.add_argument("-f", "--file-sufix", dest="filesufix", required=False,
                    help="Pass sufix to file ", metavar="SUFIX")

args = parser.parse_args()

asset = args.asset
fileSufix = ''
if args.filesufix is not None:
    fileSufix = args.filesufix

## AUTH
user = userdata.mainUser
Iq= IQ_Option(user["username"],user["password"])

## SETUP ASSETS

assetFrom = asset[:3]
assetTo = asset[3:]
goal= asset
fileName= 'data/' + asset + fileSufix + '.csv'

isThereFile = os.path.isfile(fileName)
lgr = LogisticRegression(random_state=0	, solver='lbfgs',multi_class='auto', max_iter=5000, verbose=1, tol=0.0001)
bagging = BaggingClassifier(lgr, max_samples=0.5, max_features=0.5)
## SETUP PARAMS

window = 360             # window Dimension for calculation of indicators
variance = 3.5             # Indicators window variance dimension
batch_size = 360         # Lot Memory Dimension to train the model ( features - X )
interval = args.interval # Interval between ticker queries on the server
dim = 360                # window Dimension for displaying the indicators

## ---------------------------------


X = []
Y = []
bets = 0
history_bid = []
history_ask = []

history_lowerBand = []
history_upperBand = []

history_buys = []
history_sells = []
history_signal = []

index_buys = []
index_sells = []

history = ["","","","","",""]

X_temp = [0,0,0,0,0,0]
epoch = 0


batch = []
buys = [0,0,0,0,0,0]
sells = [0,0,0,0,0,0]

signal_action = ['','','','','','']

if isThereFile:
    pass
else:
    record = open(fileName,"w")
    record.write("bid,ask\n")
    record.close()


fig = plt.figure(figsize=(10,10))

ax = fig.gca()

def resetMemory():
    global history_buys, history_sells, index_buys, index_sells

    history_buys = []
    history_sells = []
    index_buys = []
    index_sells = []


def bollingerBands(bid, ask, window, variance):

    if len(bid) > window:
        media = bid.rolling(window= window).mean()
        rolling_std  = bid.rolling(window= window).std()
        upperBand = media + (rolling_std * variance)
        lowerBand = media - (rolling_std * variance)




        #ax.plot(media, '--', color = 'gray', alpha = 0.3)
        ax.plot(upperBand, '--', color = 'green', alpha = 0.5)
        ax.plot(lowerBand, '--', color = 'red', alpha = 0.2)


        #ax.scatter(len(ask),media[-1:], color = 'gray', alpha = 0.1)
        ax.scatter(len(ask),upperBand[-1:], color = 'green', alpha = 0.1)
        ax.scatter(len(ask),lowerBand[-1:], color = 'red', alpha = 0.1)
        return lowerBand, upperBand



    else:
        print("Not enough data to create Bollinger bands")




def detect_cross(bid, ask, lowerBand, upperBand, index, spread):

    history_bid.append(bid)
    history_ask.append(ask)
    history_lowerBand.append(lowerBand)
    history_upperBand.append(upperBand)


    del history_bid[:-dim]
    del history_ask[:-dim]
    del history_lowerBand[:-dim]
    del history_upperBand[:-dim]

    # percentSpread = spread / 100



    if len(history_signal) > 1:

        if history_bid[-1:] > history_lowerBand[-1:] and history_bid[-2:-1] < history_lowerBand[-2:-1]:
            history_buys.append(float(ask))
            index_buys.append(index)
            signal_action = 1

        elif history_bid[-1:] < history_upperBand[-1:] and history_bid[-2:-1] > history_upperBand[-2:-1]:
            history_sells.append(float(bid))
            index_sells.append(index)
            signal_action =2
        else:

            signal_action = 0
    else:

        signal_action = 0
    history_signal.append(signal_action)

    return signal_action



def plotsTrading(bid,ask, lowerBand, upperBand, spread):
    resetMemory()

    for i in range(len(bid)-(window), len(bid)):
        signal_action = detect_cross(float(bid[i]), float(ask[i]), float(lowerBand[i]), float(upperBand[i]), i, spread)

    if len(history_buys) > 0:
        ax.scatter(index_buys, history_buys, marker = '^', color = "green", label ="Buy")
        for c in range(len(index_buys)):
            ax.text(index_buys[c], history_buys[c], '- buy', color = "black", alpha = 0.8)

    if len(history_sells) > 0:
        ax.scatter(index_sells, history_sells, marker = 'v', color = "red", label = "Sell" )
        for v in range(len(index_sells)):
            ax.text(index_sells[v], history_sells[v], '- sell', color = "black", alpha = 0.8)

    return signal_action

def spread(bid,ask):
    porcento = ask / 100
    diferenca = ask - bid
    porcentagem = diferenca / porcento

    return porcentagem


def get_tickers():
    #size=[1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]
	size =5
	if interval is not None:
		size=int(interval)

	maxdict=100
	Iq.start_candles_stream(goal,size,maxdict)
	time.sleep(1)
	cc=Iq.get_realtime_candles(goal,size)
	for k in cc:
		if "ask" in cc[k]:
			ask = cc[k]["ask"]
			bid = cc[k]["bid"]
			## tempo = cc[k]["at"]
			print("ask: " + str(ask) + " bid: " + str(bid))

			record = open(fileName, "a")
			record.write(str(bid)+","+str(ask)+'\n')
			record.close()


def ema(values, period):
    """ Numpy implementation of EMA
    """
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:period] = a[period]
    return a


def main():
    global epoch, history, bets

    df = pd.read_csv(fileName)

    if len(df) > 1:
        ax.clear()
        bid = df['bid']
        ask = df['ask']
        # tempo = pd.to_datetime(df['time'], unit="ns")
        j = window * 3



        diferenca = ask[-1:] - bid[-1:]
        porcentagem = spread(bid[-1:],ask[-1:])

        ax.text(len(ask) + 10, bid[-1:] + (diferenca/2), "Spread " + str(np.around(float(porcentagem),3)) + "%")


        plt.title("TRAINNING - " + goal + " - " + interval)

        if len(bid) < window:
            ax.set_xlim(0, len(bid)+(len(bid)/4)+5)

        else:
            ax.set_xlim(len(bid)-window, len(bid)+100)
            bid_min = np.array(bid[-window:]).min()
            ask_max = np.array(ask[-window:]).max()
            ax.set_ylim(bid_min-(bid_min * .001),ask_max+(ask_max * .001))




        ax.plot(bid, label = "Bid - Sell "+ assetFrom + " " + str(np.around(float(bid[-1:]),8)), color = 'black', alpha = 0.5)
        ax.plot(ask, label = "Ask - Buy "+ assetFrom + " " + str(np.around(float(ask[-1:]),8)), color = 'gray', alpha = 0.5)


        plt.legend()

        ax.scatter(len(ask)-1,ask[-1:], color = 'black', alpha = 1)
        ax.scatter(len(bid)-1,bid[-1:], color = 'gray', alpha = 1)
        if len(bid) > window * 3:
            bid_mean = float(bid[-1:] / bid[0])
            ask_mean = float(ask[-1:] / ask[0])
            worthIt = 0.5
            for ind in range(0,6):

                 lowerBand, upperBand = bollingerBands(bid, ask, int(window*worthIt), variance)
                 signal_action[ind] = plotsTrading(bid,ask, lowerBand, upperBand, spread)
                 worthIt += .5

            del batch[:-batch_size - 10]
            batch.append([[signal_action[0]], [signal_action[1]],[signal_action[2]],[signal_action[3]], [signal_action[4]], [signal_action[5]], [bid_mean], [ask_mean]])



            if len(batch) >= batch_size:
                for ind in range(0,6):

                    if signal_action[ind] == 1:
                        if history[ind] != "BUY":
                            buys[ind] = float(ask[-1:])
                            X_temp[ind] = batch[-batch_size:]
                            # print("--**--** BUY - ", str(float( buys[ind])))
                            bets += 1

                        elif history[ind] == "BUY":
                            X.append(X_temp[ind])
                            Y.append(0)
                            X_temp[ind] = batch[-batch_size:]
                            buys[ind] = float(ask[-1:])
                            epoch += 1


                        history[ind] = "BUY"


                    if signal_action[ind] == 2 and history[ind] == "BUY":
                        sells[ind] = float(bid[-1:])
                        epoch += 1
                        bets += 1
                        profit = float(float(sells[ind]) - float(buys[ind]))
                        # print("--**--** SELL ", str(float( sells[ind]))," - Lucro = US$ ", str(profit))
                        if profit > 0:
                            try:
                                X.append(X_temp[ind])
                                Y.append(np.array(1))
                                X.append(batch[-batch_size:])
                                Y.append(np.array(2))
                            except:
                                pass
                        if profit <= 0 or history[ind] =="SELL":
                            try:
                                X.append(X_temp[ind])
                                Y.append(np.array(0))
                                X.append(batch[-batch_size:])
                                Y.append(np.array(0))
                            except:
                                pass


                        history[ind] = "SELL"

        try:
            X_0 = np.array(X)
            X0 = X_0.reshape(len(Y),-1)
            y = np.array(Y)



        except:
            pass

        if epoch % 50 == 0 and epoch > 0:

             tt = Thread(target=save, args=[lgr,epoch,X0,y])
             tt.start()
        if len(batch) < batch_size:
            print("Batch Total", len(batch))
        # print("Epoch - ", str(epoch))
        sleepFor = 5
        if interval is not None:
            sleepFor = int(interval)
        plt.pause(sleepFor)


volta = 1

def save(lgr,epoch,X0,y):
    bagging.fit(X0,y)
    joblib.dump(bagging, "models/model-"+str(epoch)+".pkl", compress=3)
    # print("--*--* saved Model - model-"+str(epoch)+".pkl")


while True:
    print("--------------------------- ")
    print("Lances = ", bets)
    print("Tickers - ", volta)
    volta += 1
    try:
        get_tickers()
    except Exception as e:
        print("Server Error - await 5 seconds.: " + str(e))
        print(traceback.format_exc())
        time.sleep(3)
        pass
    main()
