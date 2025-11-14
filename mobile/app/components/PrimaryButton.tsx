import React from "react";
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  GestureResponderEvent,
  ActivityIndicator,
  ViewStyle
} from "react-native";

type Props = {
  label: string;
  onPress: (e: GestureResponderEvent) => void;
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle | ViewStyle[];
};

export const PrimaryButton: React.FC<Props> = ({
  label,
  onPress,
  disabled,
  loading,
  style
}) => {
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      style={[styles.btn, isDisabled && styles.btnDisabled, style]}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color="#000" />
      ) : (
        <Text style={styles.label}>{label}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  btn: {
    backgroundColor: "#00ff88",
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignItems: "center",
    justifyContent: "center"
  },
  btnDisabled: {
    opacity: 0.6
  },
  label: {
    color: "#000",
    fontWeight: "700",
    fontSize: 16
  }
});
