from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder

# Create your models here.


class Pair_Timeframe(models.Model):
    class Meta():
        db_table = 'pair_timeframe'
        unique_together = ("pair", "timeframe")

    pair = models.CharField(max_length=10)
    timeframe = models.CharField(max_length=10)


class Candle(models.Model):
    class Meta():
        db_table = 'candle'
        unique_together = ("pair_timeframe", "mts")

    pair_timeframe  = models.ForeignKey(Pair_Timeframe, related_name='pair_timeframe_candle', on_delete=models.CASCADE)
    mts             = models.DateTimeField(db_index=True)
    open            = models.DecimalField(max_digits=200, decimal_places=40)
    close           = models.DecimalField(max_digits=200, decimal_places=40)
    high            = models.DecimalField(max_digits=200, decimal_places=40)
    low             = models.DecimalField(max_digits=200, decimal_places=40)
    volume          = models.DecimalField(max_digits=200, decimal_places=40)


class Trade(models.Model):
    class Meta():
        db_table = 'trade'

    pair_timeframe                              = models.ForeignKey(Pair_Timeframe, related_name='pair_timeframe_trade', on_delete=models.CASCADE)
    timeperiod                                  = models.PositiveSmallIntegerField()
    independent_last_sell_buy_price_checking    = models.BooleanField()
    forse_commit_sell_buy_status_distace        = models.DecimalField(default=None, null=True, max_digits=200, decimal_places=40, help_text="In minutes, # in the begining means ignore. Example: #60*24*2")
    LPP_count                                   = models.PositiveSmallIntegerField()
    EP_gradient_threshold                       = models.PositiveSmallIntegerField()
    LPP_gradients_threshold                     = models.PositiveSmallIntegerField()
    sell_threshold                              = models.DecimalField(max_digits=200, decimal_places=40, help_text="In percent")
    buy_threshold                               = models.DecimalField(max_digits=200, decimal_places=40, help_text="In percent")
    statistic_begin_time                        = models.DateTimeField()
    trading_begin_time                          = models.DateTimeField()
    trading_end_time                            = models.DateTimeField(default=None, null=True)
    is_active                                   = models.BooleanField()
    init_last_sell_price                        = models.DecimalField(max_digits=200, decimal_places=40)
    init_last_buy_price                         = models.DecimalField(max_digits=200, decimal_places=40)
    initial_BTC_wallet                          = models.DecimalField(max_digits=200, decimal_places=40)
    initial_USD_wallet                          = models.DecimalField(max_digits=200, decimal_places=40)
    div_parts                                   = models.PositiveSmallIntegerField()


class Orders_History(models.Model):
    class Meta():
        db_table = 'orders_history'

    trade                   = models.ForeignKey(Trade, related_name='trade_orders_history', on_delete=models.CASCADE)
    mts                     = models.DateTimeField()
    wallet_index            = models.PositiveSmallIntegerField()
    price                   = models.DecimalField(max_digits=200, decimal_places=40)
    amount                  = models.DecimalField(max_digits=200, decimal_places=40)
    fee_amount              = models.DecimalField(max_digits=200, decimal_places=40)
    fee_currency            = models.CharField(max_length=10)
    loss                    = models.DecimalField(default=None, null=True, max_digits=200, decimal_places=40)
    misc                    = JSONField(encoder=DjangoJSONEncoder)
    kind                    = models.CharField(max_length=10)
    usd_init_in_wallet      = models.DecimalField(max_digits=200, decimal_places=40)
    btc_init_in_wallet      = models.DecimalField(max_digits=200, decimal_places=40)
    usd_end_in_wallet       = models.DecimalField(max_digits=200, decimal_places=40)
    btc_end_in_wallet       = models.DecimalField(max_digits=200, decimal_places=40)





