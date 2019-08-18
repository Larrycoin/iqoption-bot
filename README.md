# iqoption-bot [beta]

![vendabaixo](docs/iqobot.png)

iqoption bot is a simple ml realtime in training using LogisticRegression

it use bollinger bands to determinate if buy or sell

This code is initially based on [Saulo Catharino's code](https://github.com/saulocatharino/machine_learning_for_traders)<br>

thanks for iqoption api to [Lu-Yi-Hsun](https://github.com/Lu-Yi-Hsun/iqoptionapi)

thanks for this [renko library](https://github.com/quantroom-pro/pyrenko) and this [brick size Optimization](https://towardsdatascience.com/renko-brick-size-optimization-34d64400f60e)

NOTE:

- it not buy or sell on iqoption yet you must pay attencion to chart and do it manually
- Do tests on test account
- Give a star if it helps you

## Summary

- [Contribute with Community](#contribe)
- [PYTHON VERSION 3.7](#pythonversion)
- [How to start](#howtostart)
- [discover for assets](#discoverassets)
- [Save in database](#database)
- [TODO](#todo)
- [TIPS AND STRATEGY](#tipsStrategy)
- [SUPPORT PROJECT](#support)

<div id='contribe'/>

## Contribute with Community

Do fork<br>
do your changes<br>
do pull request with an explanation to be easy to understand why and what you have changed<br>
Be happy !!!

Please send me suggestions ... feedbacks are welcome

<div id='pythonversion'/>

### PYTHON VERSION

I'm using anaconda with python 3.7

<div id='howtostart'/>

## How to start

I'm using anaconda with python 3 to reduce time installing things

```
conda create -n myenviqoption
conda activate myenviqoption
pip install -r requirements.txt
pip install -U git+git://github.com/Lu-Yi-Hsun/iqoptionapi.git

```

rename userdata-sample.py to userdata.py

than:

```
python main.py -a EURUSD
Or
python main.py -a USDJPY -i 15 -f '-015'
```

```
-a : It is the asset you wanna trade
-i : the interval you wanna use [1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,'all']
-f : file sufix name
```

You can also use renko to better analyse tendence

```
python historicalrenko.py -a USDJPY -i 15

# or streaming
## this second command is under test and it may generate wrong stream

python streamrenko.py -a USDJPY -i 15
```

chart examples

![vendabaixo](https://i.imgur.com/dm4WxCs.png)

<div id='discoverassets'/>

## discover for assets

just change the number to identify which asset is

https://iqoption.com/traderoom/asset/1244?type=crypto&noAlternative=1

<div id='database'/>

## Save in database

To save iqoption data to rethinkdb:

- [install rethinkdb](https://computingforgeeks.com/how-to-install-rethinkdb-on-ubuntu/)
- create database called 'iqoption'
- create table 'candles'
- run fallowing code:

```
python rethinkdb.py -a EURUSD -i 5
```

<div id='todo'/>

## TODO

- Graphical interface web or desktop
- Test other models
  - logistic regression with lbfgs
  - test different parameter to SVC
  - way to classify moviments
- Optimize training with error function
- Create backtest to improve tests
- Use clean code to improve code
- [analise backtrader](https://www.backtrader.com/)
- Add function to load trained model
- create public database to store historical data( It will need donation to server manteinance )
- Create pipeline to deploy in a server
- unit tests

<div id='tipsStrategy'/>

## Tips

when spread is big and asset has small changes it doesn't compensate to start bull or sell

spread < 0,30
change 0.08 %

Best strategy: buy once when there are signals and if there is many signals close just do one one buy with profit 1%

It is high risk to use just in tranament account

if you have any strategy let us know in an issue with prefix: [STRATEGY]

IMPORTANT: Don't be naivy, don't use it in real account

<div id='support'/>

## Support this project

I'll be really happy if you support this project.

Contribute [here](https://www.patreon.com/rafaelfaria)

It will be used to:

- create server to historical data
- improve code
- create web interface
- develop new features

## DATA

- [Graphql iqoption](<https://fininfo.iqoption.com/api/graphql?query=query%20GetActivesForQuotesPage(%24userGroupID%3A%20UserGroupID!%2C%20%24locale%3A%20LocaleName!)%20%7B%0A%20%20actives(userGroupID%3A%20%24userGroupID)%20%7B%0A%20%20%20%20id%0A%20%20%20%20ticker%0A%20%20%20%20name(source%3A%20TradeRoom%2C%20locale%3A%20%24locale)%0A%20%20%20%20__typename%0A%20%20%7D%0A%7D%0A&operationName=GetActivesForQuotesPage&variables=%7B%22userGroupID%22%3A%201%2C%20%22locale%22%3A%20%22pt_PT%22%7D>)
- [Historical data](https://static.cdnpub.info/api/quotes-history/quotes/2.0?to=1557273599&from=1557190801&active_id=1)

New test open 3 terminals

```
python assets.py -a USDJPY -i 5
python assets.py -a USDJPY -i 15 -f '-015'
python assets.py -a USDJPY -i 30 -f '-30'
python assets.py -a USDJPY -i 60 -f '-60'
```

when boilinger hit at same time buy/sell in at least 2 charts

good spread is less then 0.020

take a profit 1%
