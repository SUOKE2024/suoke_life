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
  Paragraph,
  Button,
  RadioButton,
  Checkbox,
  Text,
  ProgressBar,
  Surface,
  Divider,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';

interface HealthAssessmentScreenProps {
  navigation: any;
}

interface Question {
  id: string;
  type: 'single' | 'multiple' | 'scale';
  question: string;
  options: string[];
  category: string;
}

interface Answer {
  questionId: string;
  value: string | string[] | number;
}

const HealthAssessmentScreen: React.FC<HealthAssessmentScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);

  const questions: Question[] = [
    {
      id: '1',
      type: 'single',
      question: '您的年龄段是？',
      options: ['18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '65岁以上'],
      category: 'basic',
    },
    {
      id: '2',
      type: 'single',
      question: '您的性别是？',
      options: ['男', '女'],
      category: 'basic',
    },
    {
      id: '3',
      type: 'single',
      question: '您的睡眠质量如何？',
      options: ['很好，很少失眠', '一般，偶尔失眠', '较差，经常失眠', '很差，严重失眠'],
      category: 'lifestyle',
    },
    {
      id: '4',
      type: 'single',
      question: '您的运动频率是？',
      options: ['每天运动', '每周3-4次', '每周1-2次', '很少运动', '从不运动'],
      category: 'lifestyle',
    },
    {
      id: '5',
      type: 'multiple',
      question: '您经常出现以下哪些症状？（可多选）',
      options: ['头痛', '失眠', '疲劳', '消化不良', '腰酸背痛', '情绪低落', '记忆力下降'],
      category: 'symptoms',
    },
    {
      id: '6',
      type: 'single',
      question: '您的饮食习惯如何？',
      options: ['规律且营养均衡', '基本规律', '不太规律', '很不规律'],
      category: 'lifestyle',
    },
    {
      id: '7',
      type: 'scale',
      question: '您对自己当前健康状况的满意度是？（1-10分）',
      options: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
      category: 'satisfaction',
    },
    {
      id: '8',
      type: 'multiple',
      question: '您有以下哪些慢性疾病？（可多选）',
      options: ['高血压', '糖尿病', '高血脂', '心脏病', '关节炎', '胃病', '无慢性疾病'],
      category: 'medical',
    },
  ];

  const currentQuestion = questions[currentQuestionIndex];
  const progress = (currentQuestionIndex + 1) / questions.length;

  const handleAnswer = (value: string | string[] | number) => {
    const newAnswers = answers.filter(a => a.questionId !== currentQuestion.id);
    newAnswers.push({
      questionId: currentQuestion.id,
      value,
    });
    setAnswers(newAnswers);
  };

  const getCurrentAnswer = (): string | string[] | number | undefined => {
    const answer = answers.find(a => a.questionId === currentQuestion.id);
    return answer?.value;
  };

  const handleNext = () => {
    const currentAnswer = getCurrentAnswer();
    if (!currentAnswer || (Array.isArray(currentAnswer) && currentAnswer.length === 0)) {
      Alert.alert('提示', '请选择一个答案后继续');
      return;
    }

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      completeAssessment();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const completeAssessment = () => {
    setIsCompleted(true);
    // 这里可以调用API保存评估结果
    console.log('评估完成，答案：', answers);
  };

  const generateHealthReport = () => {
    // 基于答案生成健康报告
    const basicInfo = answers.filter(a => questions.find(q => q.id === a.questionId)?.category === 'basic');
    const lifestyleInfo = answers.filter(a => questions.find(q => q.id === a.questionId)?.category === 'lifestyle');
    const symptomsInfo = answers.filter(a => questions.find(q => q.id === a.questionId)?.category === 'symptoms');
    
    // 简单的评分逻辑
    let healthScore = 80; // 基础分数
    
    // 根据生活方式调整分数
    lifestyleInfo.forEach(answer => {
      const question = questions.find(q => q.id === answer.questionId);
      if (question?.id === '3') { // 睡眠质量
        const sleepIndex = question.options.indexOf(answer.value as string);
        healthScore -= sleepIndex * 5;
      }
      if (question?.id === '4') { // 运动频率
        const exerciseIndex = question.options.indexOf(answer.value as string);
        healthScore -= exerciseIndex * 3;
      }
    });

    // 根据症状调整分数
    const symptoms = symptomsInfo[0]?.value as string[] || [];
    healthScore -= symptoms.length * 3;

    return {
      score: Math.max(healthScore, 0),
      level: healthScore >= 80 ? '优秀' : healthScore >= 60 ? '良好' : healthScore >= 40 ? '一般' : '需要改善',
      recommendations: generateRecommendations(healthScore, symptoms),
    };
  };

  const generateRecommendations = (score: number, symptoms: string[]) => {
    const recommendations = [];
    
    if (score < 60) {
      recommendations.push('建议咨询专业医生，制定个性化健康改善计划');
    }
    
    if (symptoms.includes('失眠')) {
      recommendations.push('改善睡眠环境，建立规律作息时间');
    }
    
    if (symptoms.includes('疲劳')) {
      recommendations.push('增加适量运动，注意营养均衡');
    }
    
    if (symptoms.includes('消化不良')) {
      recommendations.push('调整饮食结构，少食多餐，避免油腻食物');
    }
    
    recommendations.push('定期进行健康检查');
    recommendations.push('保持积极乐观的心态');
    
    return recommendations;
  };

  const renderQuestion = () => {
    const currentAnswer = getCurrentAnswer();

    switch (currentQuestion.type) {
      case 'single':
        return (
          <RadioButton.Group
            onValueChange={handleAnswer}
            value={currentAnswer as string || ''}
          >
            {currentQuestion.options.map((option, index) => (
              <View key={index} style={styles.optionItem}>
                <RadioButton.Item
                  label={option}
                  value={option}
                  style={styles.radioItem}
                />
              </View>
            ))}
          </RadioButton.Group>
        );

      case 'multiple':
        const selectedOptions = (currentAnswer as string[]) || [];
        return (
          <View>
            {currentQuestion.options.map((option, index) => (
              <View key={index} style={styles.optionItem}>
                <Checkbox.Item
                  label={option}
                  status={selectedOptions.includes(option) ? 'checked' : 'unchecked'}
                  onPress={() => {
                    const newSelected = selectedOptions.includes(option)
                      ? selectedOptions.filter(item => item !== option)
                      : [...selectedOptions, option];
                    handleAnswer(newSelected);
                  }}
                  style={styles.checkboxItem}
                />
              </View>
            ))}
          </View>
        );

      case 'scale':
        return (
          <View style={styles.scaleContainer}>
            <View style={styles.scaleLabels}>
              <Text>1分（很不满意）</Text>
              <Text>10分（非常满意）</Text>
            </View>
            <View style={styles.scaleOptions}>
              {currentQuestion.options.map((option, index) => (
                <Button
                  key={index}
                  mode={currentAnswer === option ? 'contained' : 'outlined'}
                  onPress={() => handleAnswer(option)}
                  style={styles.scaleButton}
                  compact
                >
                  {option}
                </Button>
              ))}
            </View>
          </View>
        );

      default:
        return null;
    }
  };

  const renderResults = () => {
    const report = generateHealthReport();
    
    return (
      <ScrollView style={styles.resultsContainer}>
        <Card style={styles.resultCard}>
          <Card.Content>
            <View style={styles.scoreContainer}>
              <Icon 
                name="heart-pulse" 
                size={48} 
                color={report.score >= 80 ? '#4CAF50' : report.score >= 60 ? '#FF9800' : '#F44336'} 
              />
              <Title style={styles.scoreTitle}>健康评分</Title>
              <Text style={[styles.scoreText, { color: report.score >= 80 ? '#4CAF50' : report.score >= 60 ? '#FF9800' : '#F44336' }]}>
                {report.score}分
              </Text>
              <Text style={styles.levelText}>{report.level}</Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.recommendationCard}>
          <Card.Content>
            <Title style={styles.sectionTitle}>健康建议</Title>
            {report.recommendations.map((recommendation, index) => (
              <View key={index} style={styles.recommendationItem}>
                <Icon name="check-circle" size={16} color={theme.colors.primary} />
                <Text style={styles.recommendationText}>{recommendation}</Text>
              </View>
            ))}
          </Card.Content>
        </Card>

        <View style={styles.actionButtons}>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('HealthPlan')}
            style={styles.actionButton}
            icon="calendar-check"
          >
            制定健康计划
          </Button>
          <Button
            mode="outlined"
            onPress={() => {
              setCurrentQuestionIndex(0);
              setAnswers([]);
              setIsCompleted(false);
            }}
            style={styles.actionButton}
            icon="refresh"
          >
            重新评估
          </Button>
        </View>
      </ScrollView>
    );
  };

  if (isCompleted) {
    return (
      <SafeAreaView style={styles.container}>
        <Appbar.Header>
          <Appbar.BackAction onPress={() => navigation.goBack()} />
          <Appbar.Content title="评估结果" />
        </Appbar.Header>
        {renderResults()}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="健康评估" />
      </Appbar.Header>

      <View style={styles.content}>
        {/* 进度条 */}
        <Surface style={styles.progressContainer}>
          <View style={styles.progressHeader}>
            <Text style={styles.progressText}>
              问题 {currentQuestionIndex + 1} / {questions.length}
            </Text>
            <Text style={styles.progressPercentage}>
              {Math.round(progress * 100)}%
            </Text>
          </View>
          <ProgressBar progress={progress} style={styles.progressBar} />
        </Surface>

        {/* 问题卡片 */}
        <Card style={styles.questionCard}>
          <Card.Content>
            <Title style={styles.questionTitle}>{currentQuestion.question}</Title>
            <Divider style={styles.divider} />
            {renderQuestion()}
          </Card.Content>
        </Card>

        {/* 导航按钮 */}
        <View style={styles.navigationButtons}>
          <Button
            mode="outlined"
            onPress={handlePrevious}
            disabled={currentQuestionIndex === 0}
            style={styles.navButton}
          >
            上一题
          </Button>
          <Button
            mode="contained"
            onPress={handleNext}
            style={styles.navButton}
          >
            {currentQuestionIndex === questions.length - 1 ? '完成评估' : '下一题'}
          </Button>
        </View>
      </View>
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
  progressContainer: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '500',
  },
  progressPercentage: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  questionCard: {
    flex: 1,
    borderRadius: 12,
    marginBottom: 16,
  },
  questionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    lineHeight: 24,
  },
  divider: {
    marginBottom: 16,
  },
  optionItem: {
    marginBottom: 8,
  },
  radioItem: {
    paddingVertical: 4,
  },
  checkboxItem: {
    paddingVertical: 4,
  },
  scaleContainer: {
    alignItems: 'center',
  },
  scaleLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 16,
  },
  scaleOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 8,
  },
  scaleButton: {
    minWidth: 40,
    margin: 2,
  },
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 16,
  },
  navButton: {
    flex: 1,
  },
  resultsContainer: {
    flex: 1,
    padding: 16,
  },
  resultCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  scoreContainer: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  scoreTitle: {
    fontSize: 18,
    marginTop: 8,
    marginBottom: 4,
  },
  scoreText: {
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  levelText: {
    fontSize: 16,
    fontWeight: '500',
  },
  recommendationCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  recommendationText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    lineHeight: 20,
  },
  actionButtons: {
    gap: 12,
  },
  actionButton: {
    marginBottom: 8,
  },
});

export default HealthAssessmentScreen;