from django.db import migrations


def backfill_pending_email(apps, schema_editor):
    db = schema_editor.connection.database
    db['users_customuser'].update_many(
        {'pending_email': {'$exists': False}},
        {'$set': {'pending_email': None}},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_pending_email'),
    ]

    operations = [
        migrations.RunPython(backfill_pending_email, migrations.RunPython.noop),
    ]
