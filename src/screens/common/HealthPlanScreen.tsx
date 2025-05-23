import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Appbar,
  Card,
  Title,
  Text,
  Button,
  FAB,
  Chip,
  ProgressBar,
  Checkbox,
  Surface,
  Menu,
  IconButton,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';

interface Task {
  id: string;
  title: string;
  description: string;
  type: 'exercise' | 'diet' | 'sleep' | 'medication' | 'checkup';
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
  dueDate: string;
  progress: number;
  target: string;
}

interface HealthPlanScreenProps {
  navigation?: any;
}

const HealthPlanScreen: React.FC<HealthPlanScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [menuVisible, setMenuVisible] = useState(false);

  // 模拟任务数据
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: '晨练',
      description: '公园快走30分钟',
      type: 'exercise',
      priority: 'high',
      completed: true,
      dueDate: '2024-03-15',
      progress: 100,
      target: '30分钟',
    },
    {
      id: '2',
      title: '饮水提醒',
      description: '每日饮水2000ml',
      type: 'diet',
      priority: 'medium',
      completed: false,
      dueDate: '2024-03-15',
      progress: 60,
      target: '2000ml',
    },
    {
      id: '3',
      title: '服用维生素',
      description: '餐后服用维生素D',
      type: 'medication',
      priority: 'high',
      completed: false,
      dueDate: '2024-03-15',
      progress: 0,
      target: '1粒',
    },
    {
      id: '4',
      title: '早睡',
      description: '晚上10点前入睡',
      type: 'sleep',
      priority: 'medium',
      completed: false,
      dueDate: '2024-03-15',
      progress: 0,
      target: '22:00前',
    },
    {
      id: '5',
      title: '体重测量',
      description: '记录今日体重',
      type: 'checkup',
      priority: 'low',
      completed: true,
      dueDate: '2024-03-15',
      progress: 100,
      target: '1次',
    },
  ]);

  const taskTypes = {
    exercise: { name: '运动', icon: 'run', color: '#4CAF50' },
    diet: { name: '饮食', icon: 'food-apple', color: '#FF9800' },
    sleep: { name: '睡眠', icon: 'sleep', color: '#9C27B0' },
    medication: { name: '用药', icon: 'pill', color: '#F44336' },
    checkup: { name: '检查', icon: 'medical-bag', color: '#2196F3' },
  };

  const priorityColors = {
    high: '#F44336',
    medium: '#FF9800',
    low: '#4CAF50',
  };

  const priorityLabels = {
    high: '高',
    medium: '中',
    low: '低',
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'pending') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  const completedCount = tasks.filter(task => task.completed).length;
  const totalCount = tasks.length;
  const completionRate = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  const toggleTaskCompletion = (taskId: string) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId
          ? { ...task, completed: !task.completed, progress: !task.completed ? 100 : 0 }
          : task
      )
    );
  };

  const deleteTask = (taskId: string) => {
    Alert.alert(
      '删除任务',
      '确定要删除这个任务吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: () => {
            setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
          },
        },
      ]
    );
  };

  const renderOverview = () => (
    <Card style={styles.overviewCard}>
      <Card.Content>
        <Title style={styles.cardTitle}>今日计划概览</Title>
        
        <View style={styles.overviewStats}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{completedCount}</Text>
            <Text style={styles.statLabel}>已完成</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{totalCount - completedCount}</Text>
            <Text style={styles.statLabel}>待完成</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{completionRate.toFixed(0)}%</Text>
            <Text style={styles.statLabel}>完成率</Text>
          </View>
        </View>

        <View style={styles.progressSection}>
          <Text style={styles.progressLabel}>整体进度</Text>
          <ProgressBar
            progress={completionRate / 100}
            color={theme.colors.primary}
            style={styles.progressBar}
          />
        </View>
      </Card.Content>
    </Card>
  );

  const renderFilters = () => (
    <View style={styles.filtersContainer}>
      <Chip
        selected={filter === 'all'}
        onPress={() => setFilter('all')}
        style={styles.filterChip}
      >
        全部 ({totalCount})
      </Chip>
      <Chip
        selected={filter === 'pending'}
        onPress={() => setFilter('pending')}
        style={styles.filterChip}
      >
        待完成 ({totalCount - completedCount})
      </Chip>
      <Chip
        selected={filter === 'completed'}
        onPress={() => setFilter('completed')}
        style={styles.filterChip}
      >
        已完成 ({completedCount})
      </Chip>
    </View>
  );

  const renderTaskItem = (task: Task) => {
    const taskType = taskTypes[task.type];
    
    return (
      <Card key={task.id} style={styles.taskCard}>
        <Card.Content>
          <View style={styles.taskHeader}>
            <View style={styles.taskInfo}>
              <View style={styles.taskTitleRow}>
                <Checkbox
                  status={task.completed ? 'checked' : 'unchecked'}
                  onPress={() => toggleTaskCompletion(task.id)}
                />
                <View style={[styles.taskIcon, { backgroundColor: taskType.color }]}>
                  <Icon name={taskType.icon} size={16} color="white" />
                </View>
                <Text style={[
                  styles.taskTitle,
                  task.completed && styles.completedTask
                ]}>
                  {task.title}
                </Text>
              </View>
              
              <Text style={styles.taskDescription}>{task.description}</Text>
              
              <View style={styles.taskMeta}>
                <Chip
                  style={[styles.priorityChip, { backgroundColor: priorityColors[task.priority] + '20' }]}
                  textStyle={{ color: priorityColors[task.priority], fontSize: 10 }}
                >
                  {priorityLabels[task.priority]}优先级
                </Chip>
                <Chip
                  style={styles.typeChip}
                  textStyle={{ fontSize: 10 }}
                >
                  {taskType.name}
                </Chip>
                <Text style={styles.targetText}>目标: {task.target}</Text>
              </View>
            </View>
            
            <IconButton
              icon="delete"
              size={20}
              onPress={() => deleteTask(task.id)}
            />
          </View>

          {!task.completed && task.progress > 0 && (
            <View style={styles.progressSection}>
              <Text style={styles.progressLabel}>进度: {task.progress}%</Text>
              <ProgressBar
                progress={task.progress / 100}
                color={taskType.color}
                style={styles.taskProgressBar}
              />
            </View>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderTaskList = () => (
    <View style={styles.taskList}>
      {filteredTasks.length > 0 ? (
        filteredTasks.map(renderTaskItem)
      ) : (
        <Surface style={styles.emptyState}>
          <Icon name="clipboard-check-outline" size={48} color={theme.colors.outline} />
          <Text style={styles.emptyText}>
            {filter === 'completed' ? '还没有完成的任务' : 
             filter === 'pending' ? '没有待完成的任务' : '还没有添加任务'}
          </Text>
        </Surface>
      )}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation?.goBack()} />
        <Appbar.Content title="健康计划" />
        <Menu
          visible={menuVisible}
          onDismiss={() => setMenuVisible(false)}
          anchor={
            <Appbar.Action
              icon="dots-vertical"
              onPress={() => setMenuVisible(true)}
            />
          }
        >
          <Menu.Item onPress={() => {}} title="导出计划" />
          <Menu.Item onPress={() => {}} title="计划模板" />
          <Menu.Item onPress={() => {}} title="设置提醒" />
        </Menu>
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {renderOverview()}
        {renderFilters()}
        {renderTaskList()}
      </ScrollView>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => {
          // 添加新任务的逻辑
          Alert.alert('添加任务', '此功能正在开发中...');
        }}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  overviewCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  overviewStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  progressSection: {
    marginTop: 8,
  },
  progressLabel: {
    fontSize: 14,
    marginBottom: 8,
    fontWeight: '500',
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  filtersContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  filterChip: {
    marginRight: 8,
  },
  taskList: {
    marginBottom: 80,
  },
  taskCard: {
    marginBottom: 12,
    borderRadius: 8,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  taskInfo: {
    flex: 1,
  },
  taskTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  taskIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
    marginRight: 12,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: '500',
    flex: 1,
  },
  completedTask: {
    textDecorationLine: 'line-through',
    color: '#666',
  },
  taskDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    marginLeft: 40,
  },
  taskMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 40,
    flexWrap: 'wrap',
  },
  priorityChip: {
    marginRight: 8,
    marginBottom: 4,
    height: 24,
  },
  typeChip: {
    marginRight: 8,
    marginBottom: 4,
    height: 24,
  },
  targetText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  taskProgressBar: {
    height: 4,
    borderRadius: 2,
    marginLeft: 40,
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
    borderRadius: 12,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default HealthPlanScreen;