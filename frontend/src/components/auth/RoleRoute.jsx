import React from 'react';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AccessDenied from './AccessDenied';

export default function RoleRoute({ allowedRoles = [], children }) {
  const { hasRole, role } = useAuth();

  if (!hasRole(...allowedRoles)) {
    return <AccessDenied message={`Access to this operational area requires one of: ${allowedRoles.join(', ')}. Your current role is ${role}.`} />;
  }

  return children ? children : <Outlet />;
}
