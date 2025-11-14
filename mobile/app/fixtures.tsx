import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator
} from "react-native";
import { useRouter } from "expo-router";
import { api } from "../lib/api";
import { useAuth } from "../auth/AuthContext";

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
  }, []);

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
        data={fixtures}
        keyExtractor={item => String(item.fixture_id)}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={{
              padding: 12,
              borderBottomWidth: 1,
              borderBottomColor: "#222"
            }}
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
          >
            <Text style={{ color: "#0f0", fontWeight: "bold" }}>
              {item.home} vs {item.away}
            </Text>
            <Text style={{ color: "#aaa" }}>{item.league}</Text>
            <Text style={{ color: "#777" }}>{item.kickoff}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}
