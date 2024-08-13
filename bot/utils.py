# bot/utils.py

import ccxt

def get_exchange_client(exchange_class, config):
    exchange = exchange_class({
        'apiKey': config['api_key'],
        'secret': config['api_secret'],
    })
    if 'api_password' in config:
        exchange.password = config['api_password']
    return exchange
