import React from "react";
import { Stack } from "expo-router";
import { AuthProvider, useAuth } from "../auth/AuthContext";
import { CouponProvider } from "../context/CouponContext";
import { ActivityIndicator, View } from "react-native";

const Loader = () => (
  <View
    style={{
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "#000"
    }}
  >
    <ActivityIndicator size="large" />
  </View>
);

const RootLayoutInner = () => {
  const { loading } = useAuth();

  if (loading) return <Loader />;

  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: "#000" },
        headerTintColor: "#fff",
        headerTitleStyle: { fontWeight: "bold" }
      }}
    >
      <Stack.Screen name="index" options={{ title: "GFPS Dashboard" }} />
      <Stack.Screen name="login" options={{ title: "Login" }} />
      <Stack.Screen name="fixtures" options={{ title: "Fixtures" }} />
      <Stack.Screen name="match" options={{ title: "Match & Markets" }} />
      <Stack.Screen name="coupon" options={{ title: "Coupon" }} />
      <Stack.Screen name="coupon-history" options={{ title: "Coupon History" }} />
      <Stack.Screen name="favorites" options={{ title: "Favorites" }} />
      <Stack.Screen name="profile" options={{ title: "Profile" }} />
      <Stack.Screen name="community" options={{ title: "Community" }} />
      <Stack.Screen name="live" options={{ title: "Live" }} />
      <Stack.Screen name="settings" options={{ title: "Settings" }} />
      <Stack.Screen name="alerts" options={{ title: "Alert Rules" }} />
    </Stack>
  );
};

export default function RootLayout() {
  return (
    <AuthProvider>
      <CouponProvider>
        <RootLayoutInner />
      </CouponProvider>
    </AuthProvider>
  );
}
