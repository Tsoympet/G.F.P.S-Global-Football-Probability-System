import axios from "axios";
import Constants from "expo-constants";

const API_BASE =
  (Constants.expoConfig?.extra as any)?.API_BASE ||
  process.env.EXPO_PUBLIC_API_BASE ||
  "http://10.0.2.2:8000";

export const api = axios.create({
  baseURL: API_BASE.replace(/\/+$/, ""),
  timeout: 15000
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}
