from myshop.celery import app
from django.core.mail import send_mail

from .models import Order


@app.task
def order_created(order_id):
    """Задача отправки email-уведомлений при успешном оформлении заказа."""

    order = Order.objects.get(id=order_id)
    subject = f'Заказ № {order_id}'
    message = f'Уважаемый {order.first_name}.\n\nВы успешно разместили заказ. \
                Номер вашего заказа: {order.id}.'
    mail_sent = send_mail(subject, message, 'admin@myshop.company', [order.email])

    return mail_sent
