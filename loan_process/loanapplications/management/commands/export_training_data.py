from django.core.management.base import BaseCommand
import csv
from datetime import date
from loanapplications.models import LoanApplication
from users.models import CustomUser
from django.db.models import Prefetch
from decimal import Decimal


class Command(BaseCommand):
    help = "Export enriched loan training data to CSV for ML model training"

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='loan_training_data.csv',
            help='Output file path for the CSV data (default: loan_training_data.csv)'
        )

    def handle(self, *args, **options):
        output_file = options['output']

        try:
            with open(output_file, "w", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write the CSV header
                writer.writerow([
                    'credit_score', 'annual_income', 'monthly_income', 'employment_status',
                    'existing_loans', 'credit_history_fetched',
                    'amount_requested', 'term_months', 'loan_to_income_ratio',
                    'credit_util_pct', 'emi_to_income_ratio', 'dpd_max',
                    'overdue_accounts', 'total_accounts', 'bureau_score', 'score_band',
                    'is_kyc_verified', 'govt_id_type', 'age', 'address_length',
                    'loan_approved'
                ])

                count = 0

                # Optimize query with select_related and prefetch_related
                loans = LoanApplication.objects.select_related('user').prefetch_related(
                    Prefetch('mock_experian')
                ).all()

                if not loans.exists():
                    self.stdout.write("No loan records found\n")
                    return

                for loan in loans:
                    try:
                        user = loan.user
                        if not user:
                            raise ValueError("No user associated with loan")

                        report = loan.mock_experian
                        if not report:
                            raise ValueError("No credit report found")

                        # Derived features with safe type conversion
                        try:
                            annual_income = float(user.annual_income or 0)
                            monthly_income = float(loan.monthly_income or 0)
                            amount_requested = float(loan.amount_requested or 0)
                        except (TypeError, ValueError):
                            annual_income = monthly_income = amount_requested = 0

                        loan_to_income = round(amount_requested / annual_income, 2) if annual_income > 0 else 0

                        age = 0
                        if user.date_of_birth:
                            today = date.today()
                            age = today.year - user.date_of_birth.year
                            # Adjust age if birthday hasn't occurred this year
                            if today.month < user.date_of_birth.month or (
                                    today.month == user.date_of_birth.month and today.day < user.date_of_birth.day):
                                age -= 1

                        address_len = len(str(user.address).strip()) if user.address else 0
                        loan_approved = 1 if loan.status and loan.status.strip().lower() == "approved" else 0

                        # Write the row with safe defaults
                        writer.writerow([
                            int(user.credit_score or 0),
                            annual_income,
                            monthly_income,
                            str(user.employment_status or 'unknown').lower(),
                            int(loan.existing_loans or 0),
                            int(bool(user.credit_history_fetched)),
                            amount_requested,
                            int(loan.term_months or 0),
                            loan_to_income,
                            float(report.credit_utilization_pct or 0),
                            float(report.emi_to_income_ratio or 0),
                            int(report.dpd_max or 0),
                            int(report.overdue_accounts or 0),
                            int(report.total_accounts or 0),
                            int(report.bureau_score or 0),
                            str(report.score_band or 'unknown').lower(),
                            int(bool(user.is_kyc_verified)),
                            str(user.govt_id_type or 'unknown').lower(),
                            age,
                            address_len,
                            loan_approved
                        ])
                        count += 1

                        if count % 100 == 0:
                            self.stdout.write(f"✅ Processed {count} records...\n")

                    except Exception as e:
                        self.stdout.write(f"⚠️ Skipped loan #{loan.id} due to: {str(e)}\n")
                        continue

                self.stdout.write(f"✅ Exported {count} records to {output_file}\n")

        except IOError as e:
            self.stdout.write(f"Failed to write to file {output_file}: {str(e)}\n")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {str(e)}"))
