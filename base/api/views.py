from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def getRoutes(request):
    """
    Point d'entrée de l'API qui retourne la liste des routes disponibles.
    
    Cette vue publique fournit une documentation de base des endpoints
    disponibles dans l'API pour aider les développeurs.
    """
    routes = [
        '/api/token/',
        '/api/token/refresh/',
        '/api/incidents/',
        '/api/incidents/<id>/',
        '/api/users/',
        '/api/profiles/',
        '/api/notes/',
    ]
    return Response(routes)