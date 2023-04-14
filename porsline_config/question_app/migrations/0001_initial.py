# Generated by Django 4.1.7 on 2023-04-13 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DropDownOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='folders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(choices=[('optional', 'Optional'), ('drop_down', 'Drop Down'), ('text_answer', 'Text Answer'), ('number_answer', 'Number Answer'), ('integer_range', 'Integer Range'), ('integer_selective', 'Integer Selective'), ('picture_field', 'Picture Field'), ('email_field', 'Email Field'), ('link', 'Link'), ('file', 'File'), ('group', 'Group')], max_length=50)),
                ('is_required', models.BooleanField(default=False)),
                ('media', models.FileField(blank=True, null=True, upload_to='question_media')),
            ],
        ),
        migrations.CreateModel(
            name='DropDownQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('multiple_choice', models.BooleanField(default=False)),
                ('max_selected_options', models.PositiveIntegerField(blank=True, null=True)),
                ('min_selected_options', models.PositiveIntegerField(blank=True, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='EmailFieldQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='FileQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('max_volume', models.PositiveIntegerField(blank=True, default=5, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='IntegerRangeQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('min', models.PositiveIntegerField(blank=True, choices=[(0, '1'), (1, '0')], default=1, null=True)),
                ('max', models.PositiveIntegerField(blank=True, default=5, null=True)),
                ('min_label', models.CharField(blank=True, max_length=50, null=True)),
                ('mid_label', models.CharField(blank=True, max_length=50, null=True)),
                ('max_label', models.CharField(blank=True, max_length=50, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='IntegerSelectiveQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('shape', models.CharField(choices=[('H', 'Heart'), ('S', 'Star'), ('L', 'Like'), ('C', 'Check Mark')], default='S', max_length=2)),
                ('max', models.PositiveIntegerField(blank=True, default=5, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='LinkQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='NumberAnswerQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('min', models.IntegerField(blank=True, default=0, null=True)),
                ('max', models.IntegerField(blank=True, default=1000, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='OptionalQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('multiple_choice', models.BooleanField(default=False)),
                ('additional_options', models.BooleanField(default=False)),
                ('max_selected_options', models.IntegerField(blank=True, null=True)),
                ('min_selected_options', models.IntegerField(blank=True, null=True)),
                ('all_options', models.BooleanField(blank=True, default=False, null=True)),
                ('nothing_selected', models.BooleanField(blank=True, default=False, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='PictureFieldQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('answer', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='TextAnswerQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='question_app.question')),
                ('min', models.PositiveIntegerField(blank=True, default=10, null=True)),
                ('max', models.PositiveIntegerField(blank=True, default=1000, null=True)),
            ],
            bases=('question_app.question',),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=False)),
                ('has_timer', models.BooleanField(default=False)),
                ('has_auto_start', models.BooleanField(default=False)),
                ('pub_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('timer', models.DurationField(blank=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questionnaires', to='question_app.folder')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionnaires', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='question_app.questionnaire'),
        ),
        migrations.CreateModel(
            name='OptionSelection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_selected', models.BooleanField(default=False)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selections', to='question_app.option')),
            ],
        ),
        migrations.CreateModel(
            name='DropDownSelection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_selected', models.BooleanField(default=False)),
                ('drop_down_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selections', to='question_app.dropdownoption')),
            ],
        ),
        migrations.CreateModel(
            name='TextAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.textanswerquestion')),
            ],
        ),
        migrations.CreateModel(
            name='PictureAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ImageField(upload_to='uploads/images')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.picturefieldquestion')),
            ],
        ),
        migrations.AddField(
            model_name='option',
            name='optional_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='question_app.optionalquestion'),
        ),
        migrations.CreateModel(
            name='NumberAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.numberanswerquestion')),
            ],
        ),
        migrations.CreateModel(
            name='LinkAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.URLField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.linkquestion')),
            ],
        ),
        migrations.CreateModel(
            name='IntegerSelectiveAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.integerselectivequestion')),
            ],
        ),
        migrations.CreateModel(
            name='IntegerRangeAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.integerrangequestion')),
            ],
        ),
        migrations.CreateModel(
            name='FileAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.FileField(upload_to='uploads')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.filequestion')),
            ],
        ),
        migrations.CreateModel(
            name='EmailAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.EmailField(max_length=254)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='question_app.emailfieldquestion')),
            ],
        ),
        migrations.AddField(
            model_name='dropdownoption',
            name='drop_down_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='question_app.dropdownquestion'),
        ),
    ]
