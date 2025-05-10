from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from loan_process.throttling import SensitiveEndpointThrottle
from .models import LoanApplication, LoanDocument
from .serializers import (
    LoanApplicationSerializer,
    LoanApplicationDetailSerializer,
    LoanDocumentSerializer,
    AdminLoanApplicationSerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from creditscorings.utils import score_and_record
from loanapplications.ml.scoring import score_loan_application
from .utils.email_utils import (
    send_loan_application_submitted_email,
    send_loan_status_update_email,
    send_document_uploaded_email,
)
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger('loanapplications.views')


# --- User: Submit New Loan Application ---
class LoanApplicationCreateView(generics.CreateAPIView):
    """
    Allows an authenticated user to submit a new loan application. 
    Runs AI scoring and records the results.
    """
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveEndpointThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                loan = serializer.save(user=self.request.user)
                try:
                    self.process_loan(loan)

                    # Send email notification
                    async_to_sync(send_loan_application_submitted_email)(loan)

                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                except Exception as e:
                    logger.error(f"Error processing loan application: {str(e)}")
                    return Response({'error': 'Failed to process loan application'},
                                    status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating loan application: {str(e)}")
                return Response({'error': 'Failed to create loan application'},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_loan(self, loan):
        try:
            # Scoring is now automatically triggered in the LoanApplication.save() method
            # We just need to send the status update email
            async_to_sync(send_loan_status_update_email)(loan)
        except Exception as e:
            logger.error(f"Error processing loan application: {str(e)}")
            raise


# --- User: List All Their Applications ---
class UserLoanListView(generics.ListAPIView):
    """
    Lists all loan applications submitted by the authenticated user.
    """
    serializer_class = LoanApplicationDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (LoanApplication.objects
                .filter(user=self.request.user)
                .select_related('user')
                .prefetch_related('documents')
                .order_by('-submitted_at'))


# --- User: View Single Application ---  
class UserLoanDetailView(generics.RetrieveAPIView):
    """
    Retrieves details of a single loan application for the authenticated user.
    """
    serializer_class = LoanApplicationDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (LoanApplication.objects
                .filter(user=self.request.user)
                .select_related('user')
                .prefetch_related('documents'))


# --- Upload Loan Document ---
class LoanDocumentUploadView(generics.CreateAPIView):
    """
    Allows an authenticated user to upload documents related to their loan application.
    """
    serializer_class = LoanDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [SensitiveEndpointThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Verify loan belongs to user
                loan = LoanApplication.objects.get(
                    id=serializer.validated_data['loan'].id,
                    user=self.request.user
                )
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except LoanApplication.DoesNotExist:
                return Response({"detail": "Not authorized to upload documents for this loan"},
                                status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                logger.error(f"Error uploading loan document: {str(e)}")
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        loan_document = serializer.save()

        # Send email notification
        async_to_sync(send_document_uploaded_email)(loan_document)


# --- Admin: View All Applications ---
class AdminLoanListView(generics.ListAPIView):
    """
    Lists all loan applications for admin users.
    """
    serializer_class = AdminLoanApplicationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = (LoanApplication.objects
                    .select_related('user')
                    .prefetch_related('documents')
                    .order_by('-submitted_at'))

        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


# --- Admin: View Single Application with ML Scoring ---
class AdminLoanDetailView(generics.RetrieveAPIView):
    """
    Retrieves details of a single loan application, including ML scoring data, for admin users.
    """
    serializer_class = AdminLoanApplicationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return (LoanApplication.objects
                .select_related('user')
                .prefetch_related('documents'))
