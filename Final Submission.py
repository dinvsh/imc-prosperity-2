from datamodel import OrderDepth, TradingState, Order
from typing import List
import copy
import numpy as np
import math

empty_dict = {'STARFRUIT' : 0, 'AMETHYSTS' : 0, 'ORCHIDS' : 0, 'CHOCOLATE': 0, 'STRAWBERRIES': 0, 'ROSES': 0, 'GIFT_BASKET': 0, 'COCONUT': 0, 'COCONUT_COUPON': 0}
empty_dict_cache = {'STARFRUIT' : np.array([]), 'AMETHYSTS' : np.array([]), 'ORCHIDS' : np.array([]), 'CHOCOLATE' : np.array([]), 'STRAWBERRIES' : np.array([]), 'ROSES': np.array([]), 'GIFT_BASKET' : np.array([]), 'COCONUT' : np.array([]), 'COCONUT_COUPON' : np.array([])}

class Trader:
    position = copy.deepcopy(empty_dict)
    POSITION_LIMIT = {'STARFRUIT' : 20, 'AMETHYSTS' : 20, 'ORCHIDS' : 100, 'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60, 'COCONUT': 300, 'COCONUT_COUPON': 600}
    mid_cache = copy.deepcopy(empty_dict_cache)
    sunlight_cache = copy.deepcopy(empty_dict_cache)
    iv_cache = copy.deepcopy(empty_dict_cache) 
    humidity_cache = copy.deepcopy(empty_dict_cache)
    rhianna_cache = copy.deepcopy(empty_dict_cache)
    gb_cache = copy.deepcopy(empty_dict_cache)

    def find_mid_price(self, order_depth):
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0] if len(order_depth.sell_orders.items()) >= 1 else [0,0]
        best_ask_2, best_ask_amount_2 = list(order_depth.sell_orders.items())[1] if len(order_depth.sell_orders.items()) >= 2 else [0,0]
        best_ask_3, best_ask_amount_3 = list(order_depth.sell_orders.items())[2] if len(order_depth.sell_orders.items()) >= 3 else [0,0]
        max_ask_amount = min(best_ask_amount, best_ask_amount_2, best_ask_amount_3)
        if max_ask_amount == best_ask_amount:
            max_ask_index = best_ask
        elif max_ask_amount == best_ask_amount_2:
            max_ask_index = best_ask_2
        else:
            max_ask_index = best_ask_3
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0] if len(order_depth.buy_orders.items()) >= 1 else [0,0]
        best_bid_2, best_bid_amount_2 = list(order_depth.buy_orders.items())[1] if len(order_depth.buy_orders.items()) >= 2 else [0,0]
        best_bid_3, best_bid_amount_3 = list(order_depth.buy_orders.items())[2] if len(order_depth.buy_orders.items()) >= 3 else [0,0]
        max_bid_amount = max(best_bid_amount, best_bid_amount_2, best_bid_amount_3)
        if max_bid_amount == best_bid_amount:
            max_bid_index = best_bid
        elif max_bid_amount == best_bid_amount_2:
            max_bid_index = best_bid_2
        else:
            max_bid_index = best_bid_3
        mid_price = (max_ask_index + max_bid_index) / 2

        return mid_price

    def orchids(self, pos, best_bid, best_ask, conv_bid, conv_ask, transport_fees, export_tariff, import_tariff, sunlight, humidity):
       
        product = 'ORCHIDS'
        storage = 0.1 * 100
        sunlight = sunlight[product]
        humidity = humidity[product]
    
        mid_price = (best_ask + best_bid) / 2
        south_buy_price = conv_ask + transport_fees + import_tariff
        south_sell_price = conv_bid - transport_fees - export_tariff 
        
        conversion = 0
        if pos > 0 and best_bid - storage <= mid_price + 1: 
            conversion = -pos

        if pos < 0 and south_buy_price < mid_price - 1: 
            conversion = -pos

        price_spread = (best_ask - best_bid) / 2
        humidity_maxima = False
        humidity_minima = False

        if len(humidity) >= 10:
             left = np.diff(humidity[ : 4])
             right = np.diff(humidity[-4 : ])
             left_up = np.where(left >= 0, 1, 0).sum() == 4
             right_up = np.where(right >= 0, 1, 0).sum() == 4
             left_down = np.where(left <= 0, 1, 0).sum() == 4
             right_down = np.where(right <= 0, 1, 0).sum() == 4
             humidity_maxima = left_up and right_down
             humidity_minima = right_up and left_down

        ask_spread_adj = int(min(price_spread, abs(south_sell_price - (best_ask - storage))) + 2) 
        bid_spread_adj = int(abs(south_buy_price - best_bid) + 3)

        if best_ask + storage < south_sell_price or humidity_minima:
            cond = 'buy' 
        elif best_bid > south_buy_price or humidity_maxima:
            cond = 'sell'
        else: 
            cond = 'do nth'

        return cond, conversion, bid_spread_adj, ask_spread_adj

    def coconuts(self, order_depth, iv_cache, trade_product, timestamp):
        cond = 'do nth'
        product = ['COCONUT_COUPON' , 'COCONUT']
        product_mids = {}
        worst_bid_dict = {}
        worst_ask_dict = {}

        for prod in product:
            worst_ask, _ = next(reversed(order_depth[prod].sell_orders.items())) if len(list(order_depth[prod].sell_orders.items())) > 0 else [0, 0]
            worst_bid, _ = next(reversed(order_depth[prod].buy_orders.items())) if len(list(order_depth[prod].buy_orders.items())) > 0 else [0, 0]
            product_mids[prod] = self.find_mid_price(order_depth[prod])
            worst_bid_dict[prod] = worst_bid
            worst_ask_dict[prod] = worst_ask

        def phi(x): 
            return (1.0 + math.erf(x / np.sqrt(2.0))) / 2.0

        def black_scholes_call(S, K, r, sigma, T):
            d1 = (np.log( S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            return S * phi(d1) - K * np.exp(-r * T) * phi(d2)

        def vega(S, K, r, sigma, T):
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            return S * np.exp(-0.5 * d1 ** 2) / np.sqrt(2 * np.pi) * np.sqrt(T)

        def solve_iv(call_price, S, K, r, T, initial_guess = 0.2, max_iter = 1000, tol = 1e-6):
            solution = initial_guess
            for _ in range(max_iter):
                f_val = black_scholes_call(S, K, r, solution, T) - call_price
                f_prime_val = vega(S, K, r, solution, T)
                if abs(f_prime_val) < tol:
                    break
                solution = solution - f_val / f_prime_val
                if abs(f_val) < tol:
                    break
            return solution
 
        t = (246 - (timestamp / 1000000)) / 252
        s, k, r = product_mids['COCONUT'], 10000, 0.0
        sigma = iv_cache[trade_product].mean() if len(iv_cache[trade_product]) > 0 else 0.1607
        curr_sigma = solve_iv(product_mids['COCONUT_COUPON'], s, k, r, t) 
        
        theo_price = black_scholes_call(s, k, r, sigma, t)
        diff = theo_price / product_mids[trade_product] - 1
        trade_if = 0.019
        if diff > trade_if:
            cond = 'buy'
        elif diff < -trade_if:
            cond = 'sell'
        
        return cond, worst_bid_dict[trade_product], worst_ask_dict[trade_product], curr_sigma


    def run(self, state: TradingState):
        result = {}
        conversions = 0
        trader_data = "noob"
                          
        for key, val in state.position.items():
          self.position[key] = val

        result = {}
        for product in state.order_depths:  
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0] if len(order_depth.sell_orders.items()) >= 1 else [0,0]
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0] if len(order_depth.buy_orders.items()) >= 1 else [0,0]
            price_spread = best_ask - best_bid
            mid_price = self.find_mid_price(order_depth)

            if product == 'STARFRUIT':
                mid_prices = self.mid_cache[product]
                if len(mid_prices) == 10:
                    X = np.arange(1, 11).reshape(-1, 1)  
                    y = mid_prices[-10:] 
                    coefficients = np.polyfit(X.flatten(), y, 1)
                    prediction = np.polyval(coefficients, 11)
                else:
                    prediction = 5000

                starfruit_position = int(state.position.get(product, 0))

                sell_flag = 1 if best_bid > prediction else 0
                buy_flag = 1 if best_ask < prediction else 0
                spread = best_ask - best_bid
                weight = 0.95
                buy_amount = min(20, min(best_bid_amount, 20 - starfruit_position))
                sell_amount = min(20, abs(min(abs(best_ask_amount), -20 - starfruit_position)))

                if state.timestamp > 1000:
                    if buy_flag == 1 and starfruit_position < 20 and spread <= 3:
                        buy_price, sell_price = best_ask, best_bid + 1
                        curr_buy_amount = math.ceil((buy_amount * weight) / 2)
                        curr_sell_amount = -math.floor(buy_amount * (1 - weight)) if abs(-math.floor(buy_amount * (1 - weight)) + starfruit_position ) <= 20 else 0
                        orders.append(Order(product, buy_price, curr_buy_amount)) 
                        orders.append(Order(product, sell_price, curr_buy_amount))
                        orders.append(Order(product, buy_price, curr_sell_amount + 1)) 

                    elif sell_flag == 1 and starfruit_position < 20 and spread <= 3:    
                        buy_price, sell_price = best_bid, best_ask - 1
                        curr_sell_amount = -math.ceil((sell_amount * weight) / 2)
                        curr_buy_amount = math.floor(sell_amount * (1 - weight)) if abs(math.floor(sell_amount * (1 - weight)) + starfruit_position ) <= 20 else 0
                        orders.append(Order(product, sell_price, curr_sell_amount))
                        orders.append(Order(product, buy_price, curr_sell_amount)) 
                        orders.append(Order(product, sell_price, curr_buy_amount - 1)) 
            
                    else:
                        buy_price, sell_price = best_bid + 1, best_ask - 1 
                        orders.append(Order(product, sell_price, -sell_amount))
                        orders.append(Order(product, buy_price, buy_amount))


                result['STARFRUIT'] = orders

            if product == 'AMETHYSTS':
                acceptable_price_buy = 9998
                acceptable_price_sell = 10002
                
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                sell_dep = len(order_depth.sell_orders)
                buy_dep = len(order_depth.buy_orders)
                current_position = int(state.position.get(product, 0))
                sec_ask = 10005
                sec_bid = 9995
                if sell_dep >= 2:
                    sec_ask, _ = list(order_depth.sell_orders.items())[1]
                if buy_dep >= 2:
                    sec_bid, _ = list(order_depth.buy_orders.items())[1]

                if int(best_ask) <= acceptable_price_buy:
                    orders.append(Order(product, best_ask, min(20-current_position, -best_ask_amount)))
                    current_position += min(20-current_position, -best_ask_amount)

                if int(best_bid) >= acceptable_price_sell:
                    orders.append(Order(product, best_bid, max(-20-current_position, -best_bid_amount)))
                    current_position += max(-20-current_position, -best_bid_amount)

                max_sell_amt = min(20+current_position, 20+int(state.position.get(product, 0)))
                max_buy_amt = min(20-current_position, 20-int(state.position.get(product, 0)))

                if best_ask == 10000 and current_position < 0:
                    canbuy = min(abs(current_position), abs(best_ask_amount))
                    orders.append(Order(product, 10000, canbuy))
                    max_buy_amt -= canbuy
                if best_bid == 10000 and current_position > 0:
                    cansell = min(abs(current_position), abs(best_bid_amount))
                    orders.append(Order(product, 10000, -cansell))
                    max_sell_amt -= cansell
                
                
                if best_ask <= 10000 or current_position <= -10:
                    under_ask = sec_ask - 1
                    orders.append(Order(product, under_ask, -max_sell_amt))
                else:
                    under_ask = best_ask - 1
                    if current_position >= 18:
                        orders.append(Order(product, max(10000, under_ask - 2), -5))
                        max_sell_amt -= 5
                        under_ask = max(10000, under_ask - 1)
                    elif current_position >= 10:
                        under_ask = max(10000, under_ask - 1)
                    orders.append(Order(product, under_ask, -max_sell_amt))

                if best_bid >= 10000 or current_position >= 10:
                    under_bid = sec_bid + 1
                    orders.append(Order(product, under_bid, max_buy_amt))
                else:
                    under_bid = best_bid + 1
                    if current_position <= -18:
                        orders.append(Order(product, min(10000, under_bid + 2), 5))
                        max_buy_amt -= 5
                        under_bid = min(10000, under_bid + 1)
                    elif current_position <= -10:
                        under_bid = min(10000, under_bid + 1)
                    orders.append(Order(product, under_bid, max_buy_amt))

                result['AMETHYSTS'] = orders

            if product == 'ORCHIDS':
                obs = state.observations.conversionObservations[product]
                conversion_bid = obs.bidPrice
                conversion_ask = obs.askPrice
                conversion_import = obs.importTariff
                conversion_export = obs.exportTariff
                conversion_transport = obs.transportFees
                conversion_humidity = obs.humidity
                conversion_sunlight = obs.sunlight
                curr_pos = state.position.get(product, 0)

                cond, conversions, mm_bid_adj, mm_ask_adj = self.orchids(curr_pos, best_bid, best_ask, conversion_bid, conversion_ask, conversion_transport, conversion_export, conversion_import, self.sunlight_cache, self.humidity_cache)

                if cond == 'buy':
                    buy_price, sell_price = best_ask, best_bid + mm_bid_adj
                if cond == 'sell':
                    buy_price, sell_price = best_bid, best_ask - mm_ask_adj

                
                if cond == 'buy':
                    curr_buy_amount = math.ceil((buy_amount * weight) / 2)
                    curr_sell_amount = -math.floor(buy_amount * (1 - weight)) if abs(-math.floor(buy_amount * (1 - weight)) + curr_pos ) <= 100 else 0
                    orders.append(Order(product, buy_price, curr_buy_amount))
                    orders.append(Order(product, sell_price, curr_buy_amount))
                    orders.append(Order(product, buy_price, curr_sell_amount))
                    
                if cond == 'sell':
                    curr_sell_amount = -math.ceil((sell_amount * weight) / 2)
                    curr_buy_amount = math.floor(sell_amount * (1 - weight)) if abs(math.floor(sell_amount * (1 - weight)) + curr_pos ) <= 100 else 0
                    orders.append(Order(product, buy_price, curr_sell_amount))
                    orders.append(Order(product, buy_price, curr_buy_amount))
                    orders.append(Order(product, sell_price, curr_sell_amount))

                result['ORCHIDS'] = orders


            if product == 'GIFT_BASKET':
                order_depth_c: OrderDepth = state.order_depths['CHOCOLATE']
                order_depth_s: OrderDepth = state.order_depths['STRAWBERRIES']
                order_depth_r: OrderDepth = state.order_depths['ROSES']

                orders: List[Order] = []
                mid_price = self.find_mid_price(order_depth)
                mid_price_c = self.find_mid_price(order_depth_c)
                mid_price_s = self.find_mid_price(order_depth_s)
                mid_price_r = self.find_mid_price(order_depth_r)

                
                basket_pos = int(state.position.get(product, 0))
                sell_flag = 0
                buy_flag = 0

                if state.timestamp > 10000:
                    difference = self.gb_cache[product]
                    mean = np.mean(difference)
                    std = np.std(difference)
                else:
                    mean = 340
                    std = 80

                combined = 4 * mid_price_c + 6 * mid_price_s + mid_price_r + mean - std / 2

                if abs(mid_price - combined) > price_spread and state.timestamp > 0:
                    if mid_price < combined:
                        if basket_pos < 60:
                            buy_flag = 1

                    elif mid_price > combined:
                        if basket_pos > -60:
                            sell_flag = 1

            
                weight = 0.95
                buy_amount = min(60, min(best_bid_amount, 60 - basket_pos))
                sell_amount = min(60, abs(min(abs(best_ask_amount), -60 - basket_pos)))

                if buy_flag == 1:
                    buy_price, sell_price = best_ask, best_bid + 1
                    curr_buy_amount = math.ceil((buy_amount * weight) / 2)
                    curr_sell_amount = -math.floor(buy_amount * (1 - weight)) if abs(-math.floor(buy_amount * (1 - weight)) + basket_pos ) <= 60 else 0
                    orders.append(Order(product, buy_price, curr_buy_amount)) 
                    orders.append(Order(product, sell_price, curr_buy_amount))
                    orders.append(Order(product, buy_price, curr_sell_amount + 1)) 

                elif sell_flag == 1:    
                    buy_price, sell_price = best_bid, best_ask - 1
                    curr_sell_amount = -math.ceil((sell_amount * weight) / 2)
                    curr_buy_amount = math.floor(sell_amount * (1 - weight)) if abs(math.floor(sell_amount * (1 - weight)) + basket_pos ) <= 60 else 0
                    orders.append(Order(product, sell_price, curr_sell_amount))
                    orders.append(Order(product, buy_price, curr_sell_amount)) 
                    orders.append(Order(product, sell_price, curr_buy_amount - 1)) 
            
                result['GIFT_BASKET'] = orders

            if product == 'ROSES':
                pos = state.position.get(product, 0)
                rose_trades = state.market_trades.get(product, [])
                rhianna = self.rhianna_cache[product]
                if rose_trades != []:
                    for trade in rose_trades:        
                        if trade.buyer == 'Rhianna':
                            orders.append(Order(product, best_ask, 60 - pos))
                            self.rhianna_cache[product] = np.append(self.rhianna_cache[product], 1)
                        elif trade.seller == 'Rhianna':
                            orders.append(Order(product, best_bid, -60 - pos))
                            self.rhianna_cache[product] = np.append(self.rhianna_cache[product], 0)
                        
                        if len(rhianna) != 0:
                            if rhianna[-1] == 1 and pos < 60:
                                orders.append(Order(product, best_ask, 60 - pos))
                            elif rhianna[-1] == 0 and pos > -60:
                                orders.append(Order(product, best_bid, -60 - pos))

                result['ROSES'] = orders

            if product == 'COCONUT_COUPON':
                cond, bid, ask, iv = self.coconuts(state.order_depths, self.iv_cache, product, state.timestamp)
                buy_flag = 0
                sell_flag = 0
                if cond == 'buy':
                    buy_price, sell_price = ask, best_bid
                    buy_flag = 1
                if cond == 'sell':
                    buy_price, sell_price = bid, best_ask
                    sell_flag = 1
                pos = state.position.get(product, 0)

                weight = 0.95
                buy_amount = min(600, min(best_bid_amount, 600 - pos))
                sell_amount = min(600, abs(min(abs(best_ask_amount), -600 - pos)))

            
                if buy_flag == 1:
                    buy_price, sell_price = best_ask, best_bid + 1
                    curr_buy_amount = math.ceil((buy_amount * weight) / 2)
                    curr_sell_amount = -math.floor(buy_amount * (1 - weight)) if abs(-math.floor(buy_amount * (1 - weight)) + pos ) <= 600 else 0
                    orders.append(Order(product, buy_price, curr_buy_amount)) 
                    orders.append(Order(product, sell_price, curr_buy_amount))
                    orders.append(Order(product, buy_price, curr_sell_amount + 1)) 

                elif sell_flag == 1:    
                    buy_price, sell_price = best_bid, best_ask - 1
                    curr_sell_amount = -math.ceil((sell_amount * weight) / 2)
                    curr_buy_amount = math.floor(sell_amount * (1 - weight)) if abs(math.floor(sell_amount * (1 - weight)) + pos ) <= 600 else 0
                    orders.append(Order(product, sell_price, curr_sell_amount))
                    orders.append(Order(product, buy_price, curr_sell_amount)) 
                    orders.append(Order(product, sell_price, curr_buy_amount - 1)) 

                result['COCONUT_COUPON'] = orders

            window = 10
            caches = [self.mid_cache, self.sunlight_cache, self.humidity_cache]
            self.mid_cache[product] = np.append(self.mid_cache[product], mid_price)
            
            if product == 'COCONUT_COUPON':
                self.iv_cache[product] = np.append(self.iv_cache[product], iv)

            
            if product == 'ORCHIDS':
                self.humidity_cache[product] = np.append(self.humidity_cache[product], conversion_humidity)
                self.sunlight_cache[product] = np.append(self.sunlight_cache[product], conversion_sunlight)
            
            if product == 'GIFT_BASKET':
                self.gb_cache[product] = np.append(self.gb_cache[product], mid_price - 4*mid_price_c - 6*mid_price_s - mid_price_r)

            if len(self.mid_cache[product]) > window:
                for i in caches:
                    i[product] = i[product][-window:]  
            
            if len(self.iv_cache[product]) > 200:
                self.iv_cache[product] = self.iv_cache[product][-200:]
            
            if len(self.gb_cache[product]) > 1000:
                self.gb_cache[product] = self.gb_cache[product][-1000:]

        return result, conversions, trader_data
