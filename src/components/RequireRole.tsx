import React from 'react';
import { useAuth } from '../context/AuthContext';
import PageState from './PageState';
import { UserRole } from '../types/roles';

interface RequireRoleProps {
  role: UserRole | UserRole[];
  children: React.ReactNode;
}

const RequireRole: React.FC<RequireRoleProps> = ({ role, children }) => {
  const { isAuthenticated, hasRole } = useAuth();

  if (!isAuthenticated) {
    return <PageState isError errorMessage="You must be logged in to access this page." />;
  }
  if (!hasRole(role)) {
    return <PageState isError errorMessage="You do not have permission to view this page." />;
  }
  return <>{children}</>;
};

export default RequireRole;
