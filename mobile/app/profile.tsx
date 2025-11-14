import React from "react";
import { View, Text, Button } from "react-native";
import { useAuth } from "../auth/AuthContext";

export default function ProfileScreen() {
  const { token, profile, logout } = useAuth();

  if (!token) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: "#000",
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <Text style={{ color: "#fff" }}>You are not logged in.</Text>
      </View>
    );
  }

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: "#000",
        padding: 16
      }}
    >
      <Text style={{ color: "#0f0", fontSize: 20, marginBottom: 12 }}>
        Profile
      </Text>
      <Text style={{ color: "#fff" }}>Email: {profile?.email}</Text>
      <Text style={{ color: "#fff" }}>
        Name: {profile?.display_name || "(none)"}
      </Text>
      <Text style={{ color: "#fff" }}>Role: {profile?.role || "free"}</Text>

      <View style={{ marginTop: 24 }}>
        <Button title="Logout" onPress={logout} />
      </View>
    </View>
  );
}
