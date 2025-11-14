import React from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ViewStyle
} from "react-native";
import { CouponSelection } from "../../context/CouponContext";

type Props = {
  selections: CouponSelection[];
  totalOdds: number;
  onRemove?: (index: number) => void;
  footer?: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
};

export const CouponView: React.FC<Props> = ({
  selections,
  totalOdds,
  onRemove,
  footer,
  style
}) => {
  return (
    <View style={[styles.container, style]}>
      <Text style={styles.title}>Current Coupon</Text>

      <FlatList
        data={selections}
        keyExtractor={(_, index) => String(index)}
        ListEmptyComponent={
          <Text style={styles.empty}>No selections added yet.</Text>
        }
        renderItem={({ item, index }) => (
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.match}>
                {item.home} vs {item.away}
              </Text>
              <Text style={styles.market}>
                {item.market} – {item.outcome}
              </Text>
              <Text style={styles.odds}>@ {item.odds.toFixed(2)}</Text>
            </View>
            {onRemove && (
              <TouchableOpacity onPress={() => onRemove(index)}>
                <Text style={styles.remove}>Remove</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      />

      <View style={styles.footer}>
        <Text style={styles.totalOdds}>
          Total odds: {totalOdds.toFixed(2)}
        </Text>
        {footer}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#111",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#222",
    padding: 10,
    flex: 1
  },
  title: {
    color: "#0f0",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 8
  },
  empty: {
    color: "#666",
    textAlign: "center",
    marginTop: 24
  },
  row: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#222",
    flexDirection: "row",
    justifyContent: "space-between"
  },
  match: {
    color: "#fff"
  },
  market: {
    color: "#aaa",
    fontSize: 12
  },
  odds: {
    color: "#0f0",
    fontWeight: "600"
  },
  remove: {
    color: "#f55",
    fontWeight: "600"
  },
  footer: {
    marginTop: 10
  },
  totalOdds: {
    color: "#fff",
    marginBottom: 6
  }
});
