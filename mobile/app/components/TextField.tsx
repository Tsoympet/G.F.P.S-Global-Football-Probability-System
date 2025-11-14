import React from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TextInputProps
} from "react-native";

type Props = TextInputProps & {
  label?: string;
  error?: string;
};

export const TextField: React.FC<Props> = ({ label, error, ...rest }) => {
  return (
    <View style={{ marginBottom: 10 }}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <TextInput
        style={[styles.input, error && styles.inputError]}
        placeholderTextColor="#666"
        {...rest}
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
};

const styles = StyleSheet.create({
  label: {
    color: "#fff",
    marginBottom: 4
  },
  input: {
    backgroundColor: "#111",
    borderWidth: 1,
    borderColor: "#333",
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 4,
    color: "#fff"
  },
  inputError: {
    borderColor: "#f55"
  },
  error: {
    color: "#f55",
    marginTop: 2,
    fontSize: 12
  }
});
