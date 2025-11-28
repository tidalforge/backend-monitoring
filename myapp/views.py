import json

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import InventorySerializer
from .models import Inventory

import sentry_sdk


InventoryData = [
    {"name": "wrench", "count": 1},
    {"name": "nails", "count": 1},
    {"name": "hammer", "count": 1},
]


def find_in_inventory(itemId):
    for item in InventoryData:
        if item["name"] == itemId:
            return item
    raise Exception("Item : " + itemId + " not in inventory ")


def process_order(cart):
    sentry_sdk.add_breadcrumb(
        category="Process Order",
        message="Step taken to process an order",
        level="info",
    )
    global InventoryData
    tempInventory = InventoryData
    for item in cart:
        itemID = item["id"]
        inventoryItem = find_in_inventory(itemID)
        if inventoryItem["count"] <= 0:
            raise Exception("Not enough inventory for " + itemID)
        else:
            inventoryItem["count"] -= 1
            print(
                "Success: "
                + itemID
                + " was purchased, remaining stock is "
                + str(inventoryItem["count"])
            )
    InventoryData = tempInventory


class SentryContextMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.body:
            body_unicode = request.body.decode("utf-8")
            order = json.loads(body_unicode)

            with sentry_sdk.configure_scope() as scope:
                scope.user = {"email": order["email"]}

        transactionId = request.headers.get("X-Transaction-ID")

        global InventoryData

        with sentry_sdk.configure_scope() as scope:
            if transactionId:
                scope.set_tag("transaction_id", transactionId)

            if Inventory:
                scope.set_extra("inventory", InventoryData)

        return super(SentryContextMixin, self).dispatch(request, *args, **kwargs)


class InventoreyView(SentryContextMixin, APIView):

    def get(self, request):
        results = InventorySerializer(InventoryData, many=True).data
        return Response(results)

    def post(self, request, format=None):
        body_unicode = request.body.decode("utf-8")
        order = json.loads(body_unicode)
        cart = order["cart"]
        process_order(cart)
        return Response(InventoryData)


class HandledErrorView(APIView):
    def get(self, request):
        sentry_sdk.add_breadcrumb(
            category="URL Endpoints",
            message="In the handled function",
            level="info",
        )
        try:
            "2" + 2
        except Exception as err:
            sentry_sdk.capture_exception(err)
        return Response()


class UnHandledErrorView(APIView):
    def get(self, request):
        sentry_sdk.add_breadcrumb(
            category="URL Endpoints",
            message="In the unhandled function",
            level="info",
        )
        obj = {}
        obj["keyDoesntExist"]
        return Response()


class CaptureMessageView(APIView):
    def get(self, request):
        sentry_sdk.add_breadcrumb(
            category="URL Endpoints",
            message="In the Capture Message function",
            level="info",
        )
        sentry_sdk.capture_message("You caught me!", "fatal")

        return Response()

class ErrorMasterView(APIView):
    def get(self, request):
        division_by_zero = 1 / 0
        return Response(division_by_zero)
