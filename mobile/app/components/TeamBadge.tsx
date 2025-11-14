import React from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";

type Props = {
  name: string;
  size?: number;
  style?: ViewStyle | ViewStyle[];
};

export const TeamBadge: React.FC<Props> = ({ name, size = 32, style }) => {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map(w => w[0]?.toUpperCase())
    .join("");

  return (
    <View
      style={[
        styles.container,
        {
          width: size,
          height: size,
          borderRadius: size / 2
        },
        style
      ]}
    >
      <Text style={styles.text}>{initials || "?"}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#00ff88",
    alignItems: "center",
    justifyContent: "center"
  },
  text: {
    color: "#000",
    fontWeight: "700"
  }
});
