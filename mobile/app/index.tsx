import React from "react";
import { View, Text, Button } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "../auth/AuthContext";

export default function IndexScreen() {
  const router = useRouter();
  const { token, profile } = useAuth();

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: "#000",
        padding: 16,
        justifyContent: "center"
      }}
    >
      <Text style={{ color: "#0f0", fontSize: 24, marginBottom: 16 }}>
        GFPS – Global Football Probability System
      </Text>

      {token ? (
        <>
          <Text style={{ color: "#fff", marginBottom: 8 }}>
            Logged in as: {profile?.display_name || profile?.email}
          </Text>
          <Button title="Fixtures" onPress={() => router.push("/fixtures")} />
          <View style={{ height: 8 }} />
          <Button title="Coupon" onPress={() => router.push("/coupon")} />
          <View style={{ height: 8 }} />
          <Button
            title="Coupon History"
            onPress={() => router.push("/coupon-history")}
          />
          <View style={{ height: 8 }} />
          <Button title="Favorites" onPress={() => router.push("/favorites")} />
          <View style={{ height: 8 }} />
          <Button title="Live" onPress={() => router.push("/live")} />
          <View style={{ height: 8 }} />
          <Button title="Community" onPress={() => router.push("/community")} />
          <View style={{ height: 8 }} />
          <Button title="Profile" onPress={() => router.push("/profile")} />
        </>
      ) : (
        <>
          <Text style={{ color: "#fff", marginBottom: 16 }}>
            Please login to use all GFPS features.
          </Text>
          <Button title="Login / Sign up" onPress={() => router.push("/login")} />
        </>
      )}
    </View>
  );
}
