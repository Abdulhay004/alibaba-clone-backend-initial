import stripe
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from order.models import Order
from cart.models import Cart
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import logging

from user.serializers import ResetPasswordSerializer

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

class PaymentConfirmView(generics.UpdateAPIView):
    @method_decorator(csrf_exempt)  # CSRF himoyasini o'chirish
    def patch(self, request, order_id):
        try:
            if not Order.objects.filter(status='pending').exists():
                return Response({'detail': 'Order payment status cannot be updated.'}, status=400)
            if not request.user.is_authenticated:
                return Response(status=401)
            groups = request.user.groups.first()
            if groups == None:
                return Response(status=403)

            client_secret = request.data.get('client_secret')

            order = Order.objects.get(id=order_id)
            transaction_id = order.transaction_id

            payment_intent = stripe.PaymentIntent.confirm(transaction_id)
            order.status = 'paid'
            order.save()

            Cart.objects.filter(user=request.user).delete()

            if payment_intent['status'] == 'succeeded':
                return Response({'status': 'succeeded'}, status=200)
            else:
                return Response({'detail': 'Order payment status cannot be updated.'}, status=400)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class PaymentCreateLinkView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            if Order.objects.filter(id=id, status='canceled').exists():
                return Response({'detail':'Order already canceled.'}, status=400)
            if not Order.objects.filter(id=id, status='pending').exists():
                return Response({'detail':'Order cannot be updated.'}, status=400)

            # Guruhni tekshirish
            groups = request.user.groups.first()
            if groups == None:
                return Response(status=403)

            order = Order.objects.get(id=id, user=request.user, status='pending')
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found or not pending.'}, status=status.HTTP_404_NOT_FOUND)
        except Order.MultipleObjectsReturned:
            return Response({'detail': 'Multiple orders found for this ID.'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': 'YOUR_PRICE_ID', # Replace with your actual price ID
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri('api/payment/'+str(order.pk)+'/success/'),
                cancel_url=request.build_absolute_uri('api/payment/'+str(order.pk)+'/cancel/'),
                metadata={"order_id": order.id}
            )
            order.transaction_id = session['id']
            order.save()
            return Response({'url': session['url']}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception({f'Error is {e}'})
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated] # Crucial: Add permission

    def patch(self, request, order_id):
        # Permissionni tekshirish
        groups = request.user.groups.first()
        if groups == None:
            return Response(status=403)
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Order.MultipleObjectsReturned:
            return Response({'detail': 'Multiple orders found for this ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if order.status != 'pending' and order.status != 'new': # Crucial check
            return Response({'detail': 'Order cannot be updated.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Crucial: Check if transaction ID exists.
            if not order.transaction_id:
                return Response({'detail': 'Transaction ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            session = stripe.checkout.Session.retrieve(order.transaction_id)

            if session['payment_status'] == 'paid':
                order.status = 'paid'
                order.is_paid = True
                order.save()
                return Response({'detail': 'Order updated successfully.'}, status=status.HTTP_200_OK)
            else:
                order.status = 'failed' # Important
                order.save()
                return Response({'detail': 'Payment failed.'}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception({f'Error is {e}'})
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)