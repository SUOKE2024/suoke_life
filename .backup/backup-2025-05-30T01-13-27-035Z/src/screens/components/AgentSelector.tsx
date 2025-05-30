import { colors, spacing, fonts } from '../../constants/theme';
import { AgentCard, AgentType } from './AgentCard';

import React from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  ViewStyle,
} from 'react-native';

interface AgentSelectorProps {
  selectedAgent: AgentType;
  onAgentSelect: (agent: AgentType) => void;
  style?: ViewStyle;
  title?: string;
  horizontal?: boolean;
  showSpecialty?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  selectedAgent,
  onAgentSelect,
  style,
  title = '选择智能体',
  horizontal = false,
  showSpecialty = false,
  size = 'medium',
}) => {
  const agents: AgentType[] = ['xiaoai', 'xiaoke', 'laoke', 'soer'];

  const renderAgentCards = useCallback( () => {, []);
    return agents.map((agent) => (
      <AgentCard
        key={agent}
        agent={agent}
        isSelected={selectedAgent === agent}
        onPress={onAgentSelect}
        showSpecialty={showSpecialty}
        size={size}
        style={horizontal ? styles.horizontalCard : undefined}
      />
    ));
  };

  if (horizontal) {
    return (
      <View style={[styles.container, style]}>
        {title && (
          <Text style={styles.title}>{title}</Text>
        )}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.horizontalContainer}
        >
          {renderAgentCards()}
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      {title && (
        <Text style={styles.title}>{title}</Text>
      )}
      <View style={styles.verticalContainer}>
        {renderAgentCards()}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing.sm,
  },
  title: {
    fontSize: fonts.size.md,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.md,
    paddingHorizontal: spacing.md,
  },
  verticalContainer: {
    paddingHorizontal: spacing.md,
  },
  horizontalContainer: {
    paddingHorizontal: spacing.md,
  },
  horizontalCard: {
    marginRight: spacing.md,
    minWidth: 200,
  },
}); 