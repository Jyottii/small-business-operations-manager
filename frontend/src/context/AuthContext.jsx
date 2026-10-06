import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Authoritatively load current user from /api/v1/auth/me
  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (!token) {
      setCurrentUser(null);
      setLoading(false);
      return null;
    }

    try {
      const user = await apiClient('/auth/me');
      setCurrentUser(user);
      return user;
    } catch (err) {
      // 401 or network error - clear invalid session
      setCurrentUser(null);
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial session restoration on mount
  useEffect(() => {
    refreshUser();

    // Global listener for 401 Unauthorized events from apiClient
    const handleUnauthorized = () => {
      setCurrentUser(null);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [refreshUser]);

  // Login handler
  const login = async (email, password) => {
    const result = await apiClient('/auth/login', {
      method: 'POST',
      body: { email, password },
    });

    if (result?.access_token) {
      localStorage.setItem('token', result.access_token);
    }

    // Set user from response
    if (result?.user) {
      setCurrentUser(result.user);
      return result.user;
    }

    // Fallback: refresh from /me
    return await refreshUser();
  };

  // Register handler (creates business + owner)
  const register = async (userData) => {
    const result = await apiClient('/auth/register', {
      method: 'POST',
      body: userData,
    });

    if (result?.access_token) {
      localStorage.setItem('token', result.access_token);
    }

    if (result?.user) {
      setCurrentUser(result.user);
      return result.user;
    }

    return await refreshUser();
  };

  // Logout handler
  const logout = async () => {
    try {
      await apiClient('/auth/logout', { method: 'POST' });
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');
      setCurrentUser(null);
    }
  };

  // Role verification helper
  const hasRole = (...allowedRoles) => {
    if (!currentUser || !currentUser.role) return false;
    return allowedRoles.includes(currentUser.role);
  };

  const value = {
    currentUser,
    loading,
    isAuthenticated: !!currentUser,
    role: currentUser?.role || null,
    businessId: currentUser?.business_id || null,
    login,
    register,
    logout,
    refreshUser,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
