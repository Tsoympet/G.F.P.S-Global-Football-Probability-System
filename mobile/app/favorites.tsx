import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  FlatList,
  TouchableOpacity
} from "react-native";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";

type FavLeague = { id: number; league_id: string; league_name: string };

export default function FavoritesScreen() {
  const { token } = useAuth();
  const [leagueId, setLeagueId] = useState("");
  const [leagueName, setLeagueName] = useState("");
  const [items, setItems] = useState<FavLeague[]>([]);

  const load = async () => {
    if (!token) return;
    try {
      const res = await api.get("/favorites/leagues", { params: { token } });
      setItems(res.data.items || []);
    } catch (err) {
      console.log("favorites error", err);
    }
  };

  useEffect(() => {
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

  const addLeague = async () => {
    if (!leagueId || !leagueName) return;
    try {
      await api.post("/favorites/league", {
        token,
        league_id: leagueId,
        league_name: leagueName
      });
      setLeagueId("");
      setLeagueName("");
      await load();
    } catch (err) {
      console.log("add league error", err);
    }
  };

  const removeLeague = async (id: number) => {
    try {
      await api.delete(`/favorites/league/${id}`, { params: { token } });
      await load();
    } catch (err) {
      console.log("delete league error", err);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#000", padding: 8 }}>
      <Text style={{ color: "#0f0", fontSize: 18, marginBottom: 8 }}>
        Favorite Leagues
      </Text>

      <Text style={{ color: "#fff" }}>League ID</Text>
      <TextInput
        style={{
          backgroundColor: "#111",
          color: "#fff",
          borderWidth: 1,
          borderColor: "#333",
          marginBottom: 4,
          padding: 6
        }}
        value={leagueId}
        onChangeText={setLeagueId}
      />
      <Text style={{ color: "#fff" }}>League Name</Text>
      <TextInput
        style={{
          backgroundColor: "#111",
          color: "#fff",
          borderWidth: 1,
          borderColor: "#333",
          marginBottom: 8,
          padding: 6
        }}
        value={leagueName}
        onChangeText={setLeagueName}
      />
      <Button title="Add League" onPress={addLeague} />

      <FlatList
        style={{ marginTop: 16 }}
        data={items}
        keyExtractor={item => String(item.id)}
        renderItem={({ item }) => (
          <View
            style={{
              padding: 8,
              borderBottomColor: "#222",
              borderBottomWidth: 1,
              flexDirection: "row",
              justifyContent: "space-between"
            }}
          >
            <View>
              <Text style={{ color: "#fff" }}>{item.league_name}</Text>
              <Text style={{ color: "#777" }}>ID: {item.league_id}</Text>
            </View>
            <TouchableOpacity onPress={() => removeLeague(item.id)}>
              <Text style={{ color: "#f55" }}>Remove</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
}
