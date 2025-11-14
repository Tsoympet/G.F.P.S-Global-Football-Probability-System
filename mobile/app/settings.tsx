import React from "react";
import { View, Text } from "react-native";

export default function SettingsScreen() {
  return (
    <View
      style={{
        flex: 1,
        backgroundColor: "#000",
        alignItems: "center",
        justifyContent: "center"
      }}
    >
      <Text style={{ color: "#fff" }}>
        Settings screen (alert rules, notifications, etc.) will go here.
      </Text>
    </View>
  );
}
