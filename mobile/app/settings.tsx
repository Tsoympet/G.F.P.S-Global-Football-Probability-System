import React, { useState } from "react";
import { View, Text, Switch } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "../auth/AuthContext";
import { ScreenContainer } from "./components/ScreenContainer";
import { SectionCard } from "./components/SectionCard";
import { PrimaryButton } from "./components/PrimaryButton";

export default function SettingsScreen() {
  const { token, profile } = useAuth();
  const router = useRouter();

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  if (!token) {
    return (
      <ScreenContainer
        style={{
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <Text style={{ color: "#fff" }}>You need to login first.</Text>
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <SectionCard title="Account">
        <Text style={{ color: "#fff" }}>
          Email: {profile?.email ?? "unknown"}
        </Text>
        <Text style={{ color: "#fff" }}>
          Plan: {profile?.role ?? "free"}
        </Text>
      </SectionCard>

      <SectionCard title="Notifications">
        <View
          style={{
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <Text style={{ color: "#fff" }}>Push notifications</Text>
          <Switch
            value={notificationsEnabled}
            onValueChange={setNotificationsEnabled}
          />
        </View>
        <Text style={{ color: "#777", marginTop: 4, fontSize: 12 }}>
          (Uses your device push token registered with GFPS backend.)
        </Text>
      </SectionCard>

      <SectionCard title="Alerts">
        <Text style={{ color: "#fff", marginBottom: 8 }}>
          Configure value-based alert rules for live matches.
        </Text>
        <PrimaryButton
          label="Manage Alert Rules"
          onPress={() => router.push("/alerts")}
        />
      </SectionCard>
    </ScreenContainer>
  );
}
