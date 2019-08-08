import logging
logger = logging.getLogger(__name__)


def replace_content(template_object, obj):
    body = template_object.body
    subject = template_object.subject

    for field in ['title', 'description', 'status', 'ticket_id']:
        body = body.replace("*|" + str(field) + "|*", getattr(obj, field))
        subject = subject.replace("*|" + str(field) + "|*", getattr(obj, field))

    if obj.created_on:
        body = body.replace('*|created_on|*', str(obj.created_on.date()) + str(obj.created_on.time()))
        subject = subject.replace('*|created_on|*', str(obj.created_on.date()) + str(obj.created_on.time()))

    if obj.customer:
        body = body.replace("*|customer_first_name|*", obj.customer.first_name)
        subject = subject.replace("*|customer_first_name|*", obj.customer.first_name)
        body = body.replace("*|customer_last_name|*", obj.customer.last_name)
        subject = subject.replace("*|customer_last_name|*", obj.customer.last_name)

    if obj.assigned_to:
        body = body.replace("*|assigned_to_first_name|*", obj.assigned_to.first_name)
        subject = subject.replace("*|assigned_to_first_name|*", obj.assigned_to.first_name)
        body = body.replace("*|assigned_to_last_name|*", obj.assigned_to.last_name)
        subject = subject.replace("*|assigned_to_last_name|*", obj.assigned_to.last_name)

    return body, subject


def send_admin_email(obj, template=None):
    from comms.models import EmailTemplate

    template_object = EmailTemplate.objects.filter(slug="support-admin").first() if not template else template
    if template_object is None:
        logger.debug("Not sending support-admin confirmation email because no template present.")
        return
    if obj.customer:
        if obj.customer.email is None:
            logger.debug("Not sending support-admin confirmation email because no email present.")

    body, subject = replace_content(template_object, obj)

    from comms.postmark import send_mail

    from promotion.models import EmailSubscriber
    for sub in EmailSubscriber.objects.filter(lists__name="support-admin-notifications"):
        if sub.email:
            try:
                send_mail(subject, body, [sub.email], None)
            except Exception as e:
                logger.error("An error occurred when sending email notifications for a ticket.")


def send_customer_email(obj, template=None, email=None, from_email=None):
    from comms.models import EmailTemplate

    template_object = EmailTemplate.objects.filter(slug="support-customer").first() if not template else template
    if template_object is None:
        logger.debug("Not sending order confirmation email because no template present.")
        return

    if obj.customer:
        if obj.customer.email:
            email = obj.customer.email
    else:
        email = email

    body, subject = replace_content(template_object, obj)

    if email is None:
        logger.debug("Not sending order confirmation email because no email present.")

    from comms.communication import send_email
    try:
        send_email(subject, body, [email], None, from_email)
    except Exception as e:
        logger.error("An error occurred when sending email notifications for a ticket.")


def send_status_update_notifications(obj, template=None, email=None):
    from comms.models import EmailTemplate

    template_object = EmailTemplate.objects.filter(slug="support-customer-status-update").first() if not template else template
    if template_object is None:
        logger.debug("Not sending order confirmation email because no template present.")
        return

    if obj.customer:
        if obj.customer.email:
            email = obj.customer.email
    else:
        email = email

    body, subject = replace_content(template_object, obj)

    if email is None:
        logger.debug("Not sending order confirmation email because no email present.")

    from comms.postmark import send_mail
    try:
        send_mail(subject, body, [email], None)
    except Exception as e:
        logger.error("An error occurred when sending email notifications for a ticket.")