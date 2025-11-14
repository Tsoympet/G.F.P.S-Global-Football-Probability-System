import React from "react";
import { View, Text } from "react-native";

export default function CommunityScreen() {
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
        Community & chat will be implemented here (WebSocket /ws/chat).
      </Text>
    </View>
  );
}
