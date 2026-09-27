from django.db import models


class Parent(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Children"

    def __str__(self):
        return self.name


class Grandchild(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Grandchildren"

    def __str__(self):
        return self.name
