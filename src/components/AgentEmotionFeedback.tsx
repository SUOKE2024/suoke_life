import { View, TouchableOpacity, Text, StyleSheet } from "react-native";
import React from "react";

const FEEDBACKS = [
  { key: "like", label: "👍", desc: "喜欢" },
  { key: "care", label: "🤗", desc: "关怀" },
  { key: "suggest", label: "💡", desc: "建议" },
  { key: "dislike", label: "👎", desc: "不喜欢" },
];

export const AgentEmotionFeedback: React.FC<{
  onFeedback: (type: string) => void;
}> = ({ onFeedback }) => {
  return (
    <View style={styles.row}>
      {FEEDBACKS.map((fb) => (
        <TouchableOpacity
          key={fb.key}
          style={styles.btn}
          onPress={() => onFeedback(fb.key)}
        >
          <Text style={styles.icon}>{fb.label}</Text>
          <Text style={styles.desc}>{fb.desc}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    justifyContent: "center",
    marginVertical: 8,
  },
  btn: {
    alignItems: "center",
    marginHorizontal: 10,
  },
  icon: {
    fontSize: 22,
  },
  desc: {
    fontSize: 12,
    color: "#666",
    marginTop: 2,
  },
});
