import React, { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, Text, View } from "react-native";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { ScreenContainer } from "./components/ScreenContainer";
import { MatchCard } from "./components/MatchCard";
import { EmptyState } from "./components/EmptyState";
import { PrimaryButton } from "./components/PrimaryButton";

type ValuePick = {
  id: number;
  fixture_id: string;
  league: string;
  league_id: string;
  home: string;
  away: string;
  bookmaker: string;
  market: string;
  outcome: string;
  odds: number;
  prob: number;
  ev: number;
  created_at: string;
};

export default function ValuePicksScreen() {
  const { token } = useAuth();
  const [picks, setPicks] = useState<ValuePick[]>([]);
  const [loading, setLoading] = useState(true);
  const [minEv, setMinEv] = useState(0.05);

  const loadPicks = async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await api.get("/value-picks", {
        params: { min_ev: minEv }
      });
      setPicks(res.data || []);
    } catch (err) {
      console.log("value-picks error", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPicks();
  }, [token]);

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

  if (loading) {
    return (
      <ScreenContainer
        style={{
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <ActivityIndicator size="large" />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <View
        style={{
          marginBottom: 8,
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >
        <Text style={{ color: "#0f0", fontSize: 18, fontWeight: "700" }}>
          Value Picks
        </Text>
        <PrimaryButton label="Refresh" onPress={loadPicks} />
      </View>

      <FlatList
        data={picks}
        keyExtractor={item => String(item.id)}
        ListEmptyComponent={
          <EmptyState message="No EV+ picks at the moment. Try again later." />
        }
        renderItem={({ item }) => {
          const badgeText = `EV ${(item.ev * 100).toFixed(1)}%`;
          const badgeColor =
            item.ev >= 0.10 ? "#ffcc00" : item.ev >= 0.05 ? "#00ff88" : "#00bfff";

          const rightText = `${item.market} ${item.outcome} @ ${item.odds.toFixed(
            2
          )}`;

          return (
            <MatchCard
              home={item.home}
              away={item.away}
              league={`${item.league} (${item.bookmaker})`}
              kickoff={""}
              rightText={rightText}
              badgeText={badgeText}
              badgeColor={badgeColor}
              isLive={true}
            />
          );
        }}
      />
    </ScreenContainer>
  );
}
