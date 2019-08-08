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
            body = body.replace("*|payment_method|*", str(obj.payment.process.method.name))

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


def send_email_notifications(obj, email=None, template=None, mark_sent=True):
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
    from config.models import Configuration
    config = Configuration.objects.first()
    currency = config.currency_symbol

    template_object = EmailTemplate.objects.filter(slug="order-confirmation").first() if not template else template
    if template_object is None:
        logger.debug("Not sending order confirmation email because no template present.")
        return
    if obj.customer.email is None and email is None:
        logger.debug("Not sending order confirmation email because no email present.")

    body = template_object.body
    subject = template_object.subject

    body = body.replace("*|order_no|*", obj.order_number)
    subject = subject.replace("*|order_no|*", obj.order_number)

    body = body.replace("*|fname|*", obj.customer.first_name.title() if obj.customer.first_name else "")
    body = body.replace("*|lname|*", obj.customer.last_name.title() if obj.customer.last_name else "")
    body = body.replace("*|mobile|*", obj.customer.mobile if obj.customer.mobile else "")
    body = body.replace("*|country_code|*", obj.customer.country_code if obj.customer.country_code else "")
    body = body.replace("*|email|*", obj.customer.email if obj.customer.email else "")

    body = body.replace("*|created_on|*", obj.created_on.strftime("%-d %m %Y"))
    subject = subject.replace("*|created_on|*", obj.created_on.strftime("%-d %m %Y"))

    body = body.replace("*|total|*", currency + " " + str(obj.do_total()))
    subject = subject.replace("*|total|*", currency + " " + str(obj.do_total()))

    body = body.replace("*|points|*", currency + " " + str(obj.points))
    body = body.replace("*|earned_points|*", currency + " " + str(obj.earned_points))
    body = body.replace("*|savings|*", currency + " " + str(obj.savings))

    if obj.payment:
        body = body.replace("*|payment_id|*",  str(obj.payment.id))
        body = body.replace("*|payment_process_id|*",  str(obj.payment.process.id))
        body = body.replace("*|payment_method|*", str(obj.payment.process.method.name))

    if obj.shipping_address:
        body = body.replace("*|shipping_street_1|*", str(obj.shipping_address.street_1))
        body = body.replace("*|shipping_street_2|*", str(obj.shipping_address.street_2))
        body = body.replace("*|shipping_city|*", str(obj.shipping_address.city.city))
        body = body.replace("*|shipping_state|*", str(obj.shipping_address.state.state))
        body = body.replace("*|shipping_country|*", str(obj.shipping_address.country.country))
        body = body.replace("*|shipping_zip|*", str(obj.billing_address.zip))

    if obj.billing_address:
        body = body.replace("*|billing_street_1|*", str(obj.billing_address.street_1))
        body = body.replace("*|billing_street_2|*", str(obj.billing_address.street_2))
        body = body.replace("*|billing_city|*", str(obj.billing_address.city.city))
        body = body.replace("*|billing_state|*", str(obj.billing_address.state.state))
        body = body.replace("*|billing_country|*", str(obj.billing_address.country.country))
        body = body.replace("*|billing_zip|*", str(obj.billing_address.zip))

    rows = list()
    rows.append(
        "<tr style='border: 1px solid lightgray;'>" +
        ''.join(["<td>" + x + "</td>" for x in ["<b>Product<b>", "<b>Quantity</b>", "<b>Cost</b>",
                                                "<b>Discounted Cost</b>", "<b>Total</b>"]])
        + "</tr>"
    )
    for item in obj.items.all():
        rows.append(
            "<tr style='border: 1px solid lightgray;'>" +
            ''.join(["<td>" + x + "</td>" for x in [str(item.product.title)[:30].rsplit(' ', 1)[0],
                                                    str(item.quantity), currency + str(item.product.cost),
                                                    currency + str(
                                                        item.product.sale_cost) if item.product.sale_cost else "N/A",
                                                    currency + str(item.total_cost)]]) + "</tr>"
        )

    rows.append(
        "<tr style='border: 1px solid lightgray;'>" +
        ''.join(["<td>" + x + "</td>" for x in ["", "", "", "Total", currency + " " + str(obj.do_total())]])
        + "</tr>"
    )

    table = "<table style='width: 100%;'><tbody>" + ''.join(rows) + "</tbody></table>"
    body = body.replace("*|table|*", table)

    from comms.postmark import send_mail
    try:
        send_mail(subject, body, [obj.customer.email if not email else email], None)
    except Exception as e:
        logger.error("An error occurred when sending email notifications.")

    if mark_sent:
        obj.order_confirmation_notifications_sent = True
        obj.save()

    # Send push notifications
    from comms.push.push import push
    user_id = obj.customer.user.id if obj.customer else 0
    title = "New Order " + obj.order_number + " on " + config.merchant_name
    body = "Your order at " + config.merchant_name + " has been successfully placed. "
    push('user-'+str(user_id), {'title': title, 'body': body})

    return