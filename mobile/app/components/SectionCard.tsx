import React from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";

type Props = {
  title?: string;
  children: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
};

export const SectionCard: React.FC<Props> = ({ title, children, style }) => {
  return (
    <View style={[styles.card, style]}>
      {title ? <Text style={styles.title}>{title}</Text> : null}
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#111",
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#222"
  },
  title: {
    color: "#0f0",
    fontWeight: "700",
    marginBottom: 6
  }
});
