from django.db import models

# Create your models here.

class EqDailyPx(models.Model):
    """
    equity daily price-related data
    """
    ticker = models.CharField(max_length=15, null=False, help_text="ticker, symbol or code")
    trade_date = models.DateField(auto_now=False, auto_now_add=False, help_text="Date of the trading session")
    open = models.DecimalField(max_digits=10, decimal_places=4, help_text="Opening price")
    high = models.DecimalField(max_digits=10, decimal_places=4, help_text="Highest price during the day")
    low = models.DecimalField(max_digits=10, decimal_places=4, help_text="Lowest price during the day")
    last = models.DecimalField(max_digits=10, decimal_places=4, help_text="Last (or closing) price")
    prev_adj_close = models.DecimalField(max_digits=10, decimal_places=4, help_text="Previous adjusted close (for splits/dividends)")
    chg = models.DecimalField(max_digits=10, decimal_places=4, help_text="")
    pct_chg = models.DecimalField(max_digits=4, decimal_places=4, help_text="")
    volume = models.PositiveBigIntegerField(help_text="Trading volume")
    turnover = models.DecimalField(max_digits=20, decimal_places=4, help_text="")

