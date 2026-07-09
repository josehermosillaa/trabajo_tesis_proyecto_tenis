from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HealthAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "OK",
                "application": "Sistema de Gestión de Torneos de Tenis",
                "version": "1.0.0",
            },
            status=status.HTTP_200_OK,
        )