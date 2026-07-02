from django.db import models

class Division(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Upazila(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UnionWard(models.Model):
    name = models.CharField(max_length=100)
    upazila = models.ForeignKey(Upazila, on_delete=models.CASCADE)

    #  these lines change "UnionWard object (4)" into readable text like "Ward 04 - Mirpur"
    def __str__(self):
        return self.name