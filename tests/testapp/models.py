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


class Note(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Notes"

    def __str__(self):
        return self.name


class Document(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Documents"

    def __str__(self):
        return self.name


class StringParent(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StringChild(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    parent = models.ForeignKey(StringParent, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
