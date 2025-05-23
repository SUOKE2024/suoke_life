import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Text, Card, Button, Chip, useTheme, Surface, Avatar, ProgressBar, Checkbox } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTranslation } from 'react-i18next';

interface HealthTask {
  id: string;
  title: string;
  description: string;
  type: 'exercise' | 'diet' | 'sleep' | 'medication' | 'checkup' | 'meditation';
  duration?: number; // 分钟
  frequency: 'daily' | 'weekly' | 'monthly';
  targetValue?: number;
  currentValue?: number;
  unit?: string;
  completed: boolean;
  dueTime?: string;
  priority: 'high' | 'medium' | 'low';
}

interface HealthPlanProps {
  title: string;
  description?: string;
  tasks: HealthTask[];
  onTaskComplete?: (taskId: string) => void;
  onTaskEdit?: (task: HealthTask) => void;
  onPlanEdit?: () => void;
}

const HealthPlan: React.FC<HealthPlanProps> = ({
  title,
  description,
  tasks,
  onTaskComplete,
  onTaskEdit,
  onPlanEdit
}) => {
  const theme = useTheme();
  const { t } = useTranslation();
  
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  // 任务类型配置
  const taskTypeConfig = {
    exercise: { icon: 'run', color: '#FF6B6B', label: '运动' },
    diet: { icon: 'food-apple', color: '#4ECDC4', label: '饮食' },
    sleep: { icon: 'sleep', color: '#45B7D1', label: '睡眠' },
    medication: { icon: 'pill', color: '#96CEB4', label: '用药' },
    checkup: { icon: 'stethoscope', color: '#FFEAA7', label: '检查' },
    meditation: { icon: 'meditation', color: '#DDA0DD', label: '冥想' }
  };

  // 优先级配置
  const priorityConfig = {
    high: { color: '#F44336', label: '高' },
    medium: { color: '#FF9800', label: '中' },
    low: { color: '#4CAF50', label: '低' }
  };

  // 计算完成进度
  const calculateProgress = () => {
    if (tasks.length === 0) return 0;
    const completedTasks = tasks.filter(task => task.completed).length;
    return completedTasks / tasks.length;
  };

  // 过滤任务
  const getFilteredTasks = () => {
    switch (filter) {
      case 'pending':
        return tasks.filter(task => !task.completed);
      case 'completed':
        return tasks.filter(task => task.completed);
      default:
        return tasks;
    }
  };

  // 切换任务展开状态
  const toggleTaskExpanded = (taskId: string) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId);
    } else {
      newExpanded.add(taskId);
    }
    setExpandedTasks(newExpanded);
  };

  // 处理任务完成
  const handleTaskComplete = (task: HealthTask) => {
    if (task.completed) {
      Alert.alert('提示', '该任务已完成');
      return;
    }

    Alert.alert(
      '确认完成',
      `确定要标记"${task.title}"为已完成吗？`,
      [
        { text: '取消', style: 'cancel' },
        { 
          text: '确定', 
          onPress: () => onTaskComplete?.(task.id)
        }
      ]
    );
  };

  // 渲染任务项
  const renderTask = (task: HealthTask) => {
    const typeConfig = taskTypeConfig[task.type];
    const priorityColor = priorityConfig[task.priority].color;
    const isExpanded = expandedTasks.has(task.id);

    return (
      <Card key={task.id} style={[
        styles.taskCard,
        task.completed && styles.completedTaskCard
      ]}>
        <TouchableOpacity
          onPress={() => toggleTaskExpanded(task.id)}
          style={styles.taskHeader}
        >
          <View style={styles.taskHeaderLeft}>
            <Avatar.Icon
              size={40}
              icon={typeConfig.icon}
              style={[styles.taskIcon, { backgroundColor: typeConfig.color }]}
            />
            <View style={styles.taskInfo}>
              <Text style={[
                styles.taskTitle,
                task.completed && styles.completedTaskTitle
              ]}>
                {task.title}
              </Text>
              <View style={styles.taskMeta}>
                <Chip
                  icon="flag"
                  style={[styles.priorityChip, { backgroundColor: priorityColor + '20' }]}
                  textStyle={[styles.priorityText, { color: priorityColor }]}
                >
                  {priorityConfig[task.priority].label}
                </Chip>
                <Chip
                  icon="clock-outline"
                  style={styles.typeChip}
                  textStyle={styles.typeText}
                >
                  {typeConfig.label}
                </Chip>
                {task.dueTime && (
                  <Chip
                    icon="alarm"
                    style={styles.timeChip}
                    textStyle={styles.timeText}
                  >
                    {task.dueTime}
                  </Chip>
                )}
              </View>
            </View>
          </View>
          
          <View style={styles.taskHeaderRight}>
            <Checkbox
              status={task.completed ? 'checked' : 'unchecked'}
              onPress={() => handleTaskComplete(task)}
            />
            <Icon
              name={isExpanded ? 'chevron-up' : 'chevron-down'}
              size={24}
              color={theme.colors.onSurface}
            />
          </View>
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.taskDetails}>
            <Text style={styles.taskDescription}>{task.description}</Text>
            
            {/* 进度显示 */}
            {task.targetValue && (
              <View style={styles.progressContainer}>
                <View style={styles.progressHeader}>
                  <Text style={styles.progressLabel}>进度</Text>
                  <Text style={styles.progressValue}>
                    {task.currentValue || 0}/{task.targetValue} {task.unit}
                  </Text>
                </View>
                <ProgressBar
                  progress={(task.currentValue || 0) / task.targetValue}
                  color={typeConfig.color}
                  style={styles.progressBar}
                />
              </View>
            )}

            {/* 任务详情 */}
            <View style={styles.taskDetailsInfo}>
              <View style={styles.detailItem}>
                <Icon name="repeat" size={16} color={theme.colors.onSurface} />
                <Text style={styles.detailText}>
                  频率: {task.frequency === 'daily' ? '每日' : 
                         task.frequency === 'weekly' ? '每周' : '每月'}
                </Text>
              </View>
              
              {task.duration && (
                <View style={styles.detailItem}>
                  <Icon name="timer-outline" size={16} color={theme.colors.onSurface} />
                  <Text style={styles.detailText}>时长: {task.duration}分钟</Text>
                </View>
              )}
            </View>

            {/* 操作按钮 */}
            <View style={styles.taskActions}>
              <Button
                mode="outlined"
                onPress={() => onTaskEdit?.(task)}
                icon="pencil"
                style={styles.actionButton}
              >
                编辑
              </Button>
              {!task.completed && (
                <Button
                  mode="contained"
                  onPress={() => handleTaskComplete(task)}
                  icon="check"
                  style={styles.actionButton}
                >
                  完成
                </Button>
              )}
            </View>
          </View>
        )}
      </Card>
    );
  };

  // 渲染过滤器
  const renderFilter = () => (
    <View style={styles.filterContainer}>
      <Chip
        selected={filter === 'all'}
        onPress={() => setFilter('all')}
        style={styles.filterChip}
      >
        全部 ({tasks.length})
      </Chip>
      <Chip
        selected={filter === 'pending'}
        onPress={() => setFilter('pending')}
        style={styles.filterChip}
      >
        待完成 ({tasks.filter(t => !t.completed).length})
      </Chip>
      <Chip
        selected={filter === 'completed'}
        onPress={() => setFilter('completed')}
        style={styles.filterChip}
      >
        已完成 ({tasks.filter(t => t.completed).length})
      </Chip>
    </View>
  );

  const progress = calculateProgress();
  const filteredTasks = getFilteredTasks();

  return (
    <Surface style={styles.container}>
      {/* 计划头部 */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.title}>{title}</Text>
          {description && (
            <Text style={styles.description}>{description}</Text>
          )}
        </View>
        <Button
          mode="outlined"
          onPress={onPlanEdit}
          icon="pencil"
          style={styles.editButton}
        >
          编辑计划
        </Button>
      </View>

      {/* 进度概览 */}
      <Card style={styles.progressCard}>
        <Card.Content>
          <View style={styles.progressOverview}>
            <View style={styles.progressInfo}>
              <Text style={styles.progressTitle}>完成进度</Text>
              <Text style={styles.progressPercentage}>
                {Math.round(progress * 100)}%
              </Text>
            </View>
            <View style={styles.progressStats}>
              <Text style={styles.progressStat}>
                已完成: {tasks.filter(t => t.completed).length}
              </Text>
              <Text style={styles.progressStat}>
                总任务: {tasks.length}
              </Text>
            </View>
          </View>
          <ProgressBar
            progress={progress}
            color={theme.colors.primary}
            style={styles.overallProgressBar}
          />
        </Card.Content>
      </Card>

      {/* 过滤器 */}
      {renderFilter()}

      {/* 任务列表 */}
      <ScrollView style={styles.taskList} showsVerticalScrollIndicator={false}>
        {filteredTasks.length > 0 ? (
          filteredTasks.map(renderTask)
        ) : (
          <View style={styles.emptyContainer}>
            <Icon name="clipboard-check-outline" size={48} color={theme.colors.outline} />
            <Text style={styles.emptyText}>
              {filter === 'all' ? '暂无任务' : 
               filter === 'pending' ? '没有待完成的任务' : '没有已完成的任务'}
            </Text>
          </View>
        )}
      </ScrollView>
    </Surface>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    margin: 16,
    borderRadius: 12,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerLeft: {
    flex: 1,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  description: {
    fontSize: 14,
    opacity: 0.7,
    lineHeight: 20,
  },
  editButton: {
    marginLeft: 16,
  },
  progressCard: {
    margin: 16,
    elevation: 1,
  },
  progressOverview: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressInfo: {
    alignItems: 'flex-start',
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  progressPercentage: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  progressStats: {
    alignItems: 'flex-end',
  },
  progressStat: {
    fontSize: 12,
    opacity: 0.7,
  },
  overallProgressBar: {
    height: 8,
    borderRadius: 4,
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  filterChip: {
    marginRight: 8,
  },
  taskList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  taskCard: {
    marginBottom: 12,
    elevation: 1,
  },
  completedTaskCard: {
    opacity: 0.7,
  },
  taskHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  taskHeaderLeft: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskIcon: {
    marginRight: 12,
  },
  taskInfo: {
    flex: 1,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  completedTaskTitle: {
    textDecorationLine: 'line-through',
    opacity: 0.7,
  },
  taskMeta: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  priorityChip: {
    marginRight: 4,
    marginBottom: 4,
  },
  priorityText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  typeChip: {
    marginRight: 4,
    marginBottom: 4,
  },
  typeText: {
    fontSize: 10,
  },
  timeChip: {
    marginRight: 4,
    marginBottom: 4,
  },
  timeText: {
    fontSize: 10,
  },
  taskHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskDetails: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  taskDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 16,
    opacity: 0.8,
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  progressValue: {
    fontSize: 14,
    opacity: 0.7,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  taskDetailsInfo: {
    marginBottom: 16,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  detailText: {
    marginLeft: 8,
    fontSize: 14,
    opacity: 0.7,
  },
  taskActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  actionButton: {
    marginLeft: 8,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    opacity: 0.6,
  },
});

export default HealthPlan;