from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CompanyInfo, LegalDocument, PrivacyPolicy
from apps.catalog.revalidate import notify_frontend_revalidate


@receiver(post_save, sender=CompanyInfo)
@receiver(post_delete, sender=CompanyInfo)
def company_info_changed(sender, instance, **kwargs):
    notify_frontend_revalidate("company", "")


@receiver(post_save, sender=LegalDocument)
@receiver(post_delete, sender=LegalDocument)
def legal_document_changed(sender, instance, **kwargs):
    notify_frontend_revalidate("legal_document", instance.slug)


@receiver(post_save, sender=PrivacyPolicy)
@receiver(post_delete, sender=PrivacyPolicy)
def privacy_policy_changed(sender, instance, **kwargs):
    notify_frontend_revalidate("privacy", "")


