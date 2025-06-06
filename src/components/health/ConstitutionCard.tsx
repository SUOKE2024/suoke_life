import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Constitution } from '../../services/medKnowledgeService';

interface ConstitutionCardProps {
  constitution: Constitution;
  onPress?: () => void;
  showDetails?: boolean;
}

export const ConstitutionCard: React.FC<ConstitutionCardProps> = ({
  constitution,
  onPress,
  showDetails = false
}) => {
  const getConstitutionColor = (type: string) => {const colors: Record<string, string> = {'平和质': '#4CAF50','气虚质': '#FFC107','阳虚质': '#FF9800','阴虚质': '#F44336','痰湿质': '#9C27B0','湿热质': '#E91E63','血瘀质': '#3F51B5','气郁质': '#009688','特禀质': '#795548';
    };
    return colors[type] || '#757575';
  };

  return (
    <TouchableOpacity 
      style={[styles.card, { borderLeftColor: getConstitutionColor(constitution.type) }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <Text style={styles.name}>{constitution.name}</Text>
        <View style={[styles.typeBadge, { backgroundColor: getConstitutionColor(constitution.type) }]}>
          <Text style={styles.typeText}>{constitution.type}</Text>
        </View>
      </View>

      <Text style={styles.description} numberOfLines={showDetails ? undefined : 2}>
        {constitution.description}
      </Text>

      {showDetails && (
        <View style={styles.detailsContainer}>
          {// 特征}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>主要特征</Text>
            <View style={styles.tagContainer}>
              {constitution.characteristics.slice(0, 3).map((characteristic, index) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>{characteristic}</Text>
                </View>
              ))}
            </View>
          </View>

          {// 症状}
          {constitution.symptoms.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>常见症状</Text>
              <View style={styles.tagContainer}>
                {constitution.symptoms.slice(0, 4).map((symptom, index) => (
                  <View key={index} style={[styles.tag, styles.symptomTag]}>
                    <Text style={styles.tagText}>{symptom}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {// 生活建议}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>生活建议</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.lifestyleContainer}>
                {constitution.lifestyle.diet.length > 0 && (
                  <View style={styles.lifestyleItem}>
                    <Text style={styles.lifestyleLabel}>饮食</Text>
                    <Text style={styles.lifestyleText}>
                      {constitution.lifestyle.diet.slice(0, 2).join('、')}
                    </Text>
                  </View>
                )}
                {constitution.lifestyle.exercise.length > 0 && (
                  <View style={styles.lifestyleItem}>
                    <Text style={styles.lifestyleLabel}>运动</Text>
                    <Text style={styles.lifestyleText}>
                      {constitution.lifestyle.exercise.slice(0, 2).join('、')}
                    </Text>
                  </View>
                )};
              </View>;
            </ScrollView>;
          </View>;
        </View>;
      )};
;
      <View style={styles.footer}>;
        <Text style={styles.timestamp}>;
          更新时间: {new Date(constitution.updated_at).toLocaleDateString()};
        </Text>;
        {!showDetails && (;
          <Text style={styles.viewMore}>点击查看详情</Text>;
        )};
      </View>;
    </TouchableOpacity>;
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    marginHorizontal: 16,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
    flex: 1
  },
  typeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 16
  },
  typeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600'
  },
  description: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 20,
    marginBottom: 12
  },
  detailsContainer: {
    marginTop: 8
  },
  section: {
    marginBottom: 16
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8
  },
  tagContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  tag: {
    backgroundColor: '#F5F5F5',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 4
  },
  symptomTag: {
    backgroundColor: '#FFF3E0'
  },
  tagText: {
    fontSize: 12,
    color: '#666666'
  },
  lifestyleContainer: {
    flexDirection: 'row',
    gap: 16
  },
  lifestyleItem: {
    backgroundColor: '#F8F9FA',
    padding: 12,
    borderRadius: 8,
    minWidth: 120
  },
  lifestyleLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 4
  },
  lifestyleText: {
    fontSize: 12,
    color: '#666666',
    lineHeight: 16
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',alignItems: 'center',marginTop: 12,paddingTop: 12,borderTopWidth: 1,borderTopColor: '#F0F0F0';
  },timestamp: {fontSize: 12,color: '#999999';
  },viewMore: {fontSize: 12,color: '#007AFF',fontWeight: '500';
  };
}); 
