from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_customuser_pending_email_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='publish_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='hourly_post_limit',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name='customuser',
            name='daily_post_limit',
            field=models.PositiveIntegerField(default=30),
        ),
    ]
