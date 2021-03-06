from hashlib import sha256
import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe


def device_directory_path(instance, filename):
    instance.image.open()  # make sure we're at the beginning of the file
    content = instance.image.read()
    hash = sha256(content).hexdigest()
    fname, ext = fname, ext = os.path.splitext(filename)
    return '{0}/{1}{2}'.format(str(instance.uuid).replace('-', ''), hash, ext)


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return "{0}".format(self.name)


class Device(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    wifi_signature = models.CharField(max_length=1000)
    mac_vendor = models.CharField(max_length=255)
    category = models.ForeignKey(Category, null=True)
    comment = models.CharField(max_length=500, blank=True, default='')
    image = models.ImageField(upload_to=device_directory_path, blank=True, null=True)
    image_url = models.CharField(max_length=250, blank=True, default='')
    approved = models.BooleanField(default=False)

    def __str__(self):
        return "{0} - {1}".format(self.name, self.uuid)

    def thumbnail(self):
        if self.image_url:
            return mark_safe('<img src="%s%s" width="50px" height="50px"/>' % (settings.MEDIA_URL, self.image_url))
        else:
            return ""

    def get_categories(self):
        categories = []
        parent = self.category

        while parent is not None:
            categories.append(parent.name)
            parent = parent.parent

        return categories

    def get_path(self):
        path = ""

        for cat in reversed(self.get_categories()):
            path += cat.replace('/', '-') + '/'

        path += str(self.uuid).replace('-', '') + '/'

        return path
