from django.core.management.base import BaseCommand
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging
from logging.handlers import RotatingFileHandler

import xgboost as xgb
import lightgbm as lgb

# Configure logging with rotation
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('ml_training.log', maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Command(BaseCommand):
    help = "Train loan eligibility models using XGBoost and LightGBM, and export as .pkl"

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='ml_models',
            help='Directory to save trained models (default: ml_models)'
        )
        parser.add_argument(
            '--input-file',
            type=str,
            default='loan_training_data.csv',
            help='Input CSV file path (default: loan_training_data.csv)'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('input_file', 'loan_training_data.csv')
        output_dir = kwargs.get('output_dir', 'ml_models')

        if not os.path.exists(file_path):
            msg = f"❌ CSV file not found at {file_path}. Run export_training_data first.\n"
            self.stdout.write(msg)
            logger.error(msg)
            return

        try:
            # Load and validate the dataset
            df = pd.read_csv(file_path)
            expected_columns = ['credit_score', 'annual_income', 'monthly_income', 'employment_status',
                                'existing_loans', 'credit_history_fetched', 'amount_requested', 'term_months',
                                'loan_to_income_ratio', 'credit_util_pct', 'emi_to_income_ratio', 'dpd_max',
                                'overdue_accounts', 'total_accounts', 'bureau_score', 'score_band',
                                'is_kyc_verified', 'govt_id_type', 'age', 'address_length', 'loan_approved']

            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                msg = f"❌ Missing columns in CSV file: {', '.join(missing_cols)}\n"
                self.stdout.write(msg)
                logger.error(msg)
                return

            # Handle missing values
            df = df.fillna(df.mean(numeric_only=True))

            # Convert categorical variables
            categorical_features = df.select_dtypes(include=['object']).columns
            df = pd.get_dummies(df, columns=[col for col in categorical_features if col != 'loan_approved'])

            X = df.drop(columns=['loan_approved'])
            y = df['loan_approved']

            # Standardize numerical features
            numerical_features = X.select_dtypes(include=['float64', 'int64']).columns
            scaler = StandardScaler()
            X[numerical_features] = scaler.fit_transform(X[numerical_features])

            # Save scaler for future predictions
            os.makedirs(output_dir, exist_ok=True)
            joblib.dump(scaler, os.path.join(output_dir, "feature_scaler.pkl"))

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )

            # Train XGBoost with better parameters 
            self.stdout.write("🚀 Training XGBoost model...")
            logger.info("Training XGBoost model...")
            xgb_model = xgb.XGBClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                min_child_weight=1,
                gamma=0,
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric='logloss',
                use_label_encoder=False,
                random_state=42
            )

            xgb_model.fit(
                X_train,
                y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=10,
                verbose=False
            )

            xgb_preds = xgb_model.predict(X_test)
            xgb_report = classification_report(y_test, xgb_preds)
            joblib.dump(xgb_model, os.path.join(output_dir, "xgboost_loan_model.pkl"))

            self.stdout.write(f"✅ XGBoost model saved to {output_dir}/xgboost_loan_model.pkl\n")
            self.stdout.write("📊 XGBoost Report:\n" + xgb_report)
            logger.info("XGBoost training complete. Report:\n" + xgb_report)

            # Train LightGBM with better parameters
            self.stdout.write("🚀 Training LightGBM model...")
            logger.info("Training LightGBM model...")
            lgb_model = lgb.LGBMClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                num_leaves=31,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )

            lgb_model.fit(
                X_train,
                y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=10,
                verbose=False
            )

            lgb_preds = lgb_model.predict(X_test)
            lgb_report = classification_report(y_test, lgb_preds)
            joblib.dump(lgb_model, os.path.join(output_dir, "lightgbm_loan_model.pkl"))

            self.stdout.write(f"✅ LightGBM model saved to {output_dir}/lightgbm_loan_model.pkl\n")
            self.stdout.write("📊 LightGBM Report:\n" + lgb_report)
            logger.info("LightGBM training complete. Report:\n" + lgb_report)

            # Save feature names for future reference
            joblib.dump(list(X.columns), os.path.join(output_dir, "feature_names.pkl"))

        except Exception as e:
            msg = f"❌ An error occurred: {str(e)}\n"
            self.stdout.write(msg)
            logger.error(msg, exc_info=True)
            raise
