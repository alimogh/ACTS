#!/usr/bin/env python3

import bittrex as exchg
import acts_config as cfg

mAPI = exchg.MarketAPI  (exchg.API_V1_1, cfg.config['Bittrex']['API_KEY'].encode('utf-8'), cfg.config['Bittrex']['API_SECRET'].encode('utf-8')) 
aAPI = exchg.AccountAPI (exchg.API_V1_1, cfg.config['Bittrex']['API_KEY'].encode('utf-8'), cfg.config['Bittrex']['API_SECRET'].encode('utf-8')) 
pAPIv2 = exchg.PublicAPI  (exchg.API_V2_0)
pAPIv1 = exchg.PublicAPI  (exchg.API_V1_1)

def sell (inpQ, outQ, params, Stop):
	market, price, qty = params
	assert (type(price) is str or type(price) is int or type(price) is float)
	assert (type(qty) is str or type(qty) is int or type(qty) is float)
	price = float(price) if type(price) is int or type(price) is float else price
	qty = float(qty) if type(qty) is int or type(qty) is float else qty
	
	#print ('Sell {qty} {cur} at {pri}'.format (qty = qty, cur = market.split('-')[1], pri = price))

	while not Stop.is_set():
		if not inpQ.empty ():
			tmp = inpQ.get (block = False)
			sell_en = True if (type(tmp) is tuple and tmp[0] is True) or (tmp is True) else False
			if sell_en:
				balance_avail, balance = aAPI.get_balance (market.split('-')[1])
				price_avail, ticker = pAPIv1.get_ticker (market)
	
				if price == 'last':
					price = ticker ['Last'] if price_avail else None
				if qty == 'all':
					qty = balance ['Available'] if balance_avail else None
	
				if price is not None and qty is not None:
					#print ('Actually sell {qty} {mar} at {pri}'.format (qty = qty, mar = market, pri = price))
					order_res, msg = mAPI.sell_limit (market, qty, price)
					if order_res:
						for oq in outQ:
							oq.put ((True, msg['uuid']), block = True)
					else:
						for oq in outQ:
							oq.put ((False, msg), block = True)
	
				else:
					for oq in outQ:
						oq.put ((False, 'Can not get last price or avaiable coins'), block = True)

			inpQ.task_done ()

def buy (inpQ, outQ, params, Stop):
	market, price, qty = params
	assert (type(price) is str or type(price) is int or type(price) is float)
	assert (type(qty) is str or type(qty) is int or type(qty) is float)
	price = float(price) if type(price) is int or type(price) is float else price
	qty = float(qty) if type(qty) is int or type(qty) is float else qty

	while not Stop.is_set():
		if not inpQ.empty ():
			tmp = inpQ.get (block = False)
			sell_en = True if (type(tmp) is tuple and tmp[0] is True) or (tmp is True) else False
			if sell_en:
				balance_avail, balance = aAPI.get_balance (market.split('-')[1])
				price_avail, ticker = pAPIv1.get_ticker (market)
	
			if price is 'last':
				price = ticker ['Last'] if price_avail else None
			if qty is 'all':
				qty = balance ['Available'] if balance_avail else None
	
			if price is not None and qty is not None:
				order_res, msg = mAPI.buy_limit (market, qty, price)
				if order_res:
					for oq in outQ:
						oq.put ((True, msg['uuid']), block = True)
				else:
					for oq in outQ:
						oq.put ((False, msg), block = True)
	
			else:
				for oq in outQ:
					oq.put ((False, 'Can not get last price or avaiable coins'), block = True)

			inpQ.task_done ()

def cancel (inpQ, outQ, params, Stop):
	#TODO: cancel
	pass
