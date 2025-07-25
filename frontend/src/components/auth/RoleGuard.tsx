'use client';

import React from 'react';
import { useAuth, useRole } from '@/hooks/useAuth';
import { hasMinimumRole, hasAnyRole, hasPermission, type UserRole } from '@/lib/auth-utils';

interface RoleGuardProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  requiredRoles?: UserRole[];
  requiredPermission?: string;
  fallback?: React.ReactNode;
  loading?: React.ReactNode;
}

/**
 * Component that conditionally renders content based on user role/permissions
 */
export default function RoleGuard({
  children,
  requiredRole,
  requiredRoles,
  requiredPermission,
  fallback = null,
  loading = null
}: RoleGuardProps) {
  const { isLoading, isAuthenticated, role } = useAuth();

  // Show loading state
  if (isLoading) {
    return <>{loading}</> || null;
  }

  // User must be authenticated
  if (!isAuthenticated) {
    return <>{fallback}</>;
  }

  // Check required role (minimum level)
  if (requiredRole && !hasMinimumRole(role, requiredRole)) {
    return <>{fallback}</>;
  }

  // Check if user has any of the required roles
  if (requiredRoles && !hasAnyRole(role, requiredRoles)) {
    return <>{fallback}</>;
  }

  // Check specific permission
  if (requiredPermission && !hasPermission(role, requiredPermission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

/**
 * Higher-order component for role-based access control
 */
export function withRoleGuard<P extends object>(
  Component: React.ComponentType<P>,
  options: Omit<RoleGuardProps, 'children'>
) {
  return function RoleGuardedComponent(props: P) {
    return (
      <RoleGuard {...options}>
        <Component {...props} />
      </RoleGuard>
    );
  };
}

/**
 * Utility components for common role checks
 */
export const AdminOnly = ({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) => (
  <RoleGuard requiredRole="ADMIN" fallback={fallback}>
    {children}
  </RoleGuard>
);

export const ManagerOrAdmin = ({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) => (
  <RoleGuard requiredRole="MANAGER" fallback={fallback}>
    {children}
  </RoleGuard>
);

export const SupervisorPlus = ({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) => (
  <RoleGuard requiredRole="SUPERVISOR" fallback={fallback}>
    {children}
  </RoleGuard>
);

export const TechnicianPlus = ({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) => (
  <RoleGuard requiredRole="TECHNICIAN" fallback={fallback}>
    {children}
  </RoleGuard>
);