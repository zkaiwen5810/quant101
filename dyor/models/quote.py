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
    close = models.DecimalField(max_digits=10, decimal_places=4, help_text="Closing price")
    prev_adj_close = models.DecimalField(max_digits=10, decimal_places=4, help_text="Previous adjusted close (for splits/dividends)")
    chg = models.DecimalField(max_digits=10, decimal_places=4, help_text="Change in price")
    pct_chg = models.DecimalField(max_digits=4, decimal_places=4, help_text="Percentage change in price(based on previous day's close)")
    volume = models.PositiveBigIntegerField(help_text="Trading volume(in board lots)")
    turnover = models.DecimalField(max_digits=20, decimal_places=4, help_text="Turnover(in thousand RMB)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    class Meta:
        db_table = "eq_daily_px"
        verbose_name = "Equity Daily Price"
        verbose_name_plural = "Equity Daily Prices"
        unique_together = ("ticker", "trade_date")

