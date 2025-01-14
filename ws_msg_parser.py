from dtypes import *
from kollider_api_client.ws import *

def parse_msg(exchange_state, msg):
	msg = json.loads(msg)
	print(msg)
	t = msg["type"]
	data = msg["data"]
	if t == AUTHENTICATE:
		if data["message"] == "success":
			print("Authenticated Successfully!")
			exchange_state.is_authenticated = True
		else:
			print("Auth Unsuccessful: {}".format(data))
			exchange_state.is_authenticated = False

	elif t == ERROR:
		print("{}".format(msg["message"]))

	elif t == TICKER:
		pass

	elif t == INDEX_VALUE:
		index_value = parse_index_value(data)
		exchange_state.index_values[exchange_state.index_symbol] = index_value

	elif t == USER_POSITIONS:
		positions = {}
		for symbol, position in data["positions"].items():
			pos = parse_position(position)
			positions[pos.symbol] = pos
		exchange_state.positions = positions

	elif t == OPEN_ORDERS:
		oo = data['open_orders']
		for symbol in oo.keys():
			open_orders = []
			for open_order in oo[symbol]:
				dp = exchange_state.tradable_symbols[open_order["symbol"]].price_dp
				open_order_parsed = parse_open_order(open_order, dp)
				open_orders.append(open_order_parsed)
			exchange_state.open_orders[symbol] = open_orders

	elif t == USER_ACCOUNTS:
		print("Received User Accounts")
		# print(data)

	elif t == WHOAMI:
		print("Received WHOAMI")
		print(data)

	elif t == RECEIVED:
		print("Received Order Received.")
		# print(data)

	elif t == DONE:
		open_orders = exchange_state.open_orders[exchange_state.symbol]
		exchange_state.open_orders[exchange_state.symbol] = [
			order for order in open_orders if order.order_id != int(data["order_id"])]

	elif t == OPEN:
		open_order = data
		symbol = open_order["symbol"]
		dp = exchange_state.tradable_symbols[symbol].price_dp
		open_order_parsed = parse_open_order(data, dp)
		if exchange_state.open_orders.get(symbol) is not None:
			exchange_state.open_orders[symbol].append(open_order_parsed)
		else:
			exchange_state.open_orders[symbol] = [open_order_parsed]

	elif t == FAIR_PRICE:
		print("Received Fair Price")
		print(data)

	elif t == TRADABLE_SYMBOLS:
		symbols = data["symbols"]
		tradable_symbols = {}
		for symbol in symbols:
			symbol_info = symbols[symbol]
			s = parse_tradable_symbols(symbol_info)
			tradable_symbols[s.symbol] = s
		exchange_state.tradable_symbols = tradable_symbols                      

	elif t == POSITION_STATE:
		position = parse_position(data)
		if data["quantity"] != 0:
			exchange_state.positions[position.symbol] = position
		else:
			del exchange_state.positions[position.symbol]

	elif t == ORDER_REJECTION:
		print("Received Order Rejection.")
		# print(data)

	else:
		print("Unhandled type: {}".format(msg))