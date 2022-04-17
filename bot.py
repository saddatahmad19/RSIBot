from pickle import TRUE
import config
import websocket,json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *


SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
RSI_period = 14
RSI_overbought = 70
RSI_oversold = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANT = 0.004


closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity, sym, order_type = ORDER_TYPE_MARKET):
    try: 
        print ("Sending order")
        order = client.create_order( side=side,  quantity = quantity, symbol=sym, type = order_type)
        print(order)
    
    except Exception as e:
        return False
    return True


def on_open(ws):
    print("Oppened Connection")

def on_close(ws):
    print("Closed Connection")

def on_message(ws, message):
    global closes
    print("Recieved Message")
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if (is_candle_closed):
        print("Candle closed at {}".format(close))
        closes.append(float(close))

        if len(closes) > RSI_period:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_period)
            print("all rsi calculated so far")
            print(rsi)
            last_rsi=rsi[-1]
            print("The current rsi is {}".format(last_rsi))

            if (last_rsi > RSI_overbought):
                if in_position:
                    print("Sell!")
                    #put sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANT, TRADE_SYMBOL)
                    if (order_succeeded):
                        in_position = False

                else:
                    print("Dont own any")

            if (last_rsi < RSI_oversold):
                if in_position:
                    print("Already own!")
                else: 
                    print("Buy!")
                    #put binance order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANT, TRADE_SYMBOL)
                    if (order_succeeded):
                        in_position = True

ws = websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message)
ws.run_forever()