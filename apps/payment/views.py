import stripe
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics

from order.models import Order
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

# Stripe API kalitlarini sozlash
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class PaymentInitiateView(generics.UpdateAPIView):
    def patch(self, request, order_id):

        order = get_object_or_404(Order, id=order_id)

        try:
            if Order.objects.filter(id=order_id, status='paid').exists():
                return Response({'detail':'Order is already paid.'}, status=400)
            if Order.objects.filter(id=order_id, status='shipped').exists():
                return Response({'detail':'Order has been shipped.'}, status=400)
            if Order.objects.filter(id=order_id, status='delivered').exists():
                return Response({'detail':'Order has been delivered.'}, status=400)
            if Order.objects.filter(id=order_id, status='canceled').exists():
                return Response({'detail':'Order already canceled.'}, status=400)
            card_number = request.data.get('card_number')
            expiry_month = request.data.get('expiry_month')
            expiry_year = request.data.get('expiry_year')
            cvc = request.data.get('cvc')

            # Karta ma'lumotlari to'liq emasligini tekshirish
            if not all([len(card_number), len(expiry_month), len(expiry_year), len(cvc)]):
                return Response({'detail': 'Card details are incomplete.'}, status=400)


            # Stripe to'lovni yaratish
            payment_intent = stripe.PaymentIntent.retrieve(
                amount=1000,
                currency='usd',
                payment_method_data={
                    'type': 'card',
                    'card': {
                        'number': card_number,
                        'exp_month': int(expiry_month),
                        'exp_year': int(expiry_year),
                        'cvc': cvc,
                    },
                },
            )


            order.status = 'completed'
            order.save()

            return Response({'client_secret': payment_intent['client_secret']}, status=200)

        except stripe.error.CardError as e:
            return Response({'detail': str(e)}, status=400)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=404)
        except Exception as e:
            logger.exception({f'Error is {e}'})
            return Response({'error': str(e)}, status=400)
