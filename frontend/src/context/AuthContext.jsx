import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient, { getErrorMessage } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(localStorage.getItem('user_role') || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    setUser(null);
    setRole(null);
    setError(null);
  }, []);

  const loadCurrentUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await apiClient.get('/auth/me/');
      if (response.data?.success) {
        setUser(response.data.data);
        setRole(response.data.data.role);
        localStorage.setItem('user_role', response.data.data.role);
      } else {
        logout();
      }
    } catch (err) {
      console.warn('Failed to load current user, logging out', err);
      logout();
    } finally {
      setLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    loadCurrentUser();

    const handleLogoutEvent = () => {
      logout();
    };
    window.addEventListener('auth:logout', handleLogoutEvent);

    return () => {
      window.removeEventListener('auth:logout', handleLogoutEvent);
    };
  }, [loadCurrentUser, logout]);

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await apiClient.post('/auth/login/', { email, password });
      const { access, refresh, role: userRole, profile } = response.data.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', userRole);

      setRole(userRole);
      setUser({
        email,
        role: userRole,
        profile,
      });

      // Load full identity
      await loadCurrentUser();
      return { success: true, role: userRole };
    } catch (err) {
      const msg = getErrorMessage(err, 'Login failed. Please check your credentials.');
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const registerStudent = async (studentData) => {
    setError(null);
    try {
      const response = await apiClient.post('/auth/register/student/', studentData);
      const { access, refresh, role: userRole, student } = response.data.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', userRole);

      setRole(userRole);
      setUser({
        email: studentData.email,
        role: userRole,
        profile: student,
      });

      await loadCurrentUser();
      return { success: true };
    } catch (err) {
      const msg = getErrorMessage(err, 'Student registration failed.');
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const registerCompany = async (companyData) => {
    setError(null);
    try {
      const response = await apiClient.post('/auth/register/company/', companyData);
      const { access, refresh, role: userRole, company } = response.data.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', userRole);

      setRole(userRole);
      setUser({
        email: companyData.email,
        role: userRole,
        profile: company,
      });

      await loadCurrentUser();
      return { success: true };
    } catch (err) {
      const msg = getErrorMessage(err, 'Company registration failed.');
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const updateUserProfile = (updatedProfile) => {
    setUser((prev) => (prev ? { ...prev, profile: { ...prev.profile, ...updatedProfile } } : prev));
  };

  const value = {
    user,
    role,
    isAuthenticated: Boolean(user && localStorage.getItem('access_token')),
    loading,
    error,
    login,
    logout,
    registerStudent,
    registerCompany,
    updateUserProfile,
    reloadUser: loadCurrentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
