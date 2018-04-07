SECRET_KEY = 'h2)nqwc@cseyx7ayd4)*8wlw(aov5)0u390p5)5ly5h26+c(b0'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crypto_trader_db',
        'USER': 'trader',
        'PASSWORD': 'traderPassworD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# Bitfinex key
API_KEY = "your_API_key"
API_SECRET = "your_API_secret"
SERVER_ENDPOINT = "http://111.222.333.444/management/"
