#!/usr/bin/env python3
from . import misc_utils as misc
from pandas import DataFrame

class BaseSeeker (misc.BPA):
	def __init__ (self, source, params):
		misc.BPA.__init__ (self, source = source, params = params)
		self.archieve = list ()
		self.pdarchieve = DataFrame ()
		self.archieve_len = 0
		if len(params) > 0:
			self.setParams (params)
		self._investment = 0
		self._qty_bought = 0
		self.studies = dict ()
		self.prediction = dict ()

	def setParams (self, params):
		misc.BPA.setParams (self, params)
		self._goal = self._params ['goal']
		self._fee  = self._params ['fee']

	def check_profit_achieved (self, price):
		gprice = price * (1 - self._fee)
		return (gprice * self._qty_bought) > (self._investment)
	
	def check_goal_achieved (self, price):
		gprice = price * (1 - self._fee)
		return (gprice * self._qty_bought) > (self._investment*(1 + self._goal))  

	def store (self, data):
		self.archieve.append (data)
		self.pdarchieve = self.pdarchieve.append (data, ignore_index = True)
		self.archieve_len += 1
		self.prediction = dict ()
	
	def predict (self, factor, data):
		if (self.archieve_len > 0 and data ['T'] != self.archieve [-1]['T']) or (self.archieve_len == 0):
			self.store (data)
		
		return self.call_predict (factor, data) if factor not in self.prediction.keys() else self.prediction [factor]

	def call_predict (self, factor, data):
		if factor == 'hitgoal':
			return self.check_goal_achieved (data['O'] if data['C'] > data['O'] else data['C'])
		if factor == 'trend':
			return self.predict_trend (data)
		if factor == 'profitable':
			return self.predict_profitable (data)
		if factor == 'harvestable':
			return self.predict_harvestable (data)

	def predict_trend (self, data):
		ptrend = True
		self.prediction ['trend'] = ptrend
		return ptrend

	def predict_profitable (self, data):
		ptb = True
		self.prediction ['profitable'] = ptb
		return ptb

	def predict_harvestable (self, data):
		hvb = True
		self.prediction ['harvestable'] = hvb
		return hvb

	def CallBack (self, data):
		if data[0] == 'buy':
			self._investment = data[2]['price'] + data[2]['fee']
			self._qty_bought = data[2]['qty']
