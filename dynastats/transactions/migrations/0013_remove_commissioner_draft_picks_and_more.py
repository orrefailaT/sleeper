# Generated by Django 4.1 on 2022-09-16 05:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0012_alter_commissioner_creator_alter_freeagent_creator_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commissioner',
            name='draft_picks',
        ),
        migrations.RemoveField(
            model_name='freeagent',
            name='draft_picks',
        ),
        migrations.RemoveField(
            model_name='waiver',
            name='draft_picks',
        ),
    ]
