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

type Fixture = {
  fixture_id: number | string;
  league_id: number | string;
  league: string;
  home: string;
  away: string;
  kickoff: string;
};

export default function FixturesScreen() {
  const router = useRouter();
  const { token } = useAuth();
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const res = await api.get("/fixtures");
        if (res.data?.fixtures) {
          setFixtures(res.data.fixtures);
        }
      } catch (err) {
        console.log("fixtures error", err);
      } finally {
        setLoading(false);
      }
    };
    load();
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
          <EmptyState message="No fixtures available at the moment." />
        }
        renderItem={({ item }) => (
          <MatchCard
            home={item.home}
            away={item.away}
            league={item.league}
            kickoff={item.kickoff}
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
        )}
      />
    </ScreenContainer>
  );
}
