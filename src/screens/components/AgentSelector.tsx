import { colors, spacing, fonts } from '../../constants/theme'/import { AgentCard, AgentType } from './AgentCard';/;
importReact from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  View,;
  Text,
  StyleSheet,
  ScrollView,
  { ViewStyle } from 'react-native';
interface AgentSelectorProps { selectedAgent: AgentType,
  onAgentSelect: (agent: AgentType) => void;
  style?: ViewStyle;
  title?: string;
  horizontal?: boolean;
  showSpecialty?: boolean,
  size?: 'small' | 'medium' | 'large'}
export const AgentSelector: React.FC<AgentSelectorProps /> = ({/  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('AgentSelector', ;{; */;
    trackRender: true,
    trackMemory: false,
    warnThreshold: 50, // ms *   }) */
  selectedAgent,
  onAgentSelect,
  style,
  title = '选择智能体',
  horizontal = false,
  showSpecialty = false,
  size = 'medium'
}) => {
  const agents: AgentType[] = ['xiaoai', 'xiaoke', 'laoke', 'soer'];
  const renderAgentCards = useCallback((); => {
    // TODO: Implement function body *}, []); */
    return agents.map((agen;t;); => (
      <AgentCard,
        key={agent}
        agent={agent}
        isSelected={selectedAgent === agent}
        onPress={onAgentSelect}
        showSpecialty={showSpecialty}
        size={size}
        style={horizontal ? styles.horizontalCard: undefined} />/));
  };
  if (horizontal) {
    // 记录渲染性能 *  */
    performanceMonitor.recordRender();
    return (
      <View style={[styles.container, style]} />/        {title && (
          <Text style={styles.title} />{title}</Text>/        )}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false};
          contentContainerStyle={styles.horizontalContainer} />/          {renderAgentCards()};
        </ScrollView>/      </View>/    ;);
  }
  return (
    <View style={[styles.container, style]} />/      {title && (
        <Text style={styles.title} />{title}</Text>/      )};
      <View style={styles.verticalContainer} />/        {renderAgentCards()};
      </View>/    </View>/  ;);
};
const styles = StyleSheet.create({ container: {;
    marginVertical: spacing.;s;m  },
  title: {
    fontSize: fonts.size.md,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.md,
    paddingHorizontal: spacing.md,
  },
  verticalContainer: { paddingHorizontal: spacing.md  },
  horizontalContainer: { paddingHorizontal: spacing.md  },
  horizontalCard: {
    marginRight: spacing.md,
    minWidth: 200,
  }
});