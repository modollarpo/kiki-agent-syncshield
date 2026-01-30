// src/types/roles.ts
export type UserRole =
  | 'admin'
  | 'owner'
  | 'manager'
  | 'member'
  | 'viewer';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarUrl?: string;
}
