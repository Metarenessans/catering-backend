from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product, ProductExtraInfo
from apps.faq.models import FaqItem
from apps.company.models import CompanyInfo
from apps.menu_requests.models import EventFormat, AdditionalService

class Command(BaseCommand):
    help = 'Load mock data from frontend/src/mock-data.ts'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading categories...')
        categories_data = [
            {"slug": "profitable", "name": "Выгодно🔥"},
            {"slug": "kids-menu", "name": "Детское меню"},
            {"slug": "premium-boxes", "name": "Боксы премиум"},
            {"slug": "assorted-snacks", "name": "Ассорти -сет закусок"},
            {"slug": "bruschetta-crostini-tapas", "name": "Брускеты кростини тапас"},
            {"slug": "canapes", "name": "Канапе"},
            {"slug": "piece-bruschetta-crostini", "name": "Штучно брускетты, кростини"},
            {"slug": "piece-canapes", "name": "Штучно канапе закуски"},
            {"slug": "tartlets-profiteroles", "name": "Тарталетки профитроли"},
            {"slug": "rolls", "name": "Рулетики"},
            {"slug": "juliennes", "name": "Жульены"},
            {"slug": "salads", "name": "Салаты"},
            {"slug": "hot", "name": "Горячее"},
            {"slug": "gastro-travel", "name": "Гастро-путешествие"},
            {"slug": "menu-options", "name": "Варианты меню"},
            {"slug": "soups", "name": "Супы, бульоны"},
            {"slug": "brunches", "name": "Бранчи, нарезки, под напитки"},
            {"slug": "pancake-boxes", "name": "Блинные боксы"},
            {"slug": "snacks-cups", "name": "Закуски в стаканчиках, рюмках"},
            {"slug": "desserts", "name": "Десерты"},
            {"slug": "romantic", "name": "Романтик на двоих"},
            {"slug": "pies", "name": "Пироги, пирожки, намазки"},
            {"slug": "services", "name": "Услуги"},
        ]
        
        for i, c_data in enumerate(categories_data):
            Category.objects.update_or_create(
                slug=c_data["slug"],
                defaults={"name": c_data["name"], "order": i}
            )

        self.stdout.write('Loading products...')
        products_data = [
            {
                "category_slug": "profitable",
                "image_url": "https://media.dodostatic.com/image/r:520x520/0198b6a3a845764da214bdec0c72370f.avif",
                "name": "Выгодный сет закусок",
                "extraInfo": [{"amount": 50, "unit": "шт."}, {"amount": 1200, "unit": "гр."}],
                "price": 6900,
                "oldPrice": 12000,
                "description": "Ассорти: Рулеты крабовый и грибной, 20шт..."
            },
            {
                "category_slug": "kids-menu",
                "image_url": "https://media.dodostatic.com/image/r:520x520/019ca7c9ceed74e0bec72b434f788981.avif",
                "name": "Детский набор мини-закусок",
                "extraInfo": [{"amount": 20, "unit": "шт."}, {"amount": 500, "unit": "гр."}],
                "price": 3500,
            },
            {
                "category_slug": "premium-boxes",
                "image_url": "https://media.dodostatic.com/image/r:520x520/019ca7c9ceed74e0bec72b434f788981.avif",
                "name": "Премиум бокс ассорти",
                "extraInfo": [{"amount": 80, "unit": "шт."}, {"amount": 2000, "unit": "гр."}],
                "price": 12000,
            },
        ]
        
        for i, p_data in enumerate(products_data):
            category = Category.objects.filter(slug=p_data["category_slug"]).first()
            prod, _ = Product.objects.update_or_create(
                name=p_data["name"],
                defaults={
                    "category": category,
                    "image_url": p_data["image_url"],
                    "price": p_data["price"],
                    "old_price": p_data.get("oldPrice"),
                    "description": p_data.get("description", ""),
                    "order": i,
                    "is_featured": p_data["category_slug"] == "profitable",
                }
            )
            prod.extra_info.all().delete()
            for extra in p_data.get("extraInfo", []):
                ProductExtraInfo.objects.create(
                    product=prod,
                    amount=extra["amount"],
                    unit=extra["unit"]
                )

        self.stdout.write('Loading FAQs...')
        faq_data = [
            {
                "question": "Доставка",
                "answerItems": [
                    "Доставка по Новому городу при заказе от 10000 бесплатно",
                    "Другие районы по тарифу такси, доставляем сами.До подъезда",
                ]
            },
            {
                "question": "Халяль ",
                "answerItems": ["Халяль по запросу, замена ингредиентов"]
            },
        ]
        
        for i, faq in enumerate(faq_data):
            FaqItem.objects.update_or_create(
                question=faq["question"],
                defaults={"answer_items": faq["answerItems"], "order": i}
            )

        self.stdout.write('Loading company info...')
        CompanyInfo.load()

        self.stdout.write('Loading Event Formats & Additional Services...')
        formats = [
            "Юбилей", "Свадьба", "Фуршет", "Корпоратив", "Детский праздник", "Доставка", "Самовывоз", "Другое"
        ]
        for i, fmt in enumerate(formats):
            EventFormat.objects.update_or_create(name=fmt, defaults={"order": i})

        services = [
            {"id": "1", "label": "Выездное накрытие столов"},
            {"id": "2", "label": "Официанты"},
            {"id": "3", "label": "Аренда посуды"},
            {"id": "4", "label": "Аренда мебели"},
        ]
        for i, svc in enumerate(services):
            AdditionalService.objects.update_or_create(label=svc["label"], defaults={"order": i})

        self.stdout.write(self.style.SUCCESS('Successfully loaded mock data.'))
