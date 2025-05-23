import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { AgentType, agentInfo } from '../../api/agents';
import { lightTheme } from '../../config/theme';

const AgentSelection = () => {
  const navigation = useNavigation<any>();
  const colors = lightTheme.colors;

  const handleAgentSelect = (agentType: AgentType) => {
    navigation.navigate('AgentChannel', { agentType });
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>智能体专区</Text>
        <Text style={styles.subtitle}>
          四大智能体各具特色，为您提供全方位的健康管理服务
        </Text>

        {Object.values(AgentType).map((agentType) => {
          const agent = agentInfo[agentType];
          return (
            <TouchableOpacity
              key={agentType}
              style={styles.agentCard}
              onPress={() => handleAgentSelect(agentType)}
            >
              <View style={styles.agentHeader}>
                <View style={[styles.agentAvatar, { backgroundColor: agent.color + '20' }]}>
                  <Icon name={agent.avatar} size={32} color={agent.color} />
                </View>
                <View style={styles.agentInfo}>
                  <Text style={styles.agentName}>{agent.name}</Text>
                  <Text style={styles.agentDescription}>{agent.description}</Text>
                </View>
              </View>

              <View style={styles.abilitiesContainer}>
                {agent.abilities.map((ability, index) => (
                  <View key={index} style={styles.abilityTag}>
                    <Text style={styles.abilityText}>{ability}</Text>
                  </View>
                ))}
              </View>
            </TouchableOpacity>
          );
        })}

        <View style={styles.collaborationCard}>
          <Text style={styles.collaborationTitle}>智能体协同</Text>
          <Text style={styles.collaborationDescription}>
            四大智能体相互协作，提供全方位、个性化的健康管理服务。
            通过"辨证论治未病"的中医理念与现代技术相结合，
            打造全生命周期的健康解决方案。
          </Text>
          <TouchableOpacity 
            style={styles.collaborationButton}
            onPress={() => navigation.navigate('AgentCollaboration')}
          >
            <Text style={styles.collaborationButtonText}>了解更多</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// 静态样式，使用从theme导入的颜色
const colors = lightTheme.colors;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    padding: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.onBackground,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.onSurfaceVariant,
    marginBottom: 24,
  },
  agentCard: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  agentHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  agentAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  agentInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  agentName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.onSurface,
    marginBottom: 4,
  },
  agentDescription: {
    fontSize: 14,
    color: colors.onSurfaceVariant,
    lineHeight: 20,
  },
  abilitiesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  abilityTag: {
    backgroundColor: colors.primaryContainer,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  abilityText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: '500',
  },
  collaborationCard: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    padding: 20,
    marginTop: 8,
    marginBottom: 30,
  },
  collaborationTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  collaborationDescription: {
    fontSize: 14,
    color: '#FFFFFF',
    lineHeight: 22,
    opacity: 0.9,
    marginBottom: 16,
  },
  collaborationButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 24,
    alignSelf: 'flex-start',
  },
  collaborationButtonText: {
    color: colors.primary,
    fontWeight: 'bold',
    fontSize: 14,
  },
});

export default AgentSelection; 