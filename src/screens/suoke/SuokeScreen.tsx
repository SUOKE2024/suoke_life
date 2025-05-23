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
  Avatar,
  Chip,
  ProgressBar,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');

const SuokeScreen = () => {
  const navigation = useNavigation<any>();
  const theme = useTheme();
  const { t } = useTranslation();

  // 健康评分
  const healthScore = {
    overall: 85,
    physical: 88,
    mental: 82,
    lifestyle: 86,
  };

  // 体质分析结果
  const constitutionAnalysis = {
    type: '平和质',
    description: '阴阳调和，脏腑功能正常，体质较好',
    characteristics: ['精力充沛', '睡眠良好', '食欲正常', '情绪稳定'],
    suggestions: ['保持规律作息', '适度运动', '均衡饮食', '心情愉悦'],
  };

  // 最近评估
  const recentAssessments = [
    {
      id: '1',
      title: '春季体质评估',
      date: '2024-03-15',
      score: 85,
      type: 'constitution',
      status: 'completed',
    },
    {
      id: '2',
      title: '睡眠质量分析',
      date: '2024-03-14',
      score: 78,
      type: 'sleep',
      status: 'completed',
    },
    {
      id: '3',
      title: '情绪健康评估',
      date: '2024-03-13',
      score: 82,
      type: 'emotion',
      status: 'completed',
    },
  ];

  // 推荐服务
  const recommendedServices = [
    {
      id: '1',
      title: '四诊合参',
      description: '中医传统诊断方法，全面了解身体状况',
      icon: 'medical-bag',
      color: '#FF5722',
      route: 'FourDiagnosisSystem',
    },
    {
      id: '2',
      title: '健康评估',
      description: '综合健康状况评估，制定个性化方案',
      icon: 'clipboard-check',
      color: '#2196F3',
      route: 'HealthAssessment',
    },
    {
      id: '3',
      title: '智能体咨询',
      description: '与AI健康顾问对话，获取专业建议',
      icon: 'robot',
      color: '#4CAF50',
      route: 'AgentSelection',
    },
    {
      id: '4',
      title: '数据分析',
      description: '健康数据可视化分析，洞察健康趋势',
      icon: 'chart-line',
      color: '#FF9800',
      route: 'HealthDataChart',
    },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#F44336';
  };

  const getScoreLevel = (score: number) => {
    if (score >= 90) return '优秀';
    if (score >= 80) return '良好';
    if (score >= 70) return '一般';
    if (score >= 60) return '需改善';
    return '较差';
  };

  const renderHealthScore = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>健康评分</Title>
        
        {/* 总体评分 */}
        <View style={styles.overallScore}>
          <View style={styles.scoreCircle}>
            <Text style={[styles.scoreNumber, { color: getScoreColor(healthScore.overall) }]}>
              {healthScore.overall}
            </Text>
            <Text style={styles.scoreLabel}>总分</Text>
          </View>
          <View style={styles.scoreInfo}>
            <Text style={styles.scoreLevel}>
              {getScoreLevel(healthScore.overall)}
            </Text>
            <Text style={styles.scoreDescription}>
              您的整体健康状况良好，继续保持！
            </Text>
          </View>
        </View>

        {/* 分项评分 */}
        <View style={styles.scoreDetails}>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreItemLabel}>身体健康</Text>
            <View style={styles.scoreItemBar}>
              <ProgressBar
                progress={healthScore.physical / 100}
                color={getScoreColor(healthScore.physical)}
                style={styles.progressBar}
              />
              <Text style={styles.scoreItemValue}>{healthScore.physical}</Text>
            </View>
          </View>
          
          <View style={styles.scoreItem}>
            <Text style={styles.scoreItemLabel}>心理健康</Text>
            <View style={styles.scoreItemBar}>
              <ProgressBar
                progress={healthScore.mental / 100}
                color={getScoreColor(healthScore.mental)}
                style={styles.progressBar}
              />
              <Text style={styles.scoreItemValue}>{healthScore.mental}</Text>
            </View>
          </View>
          
          <View style={styles.scoreItem}>
            <Text style={styles.scoreItemLabel}>生活方式</Text>
            <View style={styles.scoreItemBar}>
              <ProgressBar
                progress={healthScore.lifestyle / 100}
                color={getScoreColor(healthScore.lifestyle)}
                style={styles.progressBar}
              />
              <Text style={styles.scoreItemValue}>{healthScore.lifestyle}</Text>
            </View>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderConstitutionAnalysis = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>体质分析</Title>
        
        <View style={styles.constitutionHeader}>
          <Avatar.Text
            size={48}
            label={constitutionAnalysis.type.charAt(0)}
            style={{ backgroundColor: theme.colors.primary }}
          />
          <View style={styles.constitutionInfo}>
            <Text style={styles.constitutionType}>{constitutionAnalysis.type}</Text>
            <Text style={styles.constitutionDescription}>
              {constitutionAnalysis.description}
            </Text>
          </View>
        </View>

        <View style={styles.constitutionSection}>
          <Text style={styles.sectionTitle}>体质特征</Text>
          <View style={styles.tagsContainer}>
            {constitutionAnalysis.characteristics.map((item, index) => (
              <Chip
                key={index}
                style={styles.characteristicChip}
                textStyle={styles.chipText}
              >
                {item}
              </Chip>
            ))}
          </View>
        </View>

        <View style={styles.constitutionSection}>
          <Text style={styles.sectionTitle}>调理建议</Text>
          <View style={styles.tagsContainer}>
            {constitutionAnalysis.suggestions.map((item, index) => (
              <Chip
                key={index}
                mode="outlined"
                style={styles.suggestionChip}
                textStyle={styles.chipText}
              >
                {item}
              </Chip>
            ))}
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderRecentAssessments = () => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Title style={styles.cardTitle}>最近评估</Title>
          <Button
            mode="text"
            onPress={() => navigation.navigate('HealthAssessment')}
            compact
          >
            新建评估
          </Button>
        </View>
        
        {recentAssessments.map(assessment => (
          <View key={assessment.id} style={styles.assessmentItem}>
            <View style={styles.assessmentIcon}>
              <Icon
                name={assessment.type === 'constitution' ? 'human' : 
                      assessment.type === 'sleep' ? 'sleep' : 'emoticon-happy'}
                size={20}
                color={theme.colors.primary}
              />
            </View>
            <View style={styles.assessmentInfo}>
              <Text style={styles.assessmentTitle}>{assessment.title}</Text>
              <Text style={styles.assessmentDate}>{assessment.date}</Text>
            </View>
            <View style={styles.assessmentScore}>
              <Text style={[styles.scoreText, { color: getScoreColor(assessment.score) }]}>
                {assessment.score}
              </Text>
              <Text style={styles.scoreUnit}>分</Text>
            </View>
          </View>
        ))}
      </Card.Content>
    </Card>
  );

  const renderRecommendedServices = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>推荐服务</Title>
        <View style={styles.servicesGrid}>
          {recommendedServices.map(service => (
            <Surface
              key={service.id}
              style={styles.serviceCard}
              onTouchEnd={() => navigation.navigate(service.route)}
            >
              <View style={[styles.serviceIcon, { backgroundColor: service.color }]}>
                <Icon name={service.icon} size={24} color="white" />
              </View>
              <Text style={styles.serviceTitle}>{service.title}</Text>
              <Text style={styles.serviceDescription}>{service.description}</Text>
            </Surface>
          ))}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>索克健康</Title>
        <Text style={styles.headerSubtitle}>AI驱动的个性化健康管理</Text>
      </View>

      <ScrollView style={styles.content}>
        {renderHealthScore()}
        {renderConstitutionAnalysis()}
        {renderRecentAssessments()}
        {renderRecommendedServices()}
      </ScrollView>
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
  overallScore: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  scoreCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  scoreNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: 12,
    color: '#666',
  },
  scoreInfo: {
    flex: 1,
  },
  scoreLevel: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  scoreDescription: {
    fontSize: 14,
    color: '#666',
  },
  scoreDetails: {
    marginTop: 16,
  },
  scoreItem: {
    marginBottom: 12,
  },
  scoreItemLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
  },
  scoreItemBar: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBar: {
    flex: 1,
    height: 6,
    borderRadius: 3,
    marginRight: 12,
  },
  scoreItemValue: {
    fontSize: 14,
    fontWeight: 'bold',
    minWidth: 30,
    textAlign: 'right',
  },
  constitutionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  constitutionInfo: {
    flex: 1,
    marginLeft: 12,
  },
  constitutionType: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  constitutionDescription: {
    fontSize: 14,
    color: '#666',
  },
  constitutionSection: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  characteristicChip: {
    marginRight: 8,
    marginBottom: 8,
    backgroundColor: '#e3f2fd',
  },
  suggestionChip: {
    marginRight: 8,
    marginBottom: 8,
  },
  chipText: {
    fontSize: 12,
  },
  assessmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  assessmentIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  assessmentInfo: {
    flex: 1,
  },
  assessmentTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 2,
  },
  assessmentDate: {
    fontSize: 12,
    color: '#666',
  },
  assessmentScore: {
    alignItems: 'center',
  },
  scoreText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  scoreUnit: {
    fontSize: 10,
    color: '#666',
  },
  servicesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  serviceCard: {
    width: '48%',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  serviceIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  serviceTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 4,
    textAlign: 'center',
  },
  serviceDescription: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    lineHeight: 16,
  },
});

export default SuokeScreen;