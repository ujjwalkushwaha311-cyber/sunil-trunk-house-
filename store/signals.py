from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_store_groups(sender, **kwargs):
    if sender.name != 'store':
        return

    complaint_permissions = Permission.objects.filter(
        content_type__app_label='store',
        content_type__model='complaint',
        codename__in=[
            'add_complaint',
            'change_complaint',
            'delete_complaint',
            'view_complaint',
        ],
    )

    group, created = Group.objects.get_or_create(name='Complaint Staff')
    group.permissions.set(complaint_permissions)
    group.save()
