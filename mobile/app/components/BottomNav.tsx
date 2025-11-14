import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useRouter, usePathname } from "expo-router";

type Item = {
  label: string;
  route: string;
};

const NAV_ITEMS: Item[] = [
  { label: "Home", route: "/" },
  { label: "Fixtures", route: "/fixtures" },
  { label: "Coupon", route: "/coupon" },
  { label: "Live", route: "/live" },
  { label: "Profile", route: "/profile" }
];

export const BottomNav: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <View style={styles.container}>
      {NAV_ITEMS.map(item => {
        const active = pathname === item.route;
        return (
          <TouchableOpacity
            key={item.route}
            style={styles.item}
            onPress={() => router.push(item.route as any)}
          >
            <Text style={[styles.label, active && styles.labelActive]}>
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    backgroundColor: "#050505",
    borderTopWidth: 1,
    borderTopColor: "#222",
    paddingVertical: 6
  },
  item: {
    flex: 1,
    alignItems: "center"
  },
  label: {
    color: "#777",
    fontSize: 12
  },
  labelActive: {
    color: "#0f0",
    fontWeight: "700"
  }
});
