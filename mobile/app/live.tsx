import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Text
} from "react-native";
import { useRouter } from "expo-router";
import { api } from "../lib/api";
import { useAuth } from "../auth/AuthContext";

import { ScreenContainer } from "./components/ScreenContainer";
import { MatchCard } from "./components/MatchCard";
import { EmptyState } from "./components/EmptyState";

type LiveFixture = {
  fixture_id: number | string;
  league_id: number | string;
  league: string;
  home: string;
  away: string;
  kickoff?: string;

  // προαιρετικά, αν τα δίνει το backend:
  status?: string;
  minute?: number;
  score_home?: number;
  score_away?: number;
};

const REFRESH_MS = 20000; // 20s auto-refresh

export default function LiveScreen() {
  const router = useRouter();
  const { token } = useAuth();
  const [fixtures, setFixtures] = useState<LiveFixture[]>([]);
  const [loading, setLoading] = useState(true);

  const loadLive = async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      // Αν το backend χρησιμοποιεί άλλο path, π.χ. /fixtures?live=1,
      // άλλαξε εδώ:
      const res = await api.get("/fixtures/live");
      if (res.data?.fixtures) {
        setFixtures(res.data.fixtures);
      } else if (Array.isArray(res.data)) {
        setFixtures(res.data as LiveFixture[]);
      } else {
        setFixtures([]);
      }
    } catch (err) {
      console.log("live fixtures error", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLive();

    const id = setInterval(() => {
      loadLive();
    }, REFRESH_MS);

    return () => clearInterval(id);
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
      <FlatList
        data={fixtures}
        keyExtractor={item => String(item.fixture_id)}
        ListEmptyComponent={
          <EmptyState message="No live matches at the moment." />
        }
        renderItem={({ item }) => {
          const scoreDefined =
            typeof item.score_home === "number" &&
            typeof item.score_away === "number";

          const minuteText =
            typeof item.minute === "number" && item.minute >= 0
              ? `${item.minute}'`
              : "";

          const rightText = scoreDefined
            ? `${item.score_home}-${item.score_away}${
                minuteText ? " " + minuteText : ""
              }`
            : minuteText || "LIVE";

          return (
            <MatchCard
              home={item.home}
              away={item.away}
              league={item.league}
              kickoff={item.kickoff}
              isLive={true}
              rightText={rightText}
              onPress={() =>
                router.push({
                  pathname: "/match",
                  params: {
                    fixture_id: String(item.fixture_id),
                    league_id: String(item.league_id),
                    league: item.league,
                    home: item.home,
                    away: item.away
                  }
                })
              }
            />
          );
        }}
      />
    </ScreenContainer>
  );
}
