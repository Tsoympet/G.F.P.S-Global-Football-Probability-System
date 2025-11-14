import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView
} from "react-native";

export type MarketSelection = {
  outcome: string;
  odds: number;
};

export type MarketItem = {
  bookmaker: string;
  market: string;
  selections: MarketSelection[];
};

type Props = {
  markets: MarketItem[];
  onSelect: (params: {
    market: string;
    outcome: string;
    odds: number;
    bookmaker: string;
  }) => void;
};

export const MarketSelector: React.FC<Props> = ({ markets, onSelect }) => {
  if (!markets.length) {
    return (
      <View style={{ padding: 12 }}>
        <Text style={{ color: "#666" }}>No markets available.</Text>
      </View>
    );
  }

  return (
    <ScrollView>
      {markets.map((m, idx) => (
        <View key={`${m.bookmaker}-${idx}`} style={styles.marketCard}>
          <Text style={styles.marketTitle}>
            {m.bookmaker} – {m.market}
          </Text>
          <View style={styles.chipRow}>
            {m.selections.map((s, i) => (
              <TouchableOpacity
                key={i}
                style={styles.chip}
                onPress={() =>
                  onSelect({
                    market: m.market,
                    outcome: s.outcome,
                    odds: s.odds,
                    bookmaker: m.bookmaker
                  })
                }
              >
                <Text style={styles.chipText}>
                  {s.outcome} @ {s.odds.toFixed(2)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  marketCard: {
    backgroundColor: "#111",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#222",
    padding: 10,
    marginHorizontal: 8,
    marginVertical: 4
  },
  marketTitle: {
    color: "#fff",
    marginBottom: 6,
    fontWeight: "600"
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap"
  },
  chip: {
    backgroundColor: "#222",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 6,
    marginBottom: 6
  },
  chipText: {
    color: "#0f0",
    fontSize: 12,
    fontWeight: "600"
  }
});
