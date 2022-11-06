from django.db import models



class ThrottleRate(models.Model):

    burst = models.CharField(max_length=255)
    sustained = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.burst}, {self.sustained}"


class Plan(models.Model):

    plan_name       = models.CharField(max_length=255, unique=True)
    price           = models.DecimalField(max_digits=5, decimal_places=2)
    usage_rate      = models.IntegerField()
    throttle_id     = models.ForeignKey(to=ThrottleRate, on_delete=models.SET_DEFAULT, default=0)
    date_created    = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.plan_name


    def cad_to_btc(self):
        """Get the current BTC price"""
        # TODO: this
        pass
