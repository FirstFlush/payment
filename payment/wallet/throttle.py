from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
import random


class PlanThrottle(UserRateThrottle):

    rate = '1/day'

    # def __init__(self,  *args, **kwargs):



    #     self.rate = self.get_rate()
    #     super().__init__()



    # def get_cache_key(self, request, view):
    #     return super().get_cache_key(request, view)



    # def get_rate(self):
    #     return '1/day'



class NotifyThrottle(AnonRateThrottle):

    rate = '100/day'