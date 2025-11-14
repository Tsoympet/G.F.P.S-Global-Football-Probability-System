import React, { useEffect, useState } from "react";
import { View, Text, FlatList, ActivityIndicator } from "react-native";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";

type CouponItem = {
  id: number;
  name: string;
  status: string;
  total_odds: number;
  total_prob: number;
  total_ev: number;
  created_at: string;
};

export default function CouponHistoryScreen() {
  const { token } = useAuth();
  const [items, setItems] = useState<CouponItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const res = await api.get("/coupon/list", { params: { token } });
        setItems(res.data.items || []);
      } catch (err) {
        console.log("coupon history error", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [token]);

  if (!token) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: "#000",
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <Text style={{ color: "#fff" }}>You need to login first.</Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: "#000",
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: "#000", padding: 8 }}>
      <FlatList
        data={items}
        keyExtractor={item => String(item.id)}
        renderItem={({ item }) => (
          <View
            style={{
              padding: 8,
              borderBottomWidth: 1,
              borderBottomColor: "#222"
            }}
          >
            <Text style={{ color: "#0f0" }}>{item.name}</Text>
            <Text style={{ color: "#aaa" }}>Status: {item.status}</Text>
            <Text style={{ color: "#fff" }}>
              Odds: {item.total_odds.toFixed(2)} | EV:{" "}
              {item.total_ev.toFixed(2)}
            </Text>
            <Text style={{ color: "#777" }}>{item.created_at}</Text>
          </View>
        )}
      />
    </View>
  );
}
