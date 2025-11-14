import React, { createContext, useContext, useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, setAuthToken } from "../lib/api";

export type UserProfile = {
  email: string;
  display_name?: string;
  avatar_url?: string;
  role?: string;
};

type AuthContextType = {
  token: string | null;
  profile: UserProfile | null;
  loading: boolean;
  setAuth: (token: string, profile: UserProfile) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [token, setToken] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const storedToken = await AsyncStorage.getItem("gfps_token");
        const storedProfile = await AsyncStorage.getItem("gfps_profile");
        if (storedToken && storedProfile) {
          setToken(storedToken);
          setProfile(JSON.parse(storedProfile));
          setAuthToken(storedToken);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const setAuth = async (t: string, p: UserProfile) => {
    setToken(t);
    setProfile(p);
    setAuthToken(t);
    await AsyncStorage.setItem("gfps_token", t);
    await AsyncStorage.setItem("gfps_profile", JSON.stringify(p));
  };

  const logout = async () => {
    setToken(null);
    setProfile(null);
    setAuthToken(null);
    await AsyncStorage.removeItem("gfps_token");
    await AsyncStorage.removeItem("gfps_profile");
  };

  return (
    <AuthContext.Provider value={{ token, profile, loading, setAuth, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
