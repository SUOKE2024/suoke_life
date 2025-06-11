import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

// ARConstitutionVisualization - AR体质可视化组件
// 索克生活 - 使用AR技术展示用户体质状况

interface ARConstitutionVisualizationProps {
  constitution?: {
    type: string;
    score: number;
    characteristics: string[];
  };
  onVisualizationReady?: () => void;
}

const ARConstitutionVisualization: React.FC<ARConstitutionVisualizationProps> = ({
  constitution,
  onVisualizationReady,
}) => {
  // TODO: 实现AR体质可视化功能
  // 这里将来会集成AR库来展示3D体质模型

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AR体质可视化</Text>
      <Text style={styles.subtitle}>功能开发中...</Text>
      
      {constitution && (
        <View style={styles.constitutionInfo}>
          <Text style={styles.constitutionType}>体质类型: {constitution.type}</Text>
          <Text style={styles.constitutionScore}>体质评分: {constitution.score}</Text>
          {constitution.characteristics.map((char, index) => (
            <Text key={index} style={styles.characteristic}>• {char}</Text>
          ))}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#35bb78',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  constitutionInfo: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  constitutionType: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  constitutionScore: {
    fontSize: 16,
    color: '#35bb78',
    marginBottom: 12,
  },
  characteristic: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});

export default ARConstitutionVisualization;