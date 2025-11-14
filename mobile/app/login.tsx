import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  Alert
} from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { registerForPushNotificationsAsync } from "../notifications/registerPush";

import * as Google from "expo-auth-session/providers/google";
import * as WebBrowser from "expo-web-browser";

WebBrowser.maybeCompleteAuthSession();

export default function LoginScreen() {
  const router = useRouter();
  const { setAuth, token } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState(""); // 2FA code
  const [loading, setLoading] = useState(false);

  const [request, response, promptAsync] = Google.useAuthRequest({
    androidClientId: process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID,
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID,
    expoClientId: process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID
  });

  useEffect(() => {
    if (response?.type === "success") {
      const idToken = response.authentication?.idToken;
      if (idToken) {
        handleGoogleIdToken(idToken);
      }
    }
  }, [response]);

  useEffect(() => {
    if (token) {
      router.replace("/");
    }
  }, [token]);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const res = await api.post("/auth/login", {
        email,
        password,
        code: code || undefined
      });
      const { token: jwt, profile } = res.data;
      await setAuth(jwt, profile);
      await registerForPushNotificationsAsync(jwt);
      router.replace("/");
    } catch (err: any) {
      console.log(err?.response?.data || err.message);
      Alert.alert("Login failed", "Check your credentials / 2FA code.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleIdToken = async (idToken: string) => {
    setLoading(true);
    try {
      const res = await api.post("/auth/google", {
        id_token: idToken
      });
      const { token: jwt, profile } = res.data;
      await setAuth(jwt, profile);
      await registerForPushNotificationsAsync(jwt);
      router.replace("/");
    } catch (err: any) {
      console.log(err?.response?.data || err.message);
      Alert.alert("Google login failed", "Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>GFPS Login</Text>

      <Text style={styles.label}>Email</Text>
      <TextInput
        style={styles.input}
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />

      <Text style={styles.label}>Password</Text>
      <TextInput
        style={styles.input}
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      <Text style={styles.label}>2FA Code (if enabled)</Text>
      <TextInput
        style={styles.input}
        keyboardType="number-pad"
        value={code}
        onChangeText={setCode}
        placeholder="123456"
      />

      <Button title={loading ? "..." : "Login"} onPress={handleLogin} />

      <View style={{ height: 16 }} />

      <Button
        title="Login with Google"
        disabled={!request}
        onPress={() => {
          promptAsync();
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
    padding: 16,
    justifyContent: "center"
  },
  title: {
    color: "#0f0",
    fontSize: 24,
    marginBottom: 24,
    textAlign: "center"
  },
  label: {
    color: "#fff",
    marginBottom: 4
  },
  input: {
    backgroundColor: "#111",
    borderWidth: 1,
    borderColor: "#333",
    padding: 8,
    borderRadius: 4,
    color: "#fff",
    marginBottom: 12
  }
});
