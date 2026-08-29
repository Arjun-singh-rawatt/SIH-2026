import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockUsers, currentUserDefault } from '../data/mockUsers';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('sift_current_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return currentUserDefault;
      }
    }
    return currentUserDefault;
  });

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('sift_auth_token') !== 'logged_out';
  });

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('sift_current_user', JSON.stringify(currentUser));
    }
  }, [currentUser]);

  const login = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
    localStorage.setItem('sift_auth_token', 'valid_token');
    localStorage.setItem('sift_current_user', JSON.stringify(user));
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.setItem('sift_auth_token', 'logged_out');
  };

  const switchUser = (userId) => {
    const found = mockUsers.find((u) => u.userId === userId);
    if (found) {
      login(found);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated,
        login,
        logout,
        switchUser,
        availableUsers: mockUsers,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
