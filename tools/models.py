from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
## Used to handle thumbnails
from PIL import Image
from io import BytesIO
import pathlib
from django.core.files.base import ContentFile
##

THUMBNAIL_SIZE = 90, 90

# Create your models here.
class ShoppingItems(models.Model):
    name = models.CharField(primary_key = True, max_length = 255)
    unit = models.CharField(blank = True, null = True, max_length = 255)
    reorder_quantity = models.FloatField(blank = True, null = True, default = 0.0)
    max_quantity = models.FloatField(blank = True, null = True, default = 0.0)
    image = models.ImageField(upload_to="tools/shopping/")
    thumbnail = models.ImageField(upload_to="tools/shopping/", editable = False)
    active = models.BooleanField(default = True)

    ## Below taken from https://stackoverflow.com/a/43011898/3225832
    def save(self,*args,**kwargs):
        if not self.image.closed:
            if not self.make_thumbnail():
                raise Exception("Could not create thumbnail.")

        return super().save(*args,**kwargs)

    def make_thumbnail(self):

        image = Image.open(self.image)
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        path = pathlib.Path(self.image.name)
        thumb_filename = path.stem + '_thumb' + path.suffix

        if (ext := path.suffix.lower()) in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif ext == '.gif':
            FTYPE = 'GIF'
        elif ext == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True


class ShoppingItemsAdmin(admin.ModelAdmin):
    list_display = ("name","active")

class ShoppingListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(ShoppingItems, on_delete = models.CASCADE)
    quantity = models.FloatField(blank = True, null = True)
    reorder_flag = models.BooleanField(blank = True, default = False)
    last_update = models.DateField(auto_now = True)

    class Meta:
        unique_together = (("user", "item"),)

class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ("user","item")
