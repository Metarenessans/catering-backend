from django.db import migrations

def populate_calculate_data(apps, schema_editor):
    CalculatePageSettings = apps.get_model("menu_requests", "CalculatePageSettings")
    CalculateFeature = apps.get_model("menu_requests", "CalculateFeature")
    CalculateBudgetOption = apps.get_model("menu_requests", "CalculateBudgetOption")
    CalculateFoodOption = apps.get_model("menu_requests", "CalculateFoodOption")
    CalculateStep = apps.get_model("menu_requests", "CalculateStep")
    AdditionalService = apps.get_model("menu_requests", "AdditionalService")

    settings, _ = CalculatePageSettings.objects.get_or_create(pk=1)

    # 1. Features (3 cards under hero)
    features_data = [
        {"icon": "⏱️", "title": "Смета за 15 минут", "subtitle": "Быстрый расчет в WhatsApp/Telegram", "order": 1},
        {"icon": "💰", "title": "100% бесплатно", "subtitle": "Расчет ни к чему вас не обязывает", "order": 2},
        {"icon": "🍽️", "title": "Под любой бюджет", "subtitle": "От легкого фуршета до пышного банкета", "order": 3},
    ]
    for item in features_data:
        CalculateFeature.objects.get_or_create(
            settings=settings,
            title=item["title"],
            defaults={"icon": item["icon"], "subtitle": item["subtitle"], "order": item["order"], "is_active": True}
        )

    # 2. Budget options
    budget_data = [
        "Не определились / подскажите",
        "до 15 000 ₽",
        "15 000 – 30 000 ₽",
        "30 000 – 50 000 ₽",
        "50 000 – 100 000 ₽",
        "от 100 000 ₽",
    ]
    for idx, name in enumerate(budget_data, start=1):
        CalculateBudgetOption.objects.get_or_create(
            settings=settings,
            name=name,
            defaults={"order": idx, "is_active": True}
        )

    # 3. Food options
    food_data = [
        "Горячее",
        "Салаты",
        "Закуски",
        "Десерты",
    ]
    for idx, name in enumerate(food_data, start=1):
        CalculateFoodOption.objects.get_or_create(
            settings=settings,
            name=name,
            defaults={"order": idx, "is_active": True}
        )

    # 4. Steps ("Как мы работаем")
    steps_data = [
        {
            "step": "01",
            "title": "Заполните параметры",
            "text": "Укажите в форме выше количество гостей, формат и дату события - это займет меньше минуты.",
            "order": 1,
        },
        {
            "step": "02",
            "title": "Расчет сметы за 15 мин",
            "text": "Бесплатно составим 2-3 варианта меню под ваш бюджет и пришлем в выбранный мессенджер.",
            "order": 2,
        },
        {
            "step": "03",
            "title": "Согласование деталей и предоплата",
            "text": "Корректируем меню и услуги под вас. Бронь даты - по предоплате 30%.",
            "order": 3,
        },
        {
            "step": "04",
            "title": "Доставка и оплата",
            "text": "Привозим блюда к нужной дате и времени. Расчёт - на месте при передаче.",
            "order": 4,
        },
    ]
    for item in steps_data:
        CalculateStep.objects.get_or_create(
            settings=settings,
            step=item["step"],
            defaults={"title": item["title"], "text": item["text"], "order": item["order"], "is_active": True}
        )

    # 5. Link existing AdditionalService to settings
    AdditionalService.objects.filter(settings__isnull=True).update(settings=settings)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menu_requests", "0009_alter_additionalservice_options_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_calculate_data, reverse_code=noop),
    ]
