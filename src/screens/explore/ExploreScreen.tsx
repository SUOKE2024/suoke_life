import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
const ExploreScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>探索频道</Text>
      <Text style={styles.subtitle}>老克 - 知识传播智能体</Text>
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
export default ExploreScreen;