import React, { createContext, useContext, useState } from "react";

// إنشاء Context
const AuthContext = createContext(null);

// Hook لاستخدام Context بسهولة
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

// Provider
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Mock login function
  const login = async (email, _password) => {
    // محاكاة call للـ backend
    await new Promise((r) => setTimeout(r, 800));

    setUser({
      user_image: "",          // default empty
      email,                   // mandatory
      first_name: email.split("@")[0].replace(/[._]/g, " "), // from email
      middle_name: "",
      last_name: "",
      username: "",
      phone: "",
      birth_date: "",
      gender: "",
      default_app: "",
      company: "Acme Corp",
      role: "Developer",
    });
  };

  // Logout
  const logout = () => setUser(null);

  // Update user profile
  const updateProfile = (data) => {
    setUser((prev) => (prev ? { ...prev, ...data } : null));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};