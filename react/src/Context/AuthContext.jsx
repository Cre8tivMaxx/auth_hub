import React, { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = async (email, _password) => {
    await new Promise((r) => setTimeout(r, 800));

    setUser({
      user_image: "",          
      email,                  
      first_name: email.split("@")[0].replace(/[._]/g, " "), 
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

  const logout = () => setUser(null);

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