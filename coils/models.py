"""
Definition of models.
"""
## This module
from inventory.models import Inventory

## Builtin
import io
import datetime
## Backend
from django.db import models
from django import forms
from django.contrib import admin

## Third Party
## All of these are for QR code reading and writing
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pyzbar import pyzbar
import pyqrcode


## DATABASE FLOWCHART AT: https://drive.google.com/file/d/0BwZSKBgxjIOoZ0w0aVJrb1FPMTQ/view?usp=sharing
## NOTE: Methods inherits from Models, so DON'T IMPORT HERE!

# Create your models here.

## ALL DATES SHOULD BE FIRST-OF-MONTH

class SteelCoil(models.Model):
    """ Registers steel coils (with weight and width), generating an ID number, and tracks 3 timestamps: recieving, opened, and finished """
    size = models.FloatField(verbose_name="Size of Coil", null = False, blank = False)
    weight = models.FloatField(verbose_name="Weight of Coil")
    width = models.FloatField(verbose_name="Width of Coil")
    received = models.DateTimeField(verbose_name = "Received Date", auto_now_add = True)
    opened = models.DateTimeField(verbose_name = "Opened Date", null = True, blank = True)
    finished = models.DateTimeField(verbose_name = "Finished Date", null = True, blank = True)
    notes = models.TextField(null = True, blank = True)

    @property
    def stage(self):
        if self.finished: return "Finished"
        if self.opened: return "Opened"
        if self.received: return "Received"

    @property
    def stage_date(self):
        stage = self.stage
        if stage == "Finished": return self.finished
        if stage == "Opened": return self.opened
        if stage == "Received": return self.received

    def generate_qr(self):
        """ Generates the Coil's qr code """
        return pyqrcode.create(self.pk)

    def qroutput(self, scale = 10, quiet_zone = 4):
        """ Creates the QR Printable Image
        
        quiet_zone's default is currently 4 at the module level
        """
        qr = self.generate_qr()
        f = io.BytesIO()
        ## Scale 31 is 899 px
        qr.png(f,scale = scale, quiet_zone = quiet_zone)
        img = Image.open(f)
        ctx = ImageDraw.Draw(img)
        x,y = img.size
        font = ImageFont.truetype("arial.ttf",64)
        label = f"Coil {self.pk}: {self.size}"
        tx,ty = textsize = ctx.textsize(label, font = font)
        ctx.text((x//2-tx//2, y-ty-2), label, align = 'center', font=font)
        del ctx
        return img

    def decode_qr(qrcode):
        """ Decodes the given qrcode """
        image = Image.open(qrcode)
        image = np.array(image)
        image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
        result = SteelCoil._thresholdimage(image)
        if not result: return
        coilid = result[0].data.decode()
        coil = SteelCoil.objects.filter(pk = coilid).first()
        return coil

    def _thresholdimage(image):
        ## Try basic thresholding
        im = SteelCoil._clean_qr(image)
        result = pyzbar.decode(im)
        if result: return result
        for mode in range(1,3):
            for block_size in range(11,402,50):
                im = SteelCoil._clean_qr(image, mode = mode, block_size = block_size)
                result = pyzbar.decode(im)
                if result: return result

    def _clean_qr(image, mode = 0, block_size = 11):
        """ Applies some filtering to improve qr recognition """
        if mode == 0:
            ret,image = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
        else:
            thresh = [cv2.ADAPTIVE_THRESH_MEAN_C, cv2.ADAPTIVE_THRESH_GAUSSIAN_C][mode-1]
            image = cv2.adaptiveThreshold(image, 255, thresh, cv2.THRESH_BINARY, block_size, 10)

        return Image.fromarray(image)

    def save(self, *args, **kwargs):
        if not self.finished:
            self.finished = None
        return super().save(*args,**kwargs)

class SteelCoilAdmin(admin.ModelAdmin):
    list_display = ("pk","size","width")

class SteelCoilForm(forms.ModelForm):
    """ SteelCoilEntry Form """
    class Meta:
        model = SteelCoil
        fields = ["size","weight","width"]

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("weight"):
            self.add_error("weight","No weight supplied")
        if not cleaned_data.get("width"):
            self.add_error("width","No width supplied")


class InventoryCoil(models.Model):
    """ A record of coils that were counted as inventory """
    coil = models.ForeignKey("SteelCoil", models.DO_NOTHING, blank = False, null = False)
    item = models.ForeignKey("inventory.Inventory", models.DO_NOTHING, blank = False, null = False)
    width = models.FloatField(verbose_name = "Width of Coil")

    @property
    def weight(self):
        ratio = self.coil.weight / self.coil.width
        return ratio * self.width