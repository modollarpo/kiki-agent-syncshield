import React, { createContext, useContext, useState, useEffect } from 'react';

import { User, UserRole } from '../types/roles';
import { fetchCurrentUser, login as apiLogin, logout as apiLogout } from '../utils/api';

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
  hasRole: (role: UserRole | UserRole[]) => boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}


const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentUser().then((apiUser) => {
      if (apiUser) {
        setUser({
          id: apiUser.id,
          name: apiUser.name,
          email: apiUser.email,
          role: apiUser.role as UserRole,
          avatarUrl: apiUser.avatarUrl,
        });
      } else {
        setUser(null);
      }
      setLoading(false);
    });
  }, []);

  const hasRole = (role: UserRole | UserRole[]) => {
    if (!user) return false;
    if (Array.isArray(role)) return role.includes(user.role);
    return user.role === role;
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    await apiLogin(email, password);
    const apiUser = await fetchCurrentUser();
    if (apiUser) {
      setUser({
        id: apiUser.id,
        name: apiUser.name,
        email: apiUser.email,
        role: apiUser.role as UserRole,
        avatarUrl: apiUser.avatarUrl,
      });
    } else {
      setUser(null);
    }
    setLoading(false);
  };

  const logout = async () => {
    setLoading(true);
    await apiLogout();
    setUser(null);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, isAuthenticated: !!user, hasRole, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
