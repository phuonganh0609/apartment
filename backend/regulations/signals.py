"""Delete attachment bytes only after the database deletion commits."""

import logging

from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import RegulationDocument

logger = logging.getLogger(__name__)


def delete_file(storage, name):
    if name:
        try:
            storage.delete(name)
        except OSError:
            logger.exception("Could not remove regulation attachment")


@receiver(post_delete, sender=RegulationDocument)
def delete_document_file(sender, instance, using, **kwargs):
    storage, name = instance.file.storage, instance.file.name
    transaction.on_commit(lambda: delete_file(storage, name), using=using)
