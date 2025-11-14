import React from "react";
import { View, ViewStyle, StatusBar } from "react-native";

type Props = {
  children: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
};

export const ScreenContainer: React.FC<Props> = ({ children, style }) => {
  return (
    <View
      style={[
        {
          flex: 1,
          backgroundColor: "#000",
          paddingHorizontal: 12,
          paddingVertical: 8
        },
        style
      ]}
    >
      <StatusBar barStyle="light-content" />
      {children}
    </View>
  );
};
