import logging
logger = logging.getLogger(__name__)


def send_sms_notifications(obj, mobile=None, template=None, method='msg91'):

    try:
        from comms.message91 import Message91
        from config.models import Configuration
        config = Configuration.objects.first()
        currency = config.currency_symbol

        if template is not None:
            body = template.body
            body = body.replace("*|order_no|*", obj.order_number)
            body = body.replace("*|fname|*", obj.customer.first_name.title())
            body = body.replace("*|lname|*", obj.customer.last_name.title())
            body = body.replace("*|created_on|*", obj.created_on.strftime("%-d %m %Y"))
            body = body.replace("*|total|*", currency + " " + str(obj.do_total()))
            body = body.replace("*|points|*", currency + " " + str(obj.points))
            body = body.replace("*|earned_points|*", currency + " " + str(obj.earned_points))

            body = body.replace("*|shipping_street_1|*", str(obj.shipping_address.street_1))
            body = body.replace("*|shipping_street_2|*", str(obj.shipping_address.street_2))
            body = body.replace("*|shipping_city|*", str(obj.shipping_address.city.city))
            body = body.replace("*|shipping_state|*", str(obj.shipping_address.state.state))
            body = body.replace("*|shipping_country|*", str(obj.shipping_address.country.country))
            body = body.replace("*|shipping_zip|*", str(obj.billing_address.zip))

            body = body.replace("*|billing_street_1|*", str(obj.billing_address.street_1))
            body = body.replace("*|billing_street_2|*", str(obj.billing_address.street_2))
            body = body.replace("*|billing_city|*", str(obj.billing_address.city.city))
            body = body.replace("*|billing_state|*", str(obj.billing_address.state.state))
            body = body.replace("*|billing_country|*", str(obj.billing_address.country.country))
            body = body.replace("*|billing_zip|*", str(obj.billing_address.zip))

            if method == 'msg91':
                msg = Message91()
                msg.send(
                    country="+91",
                    text=body,
                    to=mobile
                )
            else:
                logger.error('other methods not implemented')

    except Exception as e:
        logger.error("Could not send sms to customer after order was placed." + e or e)


def send_email_notifications(obj, customer=None, template=None):
    '''
    You can use this function to send
    emails to recipients other than the customer.
    Replace params in the def.

    :param email:
    :param template:
    :param mark_sent:
    :return:
    '''
    from comms.models import EmailTemplate
    from comms.communication import send_email_template

    template_object = EmailTemplate.objects.filter(slug="shipment-update").first() if not template else template
    if template_object is None:
        logger.debug("Not sending shipment update email because no template present.")
        return
    if obj.customer.email is None:
        logger.debug("Not sending shipment update email because no email present.")

    send_email_template(customer.email, template=template_object, **{
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'username': customer.user.username,
        'tracker_code': obj.tracking.tracking_code,
        'tracker_carrier': obj.tracking.carrier,
        'tracker_public_url': obj.tracking.public_url,
        'status': obj.tracking.status,
        'updated_at': obj.tracking.updated_at,
        'created_at': obj.tracking.created_at,
        'order_no': obj.order_number,
    })

    return
