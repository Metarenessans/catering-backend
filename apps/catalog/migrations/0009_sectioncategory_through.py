# Generated manually to migrate Section.categories M2M to SectionCategory through-model with order

from django.db import migrations, models
import django.db.models.deletion


def copy_section_categories_forward(apps, schema_editor):
    SectionCategory = apps.get_model('catalog', 'SectionCategory')
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'catalog_section_categories'
            )
        """)
        old_table_exists = cursor.fetchone()[0]
        if not old_table_exists:
            return

        cursor.execute("""
            SELECT m2m.id, m2m.section_id, m2m.category_id, COALESCE(c.order, 0) as cat_order
            FROM catalog_section_categories m2m
            LEFT JOIN catalog_category c ON m2m.category_id = c.id
            ORDER BY m2m.section_id, cat_order, m2m.id
        """)
        rows = cursor.fetchall()

        current_section = None
        order = 1
        objects_to_create = []
        for row_id, section_id, category_id, _ in rows:
            if section_id != current_section:
                current_section = section_id
                order = 1
            objects_to_create.append(
                SectionCategory(
                    section_id=section_id,
                    category_id=category_id,
                    order=order,
                )
            )
            order += 1

        SectionCategory.objects.bulk_create(objects_to_create, ignore_conflicts=True)


def copy_section_categories_backward(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO catalog_section_categories (section_id, category_id)
            SELECT section_id, category_id FROM catalog_sectioncategory
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_section_image_section_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Порядок сортировки')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_sections', to='catalog.category', verbose_name='Категория')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_categories', to='catalog.section', verbose_name='Раздел')),
            ],
            options={
                'verbose_name': 'Категория раздела',
                'verbose_name_plural': 'Категории раздела',
                'ordering': ['order', 'id'],
                'unique_together': {('section', 'category')},
            },
        ),
        migrations.RunPython(
            copy_section_categories_forward,
            copy_section_categories_backward,
        ),
        migrations.RemoveField(
            model_name='section',
            name='categories',
        ),
        migrations.AddField(
            model_name='section',
            name='categories',
            field=models.ManyToManyField(blank=True, help_text='Выберите категории, входящие в этот раздел', related_name='sections', through='catalog.SectionCategory', to='catalog.category', verbose_name='Категории'),
        ),
    ]
