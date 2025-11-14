import React, { useState } from "react";
import { View, Text, Alert, TextInput } from "react-native";
import { useCoupon } from "../context/CouponContext";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { CouponView } from "./components/CouponView";
import { PrimaryButton } from "./components/PrimaryButton";

export default function CouponScreen() {
  const { selections, removeSelection, clear, totalOdds } = useCoupon();
  const { token } = useAuth();
  const [name, setName] = useState("My Coupon");
  const [sending, setSending] = useState(false);

  const sendCoupon = async () => {
    if (!token) {
      Alert.alert("Login required", "You need to login to save coupons.");
      return;
    }
    if (!selections.length) {
      Alert.alert("Empty", "Add selections first.");
      return;
    }
    setSending(true);
    try {
      const res = await api.post("/coupon/create", {
        token,
        name,
        selections
      });
      Alert.alert(
        "Coupon saved",
        `ID: ${res.data.id}\nEV: ${res.data.total_ev.toFixed(2)}`
      );
      clear();
    } catch (err) {
      console.log(err);
      Alert.alert("Error", "Failed to save coupon.");
    } finally {
      setSending(false);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#000", padding: 8 }}>
      <Text
        style={{
          color: "#0f0",
          fontSize: 18,
          marginBottom: 8
        }}
      >
        Current Coupon
      </Text>

      <Text style={{ color: "#fff", marginBottom: 4 }}>Coupon name</Text>
      <TextInput
        style={{
          backgroundColor: "#111",
          color: "#fff",
          borderWidth: 1,
          borderColor: "#333",
          paddingHorizontal: 8,
          paddingVertical: 6,
          borderRadius: 4,
          marginBottom: 10
        }}
        value={name}
        onChangeText={setName}
      />

      <CouponView
        selections={selections}
        totalOdds={totalOdds}
        onRemove={removeSelection}
        footer={
          <PrimaryButton
            label={sending ? "Saving..." : "Save coupon to backend"}
            onPress={sendCoupon}
            loading={sending}
          />
        }
      />
    </View>
  );
}
