import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ViewStyle } from "react-native";
import { TeamBadge } from "./TeamBadge";

type Props = {
  home: string;
  away: string;
  league?: string;
  kickoff?: string;
  rightText?: string;
  isLive?: boolean;
  onPress?: () => void;
  style?: ViewStyle | ViewStyle[];
};

export const MatchCard: React.FC<Props> = ({
  home,
  away,
  league,
  kickoff,
  rightText,
  isLive,
  onPress,
  style
}) => {
  return (
    <TouchableOpacity
      activeOpacity={onPress ? 0.85 : 1}
      onPress={onPress}
      style={[styles.card, style]}
    >
      <View style={styles.left}>
        <View style={styles.row}>
          <TeamBadge name={home} size={32} />
          <Text style={styles.teamText}>{home}</Text>
        </View>
        <View style={styles.row}>
          <TeamBadge name={away} size={32} />
          <Text style={styles.teamText}>{away}</Text>
        </View>
      </View>

      <View style={styles.right}>
        {league ? <Text style={styles.league}>{league}</Text> : null}
        {kickoff ? <Text style={styles.kickoff}>{kickoff}</Text> : null}
        {isLive ? <Text style={styles.live}>LIVE</Text> : null}
        {rightText ? <Text style={styles.rightText}>{rightText}</Text> : null}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#111",
    borderRadius: 8,
    padding: 10,
    marginVertical: 6,
    borderWidth: 1,
    borderColor: "#222",
    flexDirection: "row",
    justifyContent: "space-between"
  },
  left: {
    flex: 2
  },
  right: {
    flex: 1,
    alignItems: "flex-end",
    justifyContent: "center"
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4
  },
  teamText: {
    color: "#fff",
    marginLeft: 8,
    fontWeight: "600"
  },
  league: {
    color: "#aaa",
    fontSize: 12
  },
  kickoff: {
    color: "#777",
    fontSize: 11
  },
  live: {
    color: "#ff4444",
    fontSize: 12,
    fontWeight: "700",
    marginTop: 4
  },
  rightText: {
    color: "#0f0",
    marginTop: 4,
    fontWeight: "600"
  }
});
