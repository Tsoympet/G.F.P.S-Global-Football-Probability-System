import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ActivityIndicator
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { api } from "../lib/api";
import { useCoupon } from "../context/CouponContext";
import { MarketSelector, MarketItem } from "./components/MarketSelector";

export default function MatchScreen() {
  const params = useLocalSearchParams<{
    fixture_id: string;
    league_id: string;
    league: string;
    home: string;
    away: string;
  }>();

  const { addSelection } = useCoupon();

  const [markets, setMarkets] = useState<MarketItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Helper: επειδή τα params μπορεί να είναι string ή string[]
  const fixtureId =
    Array.isArray(params.fixture_id) ? params.fixture_id[0] : params.fixture_id;
  const leagueId =
    Array.isArray(params.league_id) ? params.league_id[0] : params.league_id;
  const league =
    Array.isArray(params.league) ? params.league[0] : params.league;
  const home =
    Array.isArray(params.home) ? params.home[0] : params.home;
  const away =
    Array.isArray(params.away) ? params.away[0] : params.away;

  useEffect(() => {
    const load = async () => {
      if (!fixtureId) return;
      setLoading(true);
      try {
        const res = await api.get("/fixtures/markets", {
          params: { fixture_id: Number(fixtureId) }
        });
        setMarkets(res.data?.markets || []);
      } catch (err) {
        console.log("markets error", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [fixtureId]);

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
    <View
      style={{
        padding: 12,
        borderBottomWidth: 1,
        borderBottomColor: "#222"
      }}
    >
      <Text
        style={{ color: "#0f0", fontSize: 18, fontWeight: "bold" }}
      >
        {home} vs {away}
      </Text>
      <Text style={{ color: "#aaa" }}>{league}</Text>
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      {header}
      <MarketSelector
        markets={markets}
        onSelect={({ market, outcome, odds }) =>
          addSelection({
            fixture_id: String(fixtureId),
            league: league || "",
            league_id: String(leagueId || ""),
            home: home || "",
            away: away || "",
            market,
            outcome,
            odds
          })
        }
      />
    </View>
  );
}
