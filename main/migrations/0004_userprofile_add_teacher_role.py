from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin',    'Administrateur'),
                    ('founder',  'Fondateur'),
                    ('director', 'Directeur'),
                    ('educator', 'Surveillant'),
                    ('teacher',  'Enseignant'),
                    ('cashier',  'Caissier'),
                ],
                default='admin',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='user_account',
                to='school_portal.teacher',
                verbose_name='Enseignant lié',
            ),
        ),
    ]
