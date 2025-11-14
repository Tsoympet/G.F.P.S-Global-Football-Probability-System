import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";

type Props = {
  home: string;
  away: string;
  league?: string;
  kickoff?: string;
  rightText?: string;
  onPress?: () => void;
};

export const MatchRow: React.FC<Props> = ({
  home,
  away,
  league,
  kickoff,
  rightText,
  onPress
}) => {
  return (
    <TouchableOpacity
      disabled={!onPress}
      onPress={onPress}
      style={styles.container}
      activeOpacity={onPress ? 0.8 : 1}
    >
      <View style={{ flex: 1 }}>
        <Text style={styles.teams}>
          {home} vs {away}
        </Text>
        {league ? <Text style={styles.league}>{league}</Text> : null}
        {kickoff ? <Text style={styles.kickoff}>{kickoff}</Text> : null}
      </View>
      {rightText ? <Text style={styles.right}>{rightText}</Text> : null}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#222",
    flexDirection: "row",
    alignItems: "center"
  },
  teams: {
    color: "#0f0",
    fontWeight: "600"
  },
  league: {
    color: "#aaa",
    fontSize: 12
  },
  kickoff: {
    color: "#666",
    fontSize: 11
  },
  right: {
    color: "#fff",
    marginLeft: 8,
    fontWeight: "600"
  }
});
