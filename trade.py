# Made_by_mm0ck3r (Korea University, Cyber Defence 22)

import time
import pyupbit
import telegram as tel

acc_key = "#YOUR_ACC_KEY#"
sec_key = "#YOUR_SEC_KEY#"

# send message : bot.sendMessage(chat_id=chat_id, text="Test Message")
bot = tel.Bot(token="#YOUR_TOKEN#")
chat_id = 5215157582

# price_ratio = [1, 0.985, 0.97, 0.955, 0.94, 0.92]
buy_ratio = [0.05, 0.1, 0.05, 0.1, 0.25, 0.45]
price_ratio = [1, 0.99, 0.975, 0.95, 0.925, 0.915]

sell_target_ratio = [1.003, 1.004, 1.004, 1.006, 1.006, 1.012]

will_volume = list()
upbit = pyupbit.Upbit(acc_key, sec_key)
buy_uuid = list()
def check_step(price):
    if price >= 2000000: return 1000
    elif price >= 1000000: return 500
    elif price >= 500000: return 100
    elif price >= 100000: return 50
    elif price >= 10000: return 10
    elif price >= 1000: return 5
    elif price >= 100: return 1
    elif price >= 10: return 0.1
    elif price >= 1: return 0.01
    elif price >= 0.1: return 0.001
    else: return 0.0001

def set_by_price(price):
    pass

def set_limit_least_sell_price(price, per):
    origin = price*per
    step = check_step(origin)
    mod = origin % step
    if mod == 0: return origin
    else: return (origin - mod + step)

ticker = "KRW-XLM"
price_curr = None
idx = 1
is_Buy = False
sell_uuid = None
msg = ""
my_money = None
avg_price = None
while(True):
    if(is_Buy == False):
        will_volume.clear()
        idx = 1
        price_curr = pyupbit.get_current_price(ticker)
        my_money = upbit.get_balance()
        buy_money = my_money * 0.999
        buy_uuid_0 = upbit.buy_market_order(ticker, int(buy_money * buy_ratio[0]))['uuid']
        buy_uuid.append(buy_uuid_0)
        time.sleep(0.3)
        avg_price = upbit.get_avg_buy_price(ticker)
        volume = upbit.get_balance(ticker)
        will_volume.append(str(volume))
        sell_uuid = upbit.sell_limit_order(ticker, set_limit_least_sell_price(avg_price, sell_target_ratio[0]), volume)['uuid']
        msg += f"start : {str(int(my_money))} \n\n"
        msg += f"Buy at {str(avg_price)} success\nsell_market_order : {str(set_limit_least_sell_price(avg_price, 1.003))}\nand it will be buy at\n"
        
        for i in range(1, 6):
            time.sleep(0.3)
            price_will_buy = int(price_curr * price_ratio[i])
            volume_will_buy = buy_money * buy_ratio[i] / price_will_buy
            A = upbit.buy_limit_order(ticker, price_will_buy, volume_will_buy)
            buy_uuid_n = A['uuid']
            volume_n = A['volume']
            buy_uuid.append(buy_uuid_n)
            will_volume.append(volume_n)
            msg += f"{str(price_will_buy)} : {str(int(buy_money * buy_ratio[i]))}\n"
        for i in range(0, 6): print(f"Buy_UUID : {buy_uuid[i]} and it's type : {type(buy_uuid[i])}")
        is_Buy = True
        bot.sendMessage(chat_id=chat_id, text=msg)
        msg = ""

    if(is_Buy == True):
        time.sleep(0.5)
        if(upbit.get_balance_t(ticker) == 0): #sell Success
            time.sleep(0.3)
            will_cancel = upbit.get_order(ticker)
            for i in range(idx, 6):
                upbit.cancel_order(buy_uuid[i])
                time.sleep(0.3)
            msg += f"Good ! \n {str(int(my_money))} => {str(int(upbit.get_balance()))}\n"
            bot.sendMessage(chat_id=chat_id, text=msg)
            is_Buy = False
            idx=1
            buy_uuid = list()
            sell_uuid = None
        else:
            A = None
            avg_new = upbit.get_avg_buy_price(ticker)
            time.sleep(1)
            while(A is None):
                A = upbit.get_order(ticker, state='done')
                time.sleep(0.5)
            A_uuid = list()
            for i in A[0:10]:
                A_uuid.append(i['uuid'])
            if(idx < 6):
                B = None
                while(B is None):
                    B = upbit.get_order(buy_uuid[idx])
                    time.sleep(0.5)
                if(B['state'] == 'done'):
                    upbit.cancel_order(sell_uuid)
                    time.sleep(0.5)
                    avg_price = upbit.get_avg_buy_price(ticker)
                    volume = upbit.get_balance(ticker)
                    time.sleep(0.5)
                    sell_uuid = upbit.sell_limit_order(ticker, set_limit_least_sell_price(avg_price, sell_target_ratio[idx]), volume)['uuid']
                    msg += f"avg changed {str(avg_price)}\ntarget : {str(set_limit_least_sell_price(avg_price, sell_target_ratio[idx]))}\n"
                    bot.sendMessage(chat_id=chat_id, text=msg)
                    msg = ""
                    idx += 1
            elif(idx == 6 and avg_new * 0.95 > pyupbit.get_current_price(ticker)):
                upbit.cancel_order(sell_uuid)
                volume = upbit.get_balance(ticker)
                upbit.sell_market_order(ticker, volume)
                msg += f"Sorry.\n"
                bot.sendMessage(chat_id=chat_id, text=msg)
                msg = ""
                idx = 1
                sell_uuid = None
                buy_uuid = list()
                is_Buy = False
        time.sleep(1)
