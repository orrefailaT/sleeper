# Generated by Django 4.1 on 2022-08-10 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0009_rename_creator_id_commissioner_creator_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissioner',
            name='creator',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='freeagent',
            name='creator',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='trade',
            name='creator',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='waiver',
            name='creator',
            field=models.CharField(max_length=80),
        ),
    ]
