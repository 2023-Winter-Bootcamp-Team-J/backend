from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('user', '0001_initial'),  # 'user' 앱의 초기 마이그레이션에 의존한다고 가정
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='user.user')),
                ('content', models.CharField(blank=True, max_length=200)),
                ('image_url', models.CharField(max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
    ]
