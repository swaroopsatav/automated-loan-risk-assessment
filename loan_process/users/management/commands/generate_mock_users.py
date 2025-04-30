from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils.timezone import now
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)
faker = Faker()


class Command(BaseCommand):
    help = 'Generate mock users with financial and KYC details'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of users to generate')
        parser.add_argument('--batch-size', type=int, default=100, help='Number of users to create per batch')

    def handle(self, *args, **options):
        count = options['count']
        batch_size = options['batch_size']
        created = 0
        total_errors = 0

        while created < count:
            batch = []
            current_batch_size = min(batch_size, count - created)

            for _ in range(current_batch_size):
                try:
                    user_data = self._generate_user_data()
                    user = CustomUser(**user_data)
                    user.set_password(user_data['password'])
                    batch.append(user)
                except Exception as e:
                    logger.warning(f"Skipping user due to error: {str(e)}")
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipping user due to error: {str(e)}"))
                    total_errors += 1
                    continue

            if batch:
                try:
                    created_users = CustomUser.objects.bulk_create(batch, ignore_conflicts=True)
                    created += len(created_users)
                    logger.info(f"Created {len(created_users)} users in batch")
                    self.stdout.write(f"✅ {created}/{count} users created...")
                except Exception as e:
                    logger.error(f"Error during batch creation: {str(e)}")
                    self.stdout.write(self.style.ERROR(f"❌ Error during batch creation: {str(e)}"))
                    total_errors += len(batch)
                    # Break the loop if we encounter an exception during bulk_create
                    # This ensures we don't get stuck in an infinite loop if bulk_create always fails
                    break

        summary = f"\n✅ Process completed:\n"
        summary += f"- Successfully created: {created} users\n"
        summary += f"- Failed attempts: {total_errors}\n"
        logger.info(summary)
        self.stdout.write(self.style.SUCCESS(summary))

    def _generate_user_data(self):
        username = self.generate_unique_username()
        email = self.generate_unique_email()

        return {
            'username': username,
            'email': email,
            'password': 'testpass123',
            'phone_number': faker.numerify('##########'),
            'date_of_birth': faker.date_of_birth(minimum_age=21, maximum_age=60),
            'address': faker.address(),
            'annual_income': round(random.uniform(150000, 1500000), 2),
            'employment_status': random.choice(['salaried', 'self-employed', 'unemployed']),
            'credit_score': random.randint(300, 850),
            'credit_history_fetched': random.choice([True, False]),
            'is_kyc_verified': random.choice([True, False]),
            'kyc_verified_on': now() if random.choice([True, False]) else None,
            'govt_id_type': random.choice(['PAN', 'Aadhaar', 'Passport']),
            'govt_id_number': faker.bothify(text='?????#####'),
            'experian_customer_ref': f"EX-{random.randint(100000, 999999)}",
            'last_experian_sync': now() if random.choice([True, False]) else None,
            'experian_status': random.choice(['pending', 'success', 'failed'])
        }

    def generate_unique_username(self):
        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            username = faker.user_name()
            if not CustomUser.objects.filter(username=username).exists():
                return username
            attempts += 1
        raise Exception("Could not generate unique username after maximum attempts")

    def generate_unique_email(self):
        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            email = faker.email()
            if not CustomUser.objects.filter(email=email).exists():
                return email
            attempts += 1
        raise Exception("Could not generate unique email after maximum attempts")
