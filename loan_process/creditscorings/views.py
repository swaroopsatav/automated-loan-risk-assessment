from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from .models import CreditScoreRecord
from .serializers import (
    CreditScoreDetailSerializer,
    AdminCreditScoreSerializer
)
from creditscorings.utils import score_and_record
from loanapplications.models import LoanApplication
from django.db import transaction
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


# --- View My Loan's Credit Score ---
class CreditScoreByLoanView(generics.RetrieveAPIView):
    """
    View to allow authenticated users to see their loan's credit score details.
    """
    serializer_class = CreditScoreDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict the queryset to the credit scores belonging to the authenticated user.
        """
        return CreditScoreRecord.objects.select_related('loan_application').filter(user=self.request.user)

    def get_object(self):
        """
        Retrieve the credit score record for a specific loan ID.
        """
        loan_id = self.kwargs.get('loan_id')
        if not loan_id:
            raise NotFound("Loan ID is required")

        try:
            return self.get_queryset().get(loan_application__id=loan_id)
        except CreditScoreRecord.DoesNotExist:
            raise NotFound("Credit score not found for the specified loan.")


# --- Admin: View All Credit Scores ---
class AdminCreditScoreListView(generics.ListAPIView):
    """
    View for admin users to list all credit scores.
    """
    serializer_class = AdminCreditScoreSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return CreditScoreRecord.objects.select_related('user', 'loan_application').all()


# --- Admin: View One Credit Score ---
class AdminCreditScoreDetailView(generics.RetrieveAPIView):
    """
    View for admin users to retrieve detailed information about a specific credit score.
    """
    serializer_class = AdminCreditScoreSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return CreditScoreRecord.objects.select_related('user', 'loan_application').all()


# --- Admin: Rescore a Loan on Demand ---
class RescoreLoanView(APIView):
    """
    Admin-only endpoint to re-score a loan application. Deletes the old credit score record if it exists.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, loan_id):
        try:
            loan = LoanApplication.objects.select_related('credit_scoring_record').get(pk=loan_id)

            with transaction.atomic():
                # Delete old score if it exists
                if hasattr(loan, 'credit_scoring_record'):
                    loan.credit_scoring_record.delete()

                # Re-run and save new score
                credit_score = async_to_sync(score_and_record)(loan)

                return Response({
                    "detail": "Loan rescored successfully.",
                    "credit_score_id": credit_score.id
                }, status=status.HTTP_200_OK)

        except LoanApplication.DoesNotExist:
            raise NotFound("Loan not found.")
        except Exception as e:
            logger.error(f"Error rescoring loan {loan_id}: {str(e)}", exc_info=True)
            return Response(
                {"error": "An error occurred while rescoring the loan."},
                status=status.HTTP_400_BAD_REQUEST
            )
