import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
const LifeScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>LIFE频道</Text>
      <Text style={styles.subtitle}>索儿 - 生活健康管理智能体</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#666'
  }
});
export default LifeScreen;