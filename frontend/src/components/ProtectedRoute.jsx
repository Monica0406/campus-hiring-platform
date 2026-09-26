import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, role, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner message="Checking authentication..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles) {
    const userRole = (role || '').toUpperCase();
    const normalizedAllowed = allowedRoles.map((r) => (r || '').toUpperCase());
    if (!normalizedAllowed.includes(userRole)) {
      if (userRole === 'STUDENT') {
        return <Navigate to="/student/dashboard" replace />;
      } else if (userRole === 'COMPANY') {
        return <Navigate to="/company/dashboard" replace />;
      }
      return <Navigate to="/" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
