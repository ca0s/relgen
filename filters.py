def filter_evens(n):
	return (int(n) % 2) == 0

def filter_odds(n):
	return (int(n) % 2) != 0

filters = {
	'odds': filter_odds,
	'evens': filter_evens
}
