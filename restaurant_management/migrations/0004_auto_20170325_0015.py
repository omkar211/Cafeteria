# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 00:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_management', '0003_auto_20170324_2358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fooditems',
            old_name='f_id',
            new_name='r_id',
        ),
    ]
