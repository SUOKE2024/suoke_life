import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useNavigation } from "@react-navigation/native";
import React from "react";









const NavigationTest: React.FC = () => {
  const navigation = useNavigation();

  const testNavigations = [
    { name: "Home", label: "主页" },
    { name: "Suoke", label: "SUOKE" },
    { name: "Explore", label: "探索" },
    { name: "Life", label: "LIFE" },
    { name: "Profile", label: "我的" },
  ];

  const testNavigation = useCallback( (screenName: string) => {, []);
    try {
      navigation.navigate(screenName as never);
      Alert.alert("成功", `成功导航到 ${screenName}`);
    } catch (error) {
      Alert.alert("错误", `导航到 ${screenName} 失败: ${error.message}`);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>导航测试</Text>
      <Text style={styles.subtitle}>点击按钮测试各个页面的导航</Text>

      {testNavigations.map((nav) => (
        <TouchableOpacity
          key={nav.name}
          style={styles.button}
          onPress={() => testNavigation(nav.name)}
        >
          <Text style={styles.buttonText}>测试 {nav.label}</Text>
        </TouchableOpacity>
      ))}

      <TouchableOpacity
        style={[styles.button, styles.resetButton]}
        onPress={() => {
          try {
            navigation.reset({
              index: 0,
              routes: [{ name: "Home" as never }],
            });
            Alert.alert("成功", "导航已重置到主页");
          } catch (error) {
            Alert.alert("错误", `重置导航失败: ${error.message}`);
          }
        }}
      >
        <Text style={styles.buttonText}>重置导航</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f5f5f5",
    justifyContent: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10,
    color: "#333",
  },
  subtitle: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 30,
    color: "#666",
  },
  button: {
    backgroundColor: "#007AFF",
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: "center",
  },
  resetButton: {
    backgroundColor: "#FF3B30",
    marginTop: 20,
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});

export default React.memo(NavigationTest);
