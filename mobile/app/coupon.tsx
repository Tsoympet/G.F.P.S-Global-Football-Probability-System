import React, { useState } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Button,
  Alert
} from "react-native";
import { useCoupon } from "../context/CouponContext";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";

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
      <Text style={{ color: "#0f0", fontSize: 18, marginBottom: 8 }}>
        Current Coupon
      </Text>

      <FlatList
        data={selections}
        keyExtractor={(_, index) => String(index)}
        ListEmptyComponent={
          <Text style={{ color: "#666", textAlign: "center", marginTop: 24 }}>
            No selections added yet.
          </Text>
        }
        renderItem={({ item, index }) => (
          <View
            style={{
              padding: 8,
              borderBottomWidth: 1,
              borderBottomColor: "#222",
              flexDirection: "row",
              justifyContent: "space-between"
            }}
          >
            <View style={{ flex: 1 }}>
              <Text style={{ color: "#fff" }}>
                {item.home} vs {item.away}
              </Text>
              <Text style={{ color: "#aaa" }}>
                {item.market} – {item.outcome}
              </Text>
              <Text style={{ color: "#0f0" }}>@ {item.odds.toFixed(2)}</Text>
            </View>
            <TouchableOpacity onPress={() => removeSelection(index)}>
              <Text style={{ color: "#f55" }}>Remove</Text>
            </TouchableOpacity>
          </View>
        )}
      />

      <View style={{ padding: 8 }}>
        <Text style={{ color: "#fff", marginBottom: 4 }}>
          Total odds: {totalOdds.toFixed(2)}
        </Text>
        <Button
          title={sending ? "Saving..." : "Save coupon to backend"}
          onPress={sendCoupon}
        />
      </View>
    </View>
  );
}
