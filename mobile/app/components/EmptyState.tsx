import React from "react";
import { View, Text, StyleSheet } from "react-native";

type Props = {
  message: string;
};

export const EmptyState: React.FC<Props> = ({ message }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{message}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 24,
    alignItems: "center",
    justifyContent: "center"
  },
  text: {
    color: "#666",
    fontSize: 14,
    textAlign: "center"
  }
});
