import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Importing user-related components
import RegisterForm from './users/RegisterForm';
import LoginForm from './users/LoginForm';
import ForgotPassword from './users/ForgotPassword';
import ResetPassword from './users/ResetPassword';
import Profile from './users/Profile';
import ProfileEditForm from './users/ProfileEditForm';
import Home from './users/Home';
import Navbar from './users/Navbar';
import PrivateRoute from './users/PrivateRoute';
import OAuthCallback from './users/OAuthCallback';

// Importing loan-related components
import LoanSubmitForm from './loans/LoanSubmitForm';
import MyLoanList from './loans/MyLoanList';
import LoanDetail from './loans/LoanDetail';
import LoanDocumentUpload from './loans/LoanDocumentUpload';

// Importing credit-related components
import ScoreViewer from './credit/ScoreViewer';
import RescoreButton from './credit/RescoreButton';
import AdminScoreList from './credit/AdminScoreList';
import AdminScoreDetail from './credit/AdminScoreDetail';

// Importing risk dashboard components
import RiskSnapshotList from './risk_dashboard/RiskSnapshotList';
import RiskTrendChart from './risk_dashboard/RiskTrendChart';
import ModelPerformanceLog from './risk_dashboard/ModelPerformanceLog';

// Importing compliance components
import LoanComplianceChecks from './compliance/LoanComplianceChecks';
import ComplianceCheckUpdate from './compliance/ComplianceCheckUpdate';
import ComplianceAuditTrail from './compliance/ComplianceAuditTrail';

// Importing integration components
import MockKYCViewer from './integrations/MockKYCViewer';
import MockExperianViewer from './integrations/MockExperianViewer';
import AdminMockExperianList from './integrations/AdminMockExperianList';

const App = () => {
  return (
    <Router>
      {/* Navbar is always visible */}
      <Navbar />

      {/* Main content section */}
      <div className="min-h-screen bg-gray-100 p-4">
        <Routes>
          {/* Home route - shows dashboard for authenticated users */}
          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />

          {/* User routes */}
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/auth/:provider/callback" element={<OAuthCallback />} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/profile/edit" element={<PrivateRoute><ProfileEditForm /></PrivateRoute>} />

          {/* Loan routes */}
          <Route path="/loans/apply" element={<PrivateRoute><LoanSubmitForm /></PrivateRoute>} />
          <Route path="/loans" element={<PrivateRoute><MyLoanList /></PrivateRoute>} />
          <Route path="/loans/:id" element={<PrivateRoute><LoanDetail /></PrivateRoute>} />
          <Route path="/document/upload" element={<PrivateRoute><LoanDocumentUpload /></PrivateRoute>} />

          {/* Credit routes */}
          <Route path="/score/loan/:loan_id" element={<PrivateRoute><ScoreViewer /></PrivateRoute>} />
          <Route path="/rescore" element={<PrivateRoute><RescoreButton /></PrivateRoute>} />
          <Route path="/admin/scores" element={<PrivateRoute><AdminScoreList /></PrivateRoute>} />
          <Route path="/admin/scores/:id" element={<PrivateRoute><AdminScoreDetail /></PrivateRoute>} />

          {/* Risk dashboard routes */}
          <Route path="/risk/snapshots" element={<PrivateRoute><RiskSnapshotList /></PrivateRoute>} />
          <Route path="/risk/trends" element={<PrivateRoute><RiskTrendChart /></PrivateRoute>} />
          <Route path="/risk/models" element={<PrivateRoute><ModelPerformanceLog /></PrivateRoute>} />

          {/* Compliance routes */}
          <Route path="/compliance/loan/:loanId" element={<PrivateRoute><LoanComplianceChecks /></PrivateRoute>} />
          <Route path="/compliance/check/:id/edit" element={<PrivateRoute><ComplianceCheckUpdate /></PrivateRoute>} />
          <Route path="/compliance/audit-trail" element={<PrivateRoute><ComplianceAuditTrail /></PrivateRoute>} />

          {/* Integration routes */}
          <Route path="/mock/kyc" element={<PrivateRoute><MockKYCViewer /></PrivateRoute>} />
          <Route path="/mock/experian/:loanId" element={<PrivateRoute><MockExperianViewer /></PrivateRoute>} />
          <Route path="/mock/experian/all" element={<PrivateRoute><AdminMockExperianList /></PrivateRoute>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
