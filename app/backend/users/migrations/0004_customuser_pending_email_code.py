from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_backfill_pending_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='pending_email_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='pending_email_code_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
