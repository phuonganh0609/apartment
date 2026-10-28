from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, AuditEvent
from .audit_context import audit_actor


@receiver(user_logged_in)
def login_event(sender, user, **kwargs):
    AuditEvent.objects.create(actor=user.username, action="Đăng nhập")


@receiver(user_logged_out)
def logout_event(sender, user, **kwargs):
    if user:
        AuditEvent.objects.create(actor=user.username, action="Đăng xuất")


@receiver(user_login_failed)
def failed_event(sender, credentials, **kwargs):
    AuditEvent.objects.create(actor=str(credentials.get("username", ""))[:150], action="Đăng nhập thất bại")


@receiver(pre_save, sender=User)
def user_before(sender, instance, **kwargs):
    instance._audit_previous = User.objects.filter(pk=instance.pk).values("role", "is_active", "can_edit_deposit", "can_ai_payment_notice", "can_ai_renewal_notice", "tenant_id").first() if instance.pk else None


@receiver(post_save, sender=User)
def user_after(sender, instance, created, **kwargs):
    previous = getattr(instance, "_audit_previous", None)
    if created:
        AuditEvent.objects.create(actor=audit_actor.get(), action="Tạo tài khoản", detail=instance.username)
    elif previous:
        changes = [f"{key}: {value} → {getattr(instance, key)}" for key, value in previous.items() if value != getattr(instance, key)]
        if changes:
            AuditEvent.objects.create(actor=audit_actor.get(), action="Cập nhật tài khoản", detail=(instance.username + ": " + "; ".join(changes))[:500])
