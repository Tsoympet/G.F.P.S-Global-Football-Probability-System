import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { api } from "../lib/api";
import { useCoupon } from "../context/CouponContext";

type Market = {
  bookmaker: string;
  market: string;
  selections: { outcome: string; odds: number }[];
};

export default function MatchScreen() {
  const params = useLocalSearchParams<{
    fixture_id: string;
    league_id: string;
    league: string;
    home: string;
    away: string;
  }>();

  const { addSelection } = useCoupon();

  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      if (!params.fixture_id) return;
      setLoading(true);
      try {
        const res = await api.get("/fixtures/markets", {
          params: { fixture_id: Number(params.fixture_id) }
        });
        setMarkets(res.data?.markets || []);
      } catch (err) {
        console.log("markets error", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [params.fixture_id]);

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

  const header = (
    <View style={{ padding: 12, borderBottomWidth: 1, borderBottomColor: "#222" }}>
      <Text style={{ color: "#0f0", fontSize: 18, fontWeight: "bold" }}>
        {params.home} vs {params.away}
      </Text>
      <Text style={{ color: "#aaa" }}>{params.league}</Text>
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      {header}
      <FlatList
        data={markets}
        keyExtractor={(_, index) => String(index)}
        renderItem={({ item }) => (
          <View
            style={{
              padding: 12,
              borderBottomWidth: 1,
              borderBottomColor: "#222"
            }}
          >
            <Text style={{ color: "#fff", marginBottom: 4 }}>
              {item.bookmaker} – {item.market}
            </Text>
            {item.selections.map((s, idx) => (
              <TouchableOpacity
                key={idx}
                style={{
                  padding: 8,
                  marginVertical: 2,
                  backgroundColor: "#111",
                  borderRadius: 4
                }}
                onPress={() =>
                  addSelection({
                    fixture_id: String(params.fixture_id),
                    league: params.league || "",
                    league_id: String(params.league_id || ""),
                    home: params.home || "",
                    away: params.away || "",
                    market: item.market,
                    outcome: s.outcome,
                    odds: s.odds
                  })
                }
              >
                <Text style={{ color: "#0f0" }}>
                  {s.outcome} @ {s.odds.toFixed(2)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      />
    </View>
  );
}
