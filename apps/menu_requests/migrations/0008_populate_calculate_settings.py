from django.db import migrations

def populate_initial_calculate_settings(apps, schema_editor):
    CalculatePageSettings = apps.get_model("menu_requests", "CalculatePageSettings")
    CalculateFAQ = apps.get_model("menu_requests", "CalculateFAQ")

    settings, _ = CalculatePageSettings.objects.get_or_create(
        pk=1,
        defaults={
            "hero_badge": "⚡ Бесплатный расчет за 15 минут",
            "hero_title": "Рассчитать меню кейтеринга и банкета в Набережных Челнах",
            "hero_description": "Укажите формат события, количество персон и пожелания - бесплатно составим персональное меню и смету под ваш бюджет.",
            "seo_title": "Рассчитать меню кейтеринга онлайн - Бесплатный расчет банкета и фуршета | Шеф Мил",
            "seo_description": "Бесплатный онлайн-расчёт меню кейтеринга под формат мероприятия, количество гостей и бюджет в Набережных Челнах. Персональная смета за 15 минут!",
        }
    )

    initial_faqs = [
        {
            "question": "Сколько стоит расчет меню кейтеринга?",
            "answer": "Расчет меню и составление индивидуальной сметы полностью бесплатны и ни к чему вас не обязывают. Подготовим варианты под комфортный для вас бюджет.",
            "order": 1,
        },
        {
            "question": "За сколько дней нужно бронировать кейтеринг?",
            "answer": "Расчет мы отправляем в течение 15-30 минут. Само мероприятие рекомендуем бронировать за 3 дня.",
            "order": 2,
        },
        {
            "question": "Предоставляете ли вы посуду и официантов?",
            "answer": "Да, помимо доставки готовых боксов и блюд, мы можем предоставить посуду, бокалы, текстиль и работу профессиональных официантов для обслуживания события, как доп. услуга.",
            "order": 3,
        },
        {
            "question": "Как упакованы блюда при доставке?",
            "answer": "Все закуски и блюда доставляются в стильных боксах с прозрачным окном, если боксов несколько, то они упаковываются в удобные для переноски пакеты.",
            "order": 4,
        },
    ]

    for faq in initial_faqs:
        CalculateFAQ.objects.get_or_create(
            settings=settings,
            question=faq["question"],
            defaults={
                "answer": faq["answer"],
                "order": faq["order"],
                "is_active": True,
            }
        )

def remove_initial_calculate_settings(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menu_requests", "0007_calculatepagesettings_alter_menurequest_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            populate_initial_calculate_settings,
            reverse_code=remove_initial_calculate_settings,
        ),
    ]
