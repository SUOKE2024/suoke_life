import { View, Text, StyleSheet, TouchableOpacity } from "../../placeholder";react-native;
import React from "react";
export const HomeHeader: React.FC  = () => {}
  return (;)
    <View style={styles.container}>;
      <Text style={styles.title}>索克生活</    Text>;
      <TouchableOpacity style={styles.menuButton}>;
        <Text style={styles.menuIcon}>☰</    Text>;
      </    TouchableOpacity>;
    </    View>;
  );
}
const styles = StyleSheet.create({container: {),
  flexDirection: row",
    justifyContent: "space-between,",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: white",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0"
  },
  title: {,
  fontSize: 20,
    fontWeight: "bold",
    color: #333""
  },
  menuButton: {,
  padding: 8;
  },
  menuIcon: {,
  fontSize: 18,
    color: '#666'
  };
});