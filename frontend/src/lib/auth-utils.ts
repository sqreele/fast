import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import type { Session } from 'next-auth';

// Role hierarchy - higher numbers = more permissions
export const ROLE_HIERARCHY = {
  'USER': 1,
  'TECHNICIAN': 2,
  'SUPERVISOR': 3,
  'MANAGER': 4,
  'ADMIN': 5
} as const;

export type UserRole = keyof typeof ROLE_HIERARCHY;

/**
 * Check if a user has at least the required role level
 */
export function hasMinimumRole(userRole: string | undefined, requiredRole: UserRole): boolean {
  if (!userRole) return false;
  
  const userLevel = ROLE_HIERARCHY[userRole as UserRole];
  const requiredLevel = ROLE_HIERARCHY[requiredRole];
  
  return userLevel >= requiredLevel;
}

/**
 * Check if a user has the exact role
 */
export function hasExactRole(userRole: string | undefined, requiredRole: UserRole): boolean {
  return userRole === requiredRole;
}

/**
 * Check if a user has any of the specified roles
 */
export function hasAnyRole(userRole: string | undefined, roles: UserRole[]): boolean {
  if (!userRole) return false;
  return roles.includes(userRole as UserRole);
}

/**
 * Server-side authentication check
 * Use this in server components and API routes
 */
export async function requireAuth(requiredRole?: UserRole) {
  const session = await getServerSession();
  
  if (!session) {
    redirect('/api/auth/signin');
  }
  
  if (requiredRole && !hasMinimumRole(session.user?.role, requiredRole)) {
    redirect('/unauthorized');
  }
  
  return session;
}

/**
 * Get user permissions based on role
 */
export function getUserPermissions(role: string | undefined) {
  if (!role) return [];
  
  const permissions: string[] = [];
  
  // Base permissions for all authenticated users
  permissions.push('view_dashboard');
  
  // Role-specific permissions
  switch (role) {
    case 'ADMIN':
      permissions.push(
        'manage_users',
        'manage_properties',
        'manage_system',
        'view_all_data',
        'delete_any',
        'modify_any'
      );
      // Fall through to include all lower-level permissions
    case 'MANAGER':
      permissions.push(
        'manage_work_orders',
        'assign_tasks',
        'view_reports',
        'manage_schedules'
      );
      // Fall through
    case 'SUPERVISOR':
      permissions.push(
        'approve_work_orders',
        'manage_technicians',
        'view_team_performance'
      );
      // Fall through
    case 'TECHNICIAN':
      permissions.push(
        'create_work_orders',
        'update_maintenance_logs',
        'view_assigned_tasks',
        'upload_files'
      );
      // Fall through
    case 'USER':
      permissions.push(
        'view_own_data',
        'create_issues'
      );
      break;
  }
  
  return [...new Set(permissions)]; // Remove duplicates
}

/**
 * Check if user has a specific permission
 */
export function hasPermission(role: string | undefined, permission: string): boolean {
  const permissions = getUserPermissions(role);
  return permissions.includes(permission);
}

/**
 * Format user display name
 */
export function formatUserName(user: Session['user']): string {
  if (user?.name) return user.name;
  if (user?.email) return user.email.split('@')[0];
  return 'Unknown User';
}

/**
 * Get role display name
 */
export function getRoleDisplayName(role: string | undefined): string {
  if (!role) return 'No Role';
  
  const roleMap: Record<string, string> = {
    'ADMIN': 'Administrator',
    'MANAGER': 'Manager',
    'SUPERVISOR': 'Supervisor',
    'TECHNICIAN': 'Technician',
    'USER': 'User'
  };
  
  return roleMap[role] || role;
}

/**
 * Client-side role guard hook
 * Use this in client components to conditionally render content
 */
export function useRoleGuard() {
  return {
    hasMinimumRole,
    hasExactRole,
    hasAnyRole,
    hasPermission,
    getUserPermissions,
    formatUserName,
    getRoleDisplayName
  };
}