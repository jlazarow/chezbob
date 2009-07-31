from django.db import models

class Entity(models.Model):
    class Meta:
        db_table = 'cashout_entity'

    name = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return "%s" % self.name


class CashOut(models.Model):
    class Meta:
        db_table = 'cashout_cashout'
        permissions = [("view_cashouts", "View CashOut Ledger")]

    datetime = models.DateTimeField('Collection Time')
    notes = models.TextField()

    def __unicode__(self):
        return "%s %s" % (self.datetime, self.notes)

    @classmethod
    def fetch_all(cls):

        entitys = {}
        for e in Entity.objects.all():
            entitys[e.id] = e

        result = []

        cashouts = CashOut.objects.all().order_by('datetime')
        for cashout in cashouts:
            counts = CashCount.objects.filter(cashout=cashout)
            result.append([cashout, counts])

        return result

    def delete(self):
        CashCount.objects.filter(cashout=self).delete()
        super(CashOut, self).delete() # Call the real save func


class CashCount(models.Model):
    class Meta:
        db_table = 'cashout_cashcount'

    cashout = models.ForeignKey(CashOut)
    entity = models.ForeignKey(Entity)
    memo = models.CharField(max_length=256, blank=True)

    bill100 = models.IntegerField('$100')
    bill50  = models.IntegerField('$50')
    bill20  = models.IntegerField('$20')
    bill10  = models.IntegerField('$10')
    bill5   = models.IntegerField('$5')
    bill1   = models.IntegerField('$1')
    coin100 = models.IntegerField('&cent;100') # \xa2 is cent symbol
    coin50  = models.IntegerField('&cent;50')
    coin25  = models.IntegerField('&cent;25')
    coin10  = models.IntegerField('&cent;10')
    coin5   = models.IntegerField('&cent;5')
    coin1   = models.IntegerField('&cent;1')
    other   = models.DecimalField(max_digits=12, decimal_places=2)
    total   = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Meta-data
    fields = (
            'bill100',
            'bill50',
            'bill20',
            'bill10',
            'bill5',
            'bill1',
            'coin25',
            'coin10',
            'coin5',
            'coin1',
            'other',
            'coin100',
            'coin50',
            'total'
            )

    field_names = (
            '$100',
            '$50',
            '$20',
            '$10',
            '$5',
            '$1',
            '&cent;25',
            '&cent;10',
            '&cent;5',
            '&cent;1',
            'other',
            '&cent;100',
            '&cent;50',
            'total'
            )

    field_values = {
            'bill100' : 100,
            'bill50' : 50,
            'bill20' : 20,
            'bill10' : 10,
            'bill5' : 5,
            'bill1' : 1,
            'coin25' : 0.25,
            'coin10' : 0.10,
            'coin5' : 0.05,
            'coin1' : 0.01,
            'other' : 1,
            'coin100' : 1.00,
            'coin50' : 0.50,
            'total' : 1
            }


    def save(self):
        total = 0

        for f in CashCount.fields[:-1]:
            total += self.__dict__[f] * CashCount.field_values[f]

        self.total = total

        super(CashCount, self).save() # Call the real save func
