from django.db import models


class EqBasic(models.Model):
    """
    Stock Basic Information Model
    Corresponds to Tushare Pro API: stock_basic
    Documentation: https://tushare.pro/document/2?doc_id=25
    """
    
    ticker = models.CharField(max_length=20, primary_key=True, help_text="ticker, symbol or code")
    code = models.CharField(max_length=10, help_text="Stock Code or Security Code")
    name = models.CharField(max_length=100, help_text="Stock Name")
    area = models.CharField(max_length=50, null=True, blank=True, help_text="Region")
    industry = models.CharField(max_length=100, null=True, blank=True, help_text="Industry")
    fullname = models.CharField(max_length=200, null=True, blank=True, help_text="Full Stock Name")
    enname = models.CharField(max_length=200, null=True, blank=True, help_text="English Full Name")
    cnspell = models.CharField(max_length=50, null=True, blank=True, help_text="Pinyin Abbreviation")
    market = models.CharField(max_length=20, null=True, blank=True, help_text="Market Type (Main Board/ChiNext/STAR/CDR/BSE)")
    exchange = models.CharField(max_length=10, null=True, blank=True, help_text="Exchange Code")
    curr_type = models.CharField(max_length=10, null=True, blank=True, help_text="Trading Currency")
    list_status = models.CharField(max_length=1, null=True, blank=True, help_text="Listing Status: L=Listed, D=Delisted, P=Suspended")
    list_date = models.DateField(null=True, blank=True, help_text="Listing Date")
    delist_date = models.DateField(null=True, blank=True, help_text="Delisting Date")
    is_hs = models.CharField(max_length=1, null=True, blank=True, help_text="Shanghai-Shenzhen-Hong Kong Stock Connect: N=No, H=Shanghai Connect, S=Shenzhen Connect")
    act_name = models.CharField(max_length=200, null=True, blank=True, help_text="Name of the Actual Controller")
    act_ent_type = models.CharField(max_length=200, null=True, blank=True, help_text="Nature of the Actual Controller's Enterprise")
    
    # Data management fields
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation Time")
    updated_at = models.DateTimeField(auto_now=True, help_text="Update Time")
    
    class Meta:
        db_table = 'eq_basic'
        verbose_name = 'Equity Basic Information'
        verbose_name_plural = 'Equity Basic Information'
        ordering = ['ticker']
        indexes = [
            models.Index(fields=['ticker']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['industry']),
            models.Index(fields=['market']),
        ]
    
    def __str__(self):
        return f"{self.ticker} - {self.name}"
    
    @property
    def is_listed(self):
        """Whether the stock is listed"""
        return self.list_status == 'L'
    
    @property
    def is_delisted(self):
        """Whether the stock is delisted"""
        return self.list_status == 'D'
    
    @property
    def is_suspended(self):
        """Whether the stock is suspended from listing"""
        return self.list_status == 'P'
