import React from "react";
import { View, Text } from "react-native";

export default function LiveScreen() {
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
        Live streamer view (odds, alerts, events) will be added here.
      </Text>
    </View>
  );
}
