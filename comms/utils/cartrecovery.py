import logging
logger = logging.getLogger(__name__)


def send_sms_notifications(obj, template=None, method='msg91'):

    try:
        from comms.message91 import Message91
        from config.models import Configuration
        config = Configuration.objects.first()
        currency = config.currency_symbol

        if template is not None:
            body = template.body
            try:
                body = body.replace("*|fname|*", obj.customer.first_name.title())
                body = body.replace("*|lname|*", obj.customer.last_name.title())
                body = body.replace("*|created_on|*", obj.created_on.strftime("%-d %m %Y"))
                body = body.replace("*|total|*", currency + " " + str(obj.get_total()))

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
            except Exception as e:
                logger.error(e.message or e)

            if method == 'msg91':
                msg = Message91()
                msg.send(
                    country="+91",
                    text=body,
                    to=obj.customer.mobile
                )
            else:
                logger.error('other methods not implemented')

    except Exception as e:
        logger.error("Could not send sms to customer for cart recovery" + e.message or e)


def send_email_notifications(obj, template=None):
    from comms.models import EmailTemplate
    from config.models import Configuration
    config = Configuration.objects.first()
    currency = config.currency_symbol

    template_object = EmailTemplate.objects.filter(slug="cart-recovery").first() if not template else template
    if template_object is None:
        logger.debug("Not sending cart recovery email because no template present.")
        return
    if obj.customer.email is None:
        logger.debug("Not sending cart recovery email because no email present.")

    body = template_object.body
    subject = template_object.subject

    try:
        body = body.replace("*|fname|*", obj.customer.first_name.title() if obj.customer.first_name else "")
        body = body.replace("*|lname|*", obj.customer.last_name.title() if obj.customer.last_name else "")
        body = body.replace("*|mobile|*", obj.customer.mobile if obj.customer.mobile else "")
        body = body.replace("*|country_code|*", obj.customer.country_code if obj.customer.country_code else "")
        body = body.replace("*|email|*", obj.customer.email if obj.customer.email else "")
        body = body.replace("*|id|*", str(obj.id))
        body = body.replace("*|created_on|*", str(obj.created_on))
        body = body.replace("*|get_total|*", str(obj.get_total))
        body = body.replace("*|lowest_possible_total|*", str(obj.lowest_possible_total()))
        body = body.replace("*|get_discount|*", str(obj.get_discount()))
        body = body.replace("*|get_total_before_points|*", str(obj.get_total_before_points()))
        body = body.replace("*|get_total_in_paise|*", str(obj.get_total_in_paise()))
        body = body.replace("*|get_taxes|*", str(obj.get_taxes()))
        body = body.replace("*|number_of_items|*", str(obj.number_of_items()))
        body = body.replace("*|get_shipping|*", str(obj.get_shipping()))
        body = body.replace("*|get_points_redeemable|*", str(obj.get_points_redeemable()))
        body = body.replace("*|get_points_redeemable_logged_out|*", str(obj.get_points_redeemable_logged_out()))
        body = body.replace("*|get_total_points|*", str(obj.get_total_points()))
        body = body.replace("*|get_savings|*", str(obj.get_savings()))
        body = body.replace("*|all_products_allow_scod|*", str(obj.all_products_allow_scod))
        body = body.replace("*|all_products_allow_emi|*", str(obj.all_products_allow_emi))
        body = body.replace("*|all_products_allow_cod|*", str(obj.all_products_allow_cod))
    except Exception as e:
        logger.error(e.message or e)

    try:
        body = body.replace("*|created_on|*", obj.created_on.strftime("%-d %m %Y"))
        subject = subject.replace("*|created_on|*", obj.created_on.strftime("%-d %m %Y"))
    except Exception as e:
        logger.error(e.message or e)

    try:
        body = body.replace("*|total|*", currency + " " + str(obj.get_total()))
        subject = subject.replace("*|total|*", currency + " " + str(obj.get_total()))
    except Exception as e:
        logger.error(e.message or e)

    try:
        if obj.shipping_address:
            body = body.replace("*|shipping_street_1|*", str(obj.shipping_address.street_1))
            body = body.replace("*|shipping_street_2|*", str(obj.shipping_address.street_2))
            body = body.replace("*|shipping_city|*", str(obj.shipping_address.city.city))
            body = body.replace("*|shipping_state|*", str(obj.shipping_address.state.state))
            body = body.replace("*|shipping_country|*", str(obj.shipping_address.country.country))
            body = body.replace("*|shipping_zip|*", str(obj.billing_address.zip))
    except Exception as e:
        logger.error(e.message or e)

    try:
        if obj.billing_address:
            body = body.replace("*|billing_street_1|*", str(obj.billing_address.street_1))
            body = body.replace("*|billing_street_2|*", str(obj.billing_address.street_2))
            body = body.replace("*|billing_city|*", str(obj.billing_address.city.city))
            body = body.replace("*|billing_state|*", str(obj.billing_address.state.state))
            body = body.replace("*|billing_country|*", str(obj.billing_address.country.country))
            body = body.replace("*|billing_zip|*", str(obj.billing_address.zip))
    except Exception as e:
        logger.error(e.message or e)

    rows = None
    try:
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
                                                        currency + str(item.get_line_total())]]) + "</tr>"
            )

        rows.append(
            "<tr style='border: 1px solid lightgray;'>" +
            ''.join(["<td>" + x + "</td>" for x in ["", "", "", "Total", currency + " " + str(obj.get_total())]])
            + "</tr>"
        )
    except Exception as e:
        logger.error(e.message or e)

    table = "<table style='width: 100%;'><tbody>" + ''.join(rows or "") + "</tbody></table>"
    body = body.replace("*|table|*", table)

    from comms.postmark import send_mail
    try:
        send_mail(subject, body, [obj.customer.email], None)
    except Exception as e:
        logger.error("An error occurred when sending cart recovery email notifications." + e.message or e)

    return

