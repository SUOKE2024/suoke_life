import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  Surface,
  FAB,
  Chip,
  ProgressBar,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');

const LifeScreen = () => {
  const navigation = useNavigation<any>();
  const theme = useTheme();
  const { t } = useTranslation();

  // 模拟今日数据
  const todayData = {
    steps: 8432,
    stepGoal: 10000,
    water: 1200,
    waterGoal: 2000,
    sleep: 7.5,
    sleepGoal: 8,
    calories: 1850,
    calorieGoal: 2200,
  };

  // 最近记录
  const recentRecords = [
    {
      id: '1',
      type: 'diet',
      title: '午餐',
      description: '蒸蛋羹、青菜、米饭',
      time: '12:30',
      icon: 'food-apple',
      color: '#FF9800',
    },
    {
      id: '2',
      type: 'exercise',
      title: '快走',
      description: '公园快走 30分钟',
      time: '07:00',
      icon: 'walk',
      color: '#4CAF50',
    },
    {
      id: '3',
      type: 'mood',
      title: '心情记录',
      description: '今天心情不错，工作顺利',
      time: '09:15',
      icon: 'emoticon-happy',
      color: '#E91E63',
    },
  ];

  // 健康指标
  const healthMetrics = [
    {
      title: '血压',
      value: '120/80',
      unit: 'mmHg',
      status: 'normal',
      icon: 'heart-pulse',
      color: '#4CAF50',
    },
    {
      title: '心率',
      value: '72',
      unit: 'bpm',
      status: 'normal',
      icon: 'heart',
      color: '#2196F3',
    },
    {
      title: 'BMI',
      value: '22.5',
      unit: '',
      status: 'normal',
      icon: 'scale-bathroom',
      color: '#FF9800',
    },
    {
      title: '体温',
      value: '36.5',
      unit: '°C',
      status: 'normal',
      icon: 'thermometer',
      color: '#9C27B0',
    },
  ];

  const getProgressColor = (current: number, goal: number) => {
    const percentage = current / goal;
    if (percentage >= 1) return '#4CAF50';
    if (percentage >= 0.7) return '#FF9800';
    return '#F44336';
  };

  const renderDailyProgress = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>今日进度</Title>
        
        {/* 步数 */}
        <View style={styles.progressItem}>
          <View style={styles.progressHeader}>
            <View style={styles.progressInfo}>
              <Icon name="walk" size={20} color={theme.colors.primary} />
              <Text style={styles.progressLabel}>步数</Text>
            </View>
            <Text style={styles.progressValue}>
              {todayData.steps.toLocaleString()} / {todayData.stepGoal.toLocaleString()}
            </Text>
          </View>
          <ProgressBar
            progress={todayData.steps / todayData.stepGoal}
            color={getProgressColor(todayData.steps, todayData.stepGoal)}
            style={styles.progressBar}
          />
        </View>

        {/* 饮水 */}
        <View style={styles.progressItem}>
          <View style={styles.progressHeader}>
            <View style={styles.progressInfo}>
              <Icon name="cup-water" size={20} color={theme.colors.primary} />
              <Text style={styles.progressLabel}>饮水</Text>
            </View>
            <Text style={styles.progressValue}>
              {todayData.water}ml / {todayData.waterGoal}ml
            </Text>
          </View>
          <ProgressBar
            progress={todayData.water / todayData.waterGoal}
            color={getProgressColor(todayData.water, todayData.waterGoal)}
            style={styles.progressBar}
          />
        </View>

        {/* 睡眠 */}
        <View style={styles.progressItem}>
          <View style={styles.progressHeader}>
            <View style={styles.progressInfo}>
              <Icon name="sleep" size={20} color={theme.colors.primary} />
              <Text style={styles.progressLabel}>睡眠</Text>
            </View>
            <Text style={styles.progressValue}>
              {todayData.sleep}h / {todayData.sleepGoal}h
            </Text>
          </View>
          <ProgressBar
            progress={todayData.sleep / todayData.sleepGoal}
            color={getProgressColor(todayData.sleep, todayData.sleepGoal)}
            style={styles.progressBar}
          />
        </View>

        {/* 卡路里 */}
        <View style={styles.progressItem}>
          <View style={styles.progressHeader}>
            <View style={styles.progressInfo}>
              <Icon name="fire" size={20} color={theme.colors.primary} />
              <Text style={styles.progressLabel}>卡路里</Text>
            </View>
            <Text style={styles.progressValue}>
              {todayData.calories} / {todayData.calorieGoal}
            </Text>
          </View>
          <ProgressBar
            progress={todayData.calories / todayData.calorieGoal}
            color={getProgressColor(todayData.calories, todayData.calorieGoal)}
            style={styles.progressBar}
          />
        </View>
      </Card.Content>
    </Card>
  );

  const renderHealthMetrics = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>健康指标</Title>
        <View style={styles.metricsGrid}>
          {healthMetrics.map((metric, index) => (
            <Surface key={index} style={styles.metricCard}>
              <View style={[styles.metricIcon, { backgroundColor: metric.color }]}>
                <Icon name={metric.icon} size={24} color="white" />
              </View>
              <Text style={styles.metricTitle}>{metric.title}</Text>
              <Text style={styles.metricValue}>
                {metric.value}
                <Text style={styles.metricUnit}>{metric.unit}</Text>
              </Text>
              <Chip
                style={[styles.statusChip, { backgroundColor: metric.color + '20' }]}
                textStyle={{ color: metric.color, fontSize: 10 }}
              >
                正常
              </Chip>
            </Surface>
          ))}
        </View>
      </Card.Content>
    </Card>
  );

  const renderRecentRecords = () => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Title style={styles.cardTitle}>最近记录</Title>
          <Button
            mode="text"
            onPress={() => navigation.navigate('LifeRecord')}
            compact
          >
            查看全部
          </Button>
        </View>
        
        {recentRecords.map(record => (
          <View key={record.id} style={styles.recordItem}>
            <View style={[styles.recordIcon, { backgroundColor: record.color }]}>
              <Icon name={record.icon} size={20} color="white" />
            </View>
            <View style={styles.recordInfo}>
              <Text style={styles.recordTitle}>{record.title}</Text>
              <Text style={styles.recordDescription}>{record.description}</Text>
            </View>
            <Text style={styles.recordTime}>{record.time}</Text>
          </View>
        ))}
      </Card.Content>
    </Card>
  );

  const renderQuickActions = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>快捷操作</Title>
        <View style={styles.actionsGrid}>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('LifeRecord')}
            style={styles.actionButton}
            icon="plus"
          >
            添加记录
          </Button>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('HealthDataChart')}
            style={styles.actionButton}
            icon="chart-line"
          >
            数据分析
          </Button>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('HealthPlan')}
            style={styles.actionButton}
            icon="calendar-check"
          >
            健康计划
          </Button>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('FourDiagnosisSystem')}
            style={styles.actionButton}
            icon="medical-bag"
          >
            四诊合参
          </Button>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>生活记录</Title>
        <Text style={styles.headerSubtitle}>记录健康生活的每一天</Text>
      </View>

      <ScrollView style={styles.content}>
        {renderDailyProgress()}
        {renderHealthMetrics()}
        {renderRecentRecords()}
        {renderQuickActions()}
      </ScrollView>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('LifeRecord')}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 16,
    paddingBottom: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginBottom: 16,
    borderRadius: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  progressItem: {
    marginBottom: 16,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressLabel: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
  },
  progressValue: {
    fontSize: 12,
    color: '#666',
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: '48%',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  metricIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  metricUnit: {
    fontSize: 12,
    fontWeight: 'normal',
    color: '#666',
  },
  statusChip: {
    height: 20,
  },
  recordItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  recordIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  recordInfo: {
    flex: 1,
  },
  recordTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 2,
  },
  recordDescription: {
    fontSize: 12,
    color: '#666',
  },
  recordTime: {
    fontSize: 12,
    color: '#666',
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    marginBottom: 8,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default LifeScreen;