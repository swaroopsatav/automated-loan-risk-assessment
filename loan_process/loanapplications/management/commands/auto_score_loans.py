from django.core.management.base import BaseCommand
from loanapplications.models import LoanApplication
from integrations.models import MockExperianReport
from loanapplications.ml.scoring import score_loan_application
from django.db import transaction


class Command(BaseCommand):
    help = "Score all unscored loan applications using AI model"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the scoring process without saving changes to the database.'
        )

    def handle(self, *args, **kwargs):
        dry_run = kwargs.get('dry_run', False)

        # Use transaction to ensure data consistency
        with transaction.atomic():
            loans = LoanApplication.objects.select_for_update().filter(
                ai_decision__isnull=True,
                status__in=["pending", "under_review"]
            ).select_related('user', 'credit_scoring_record')

            if not loans.exists():
                self.stdout.write("✅ No unscored loans.\n")
                return

            updated = 0
            errors = 0

            for loan in loans:
                try:
                    # Validate required data exists
                    if not loan.credit_scoring_record or not loan.user:
                        raise ValueError("Missing required credit scoring data or user")

                    report = loan.credit_scoring_record
                    user = loan.user

                    # Prepare features with validation
                    features = {
                        'credit_score': max(0, user.credit_score or 0),
                        'credit_util_pct': max(0, min(100, report.credit_utilization_pct or 0)),
                        'dpd_max': max(0, report.dpd_max or 0),
                        'emi_to_income_ratio': max(0, report.emi_to_income_ratio or 0),
                        'monthly_income': max(0, loan.monthly_income or 0),
                        'existing_loans': max(0, int(loan.existing_loans or 0)),
                    }

                    # Perform scoring within try block
                    risk_score, decision, explanation = score_loan_application(features)

                    # Validate scoring results
                    if not all(v is not None for v in [risk_score, decision, explanation]):
                        raise ValueError("Invalid scoring results")

                    # Update loan object
                    loan.risk_score = risk_score
                    loan.ai_decision = decision
                    loan.ml_scoring_output = explanation
                    loan.status = "approved" if decision == "approve" else "rejected"

                    if not dry_run:
                        loan.save(update_fields=['risk_score', 'ai_decision',
                                                 'ml_scoring_output', 'status'])
                    updated += 1

                    self.stdout.write(
                        f"Loan #{loan.id} scored: risk_score={risk_score}, ai_decision={decision}\n"
                    )

                except Exception as e:
                    self.stdout.write(
                        f"⚠️ Loan #{loan.id} failed: {str(e)}\n"
                    )
                    errors += 1

            # Summary with proper styling
            summary = f"✅ Scored {updated} loans"
            if dry_run:
                self.stdout.write(
                    f"✅ Scored {updated} loans (dry run, no changes saved).\n"
                )
            else:
                self.stdout.write(f"{summary}.\n")

            if errors > 0:
                self.stdout.write(
                    f"⚠️ {errors} loan(s) failed to score.\n"
                )
