from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404 # Fix 1: Added import
from .models import UserProgress
from quiz.models import Quiz
from .serializers import UserProgressSerializer

class DashboardStatsView(APIView):
    def get(self, request):
        # 1. Fetch the progress object
        progress = get_object_or_404(UserProgress, user=request.user)
        
        # 2. Serialize the data (this gives us rank_title, progress_percentage, etc.)
        serializer = UserProgressSerializer(progress)
        
        # 3. Pull extra stats that aren't in the model
        total_quizzes = Quiz.objects.filter(session__user=request.user, is_completed=True).count()
        
        # 4. Combine them into one response
        data = serializer.data
        data['total_quizzes_count'] = total_quizzes # Adding the extra count
        
        return Response(data)