import React, { useEffect, useState } from "react";
import { View, Text, Alert, ScrollView, TouchableOpacity } from "react-native";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { ScreenContainer } from "./components/ScreenContainer";
import { SectionCard } from "./components/SectionCard";
import { TextField } from "./components/TextField";
import { PrimaryButton } from "./components/PrimaryButton";
import { EmptyState } from "./components/EmptyState";

type AlertRuleItem = {
  id: number;
  name: string;
  league_filter?: string | null;
  team_filter?: string | null;
  market_filter?: string | null;
  outcome_filter?: string | null;
  min_odds?: number | null;
  max_odds?: number | null;
  min_ev?: number | null;
  is_active: boolean;
};

export default function AlertsScreen() {
  const { token } = useAuth();

  const [rules, setRules] = useState<AlertRuleItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [name, setName] = useState("");
  const [leagueFilter, setLeagueFilter] = useState("");
  const [teamFilter, setTeamFilter] = useState("");
  const [marketFilter, setMarketFilter] = useState("");
  const [outcomeFilter, setOutcomeFilter] = useState("");
  const [minOdds, setMinOdds] = useState("");
  const [maxOdds, setMaxOdds] = useState("");
  const [minEv, setMinEv] = useState("");

  const loadRules = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await api.get("/alerts/rules", { params: { token } });
      setRules(res.data.items || []);
    } catch (err) {
      console.log("alerts rules error", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
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

  const parseNum = (val: string): number | undefined => {
    const n = Number(val.replace(",", "."));
    if (Number.isNaN(n)) return undefined;
    return n;
  };

  const createRule = async () => {
    if (!name.trim()) {
      Alert.alert("Name required", "Please enter a rule name.");
      return;
    }
    try {
      await api.post("/alerts/rules", {
        token,
        name,
        league_filter: leagueFilter || undefined,
        team_filter: teamFilter || undefined,
        market_filter: marketFilter || undefined,
        outcome_filter: outcomeFilter || undefined,
        min_odds: parseNum(minOdds),
        max_odds: parseNum(maxOdds),
        min_ev: parseNum(minEv),
        is_active: true
      });
      setName("");
      setLeagueFilter("");
      setTeamFilter("");
      setMarketFilter("");
      setOutcomeFilter("");
      setMinOdds("");
      setMaxOdds("");
      setMinEv("");
      await loadRules();
    } catch (err) {
      console.log("create rule error", err);
      Alert.alert("Error", "Failed to create rule.");
    }
  };

  const toggleActive = async (rule: AlertRuleItem) => {
    try {
      await api.patch(`/alerts/rules/${rule.id}`, {
        token,
        is_active: !rule.is_active
      });
      await loadRules();
    } catch (err) {
      console.log("toggle rule error", err);
      Alert.alert("Error", "Failed to update rule.");
    }
  };

  const deleteRule = async (rule: AlertRuleItem) => {
    Alert.alert(
      "Delete rule",
      `Are you sure you want to delete "${rule.name}"?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await api.delete(`/alerts/rules/${rule.id}`, {
                params: { token }
              });
              await loadRules();
            } catch (err) {
              console.log("delete rule error", err);
              Alert.alert("Error", "Failed to delete rule.");
            }
          }
        }
      ]
    );
  };

  return (
    <ScreenContainer>
      <ScrollView>
        <SectionCard title="New Alert Rule">
          <TextField
            label="Rule name"
            value={name}
            onChangeText={setName}
            placeholder="EV+ Over 2.5 Premier League"
          />
          <TextField
            label="League filter (contains)"
            value={leagueFilter}
            onChangeText={setLeagueFilter}
            placeholder="Premier League"
          />
          <TextField
            label="Team filter (contains)"
            value={teamFilter}
            onChangeText={setTeamFilter}
            placeholder="Liverpool"
          />
          <TextField
            label="Market filter (contains)"
            value={marketFilter}
            onChangeText={setMarketFilter}
            placeholder="Over/Under"
          />
          <TextField
            label="Outcome filter (contains)"
            value={outcomeFilter}
            onChangeText={setOutcomeFilter}
            placeholder="Over 2.5"
          />
          <TextField
            label="Min odds"
            value={minOdds}
            onChangeText={setMinOdds}
            placeholder="1.80"
            keyboardType="decimal-pad"
          />
          <TextField
            label="Max odds"
            value={maxOdds}
            onChangeText={setMaxOdds}
            placeholder="3.50"
            keyboardType="decimal-pad"
          />
          <TextField
            label="Min EV (e.g. 0.05 = +5%)"
            value={minEv}
            onChangeText={setMinEv}
            placeholder="0.05"
            keyboardType="decimal-pad"
          />

          <PrimaryButton label="Create rule" onPress={createRule} />
        </SectionCard>

        <SectionCard title="Existing Rules">
          {loading ? (
            <Text style={{ color: "#fff" }}>Loading...</Text>
          ) : !rules.length ? (
            <EmptyState message="No alert rules defined yet." />
          ) : (
            rules.map(rule => (
              <View
                key={rule.id}
                style={{
                  borderBottomWidth: 1,
                  borderBottomColor: "#222",
                  paddingVertical: 8
                }}
              >
                <Text style={{ color: "#0f0", fontWeight: "700" }}>
                  {rule.name}
                </Text>
                <Text style={{ color: "#aaa", fontSize: 12 }}>
                  League: {rule.league_filter || "any"} | Team:{" "}
                  {rule.team_filter || "any"}
                </Text>
                <Text style={{ color: "#aaa", fontSize: 12 }}>
                  Market: {rule.market_filter || "any"} | Outcome:{" "}
                  {rule.outcome_filter || "any"}
                </Text>
                <Text style={{ color: "#fff", fontSize: 12 }}>
                  Min odds:{" "}
                  {rule.min_odds != null ? rule.min_odds.toFixed(2) : "any"} | Max
                  odds:{" "}
                  {rule.max_odds != null ? rule.max_odds.toFixed(2) : "any"}
                </Text>
                <Text style={{ color: "#fff", fontSize: 12 }}>
                  Min EV:{" "}
                  {rule.min_ev != null ? rule.min_ev.toFixed(2) : "any"} |{" "}
                  Status: {rule.is_active ? "ACTIVE" : "INACTIVE"}
                </Text>

                <View
                  style={{
                    flexDirection: "row",
                    marginTop: 6,
                    gap: 8
                  }}
                >
                  <PrimaryButton
                    label={rule.is_active ? "Deactivate" : "Activate"}
                    onPress={() => toggleActive(rule)}
                    style={{ flex: 1 }}
                  />
                  <TouchableOpacity
                    style={{
                      flex: 1,
                      alignItems: "center",
                      justifyContent: "center",
                      paddingVertical: 8,
                      borderRadius: 6,
                      borderWidth: 1,
                      borderColor: "#f55"
                    }}
                    onPress={() => deleteRule(rule)}
                  >
                    <Text style={{ color: "#f55", fontWeight: "600" }}>
                      Delete
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))
          )}
        </SectionCard>
      </ScrollView>
    </ScreenContainer>
  );
}
