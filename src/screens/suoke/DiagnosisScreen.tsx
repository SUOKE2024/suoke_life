import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Button, Card, Chip, SegmentedButtons, Title, Paragraph, List, Divider, Surface, ActivityIndicator } from 'react-native-paper';
import { useTheme } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// 导入四诊组件
import LookDiagnosis from '../../components/medical/LookDiagnosis';
import ListenDiagnosis from '../../components/medical/ListenDiagnosis';
import InquiryDiagnosis from '../../components/medical/InquiryDiagnosis';
import PalpationDiagnosis from '../../components/medical/PalpationDiagnosis';

// 导入诊断服务
import { diagnosisService } from '../../services/diagnostic';

// 导入LookDiagnosis的结果类型
interface LookDiagnosisResults {
  face?: any;
  tongue?: any;
  eyes?: any;
}

// 类型定义
interface DiagnosisResult {
  analysis?: {
    constitution: string;
    recommendation: string;
  };
}

interface DiagnosisResults {
  look: LookDiagnosisResults | DiagnosisResult | null;
  listen: DiagnosisResult | null;
  inquiry: DiagnosisResult | null;
  palpation: DiagnosisResult | null;
}

const DiagnosisScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const [activeTab, setActiveTab] = useState('intro');
  const [diagnosisResults, setDiagnosisResults] = useState<DiagnosisResults>({
    look: null,
    listen: null,
    inquiry: null,
    palpation: null
  });
  const [integratedAnalysis, setIntegratedAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  
  // 当诊断结果变化时，尝试获取综合分析
  useEffect(() => {
    const completedCount = getCompletedDiagnosisCount();
    
    // 如果有至少一个诊断结果，并且当前在结果页面，则获取综合分析
    if (completedCount > 0 && activeTab === 'summary') {
      fetchIntegratedAnalysis();
    }
  }, [diagnosisResults, activeTab]);
  
  // 从后端获取综合分析
  const fetchIntegratedAnalysis = async () => {
    // 如果已经在分析中，则不重复请求
    if (isAnalyzing) return;
    
    setIsAnalyzing(true);
    setAnalysisError('');
    
    try {
      const response = await diagnosisService.submitDiagnosis(diagnosisResults);
      
      if (response.success) {
        setIntegratedAnalysis(response.data);
      } else {
        setAnalysisError(response.message || '无法获取综合分析结果');
        // 仍然使用本地分析作为备选
        setIntegratedAnalysis(getFallbackAnalysis());
      }
    } catch (error) {
      console.error('Error fetching integrated analysis:', error);
      setAnalysisError('服务连接失败');
      // 使用本地分析作为备选
      setIntegratedAnalysis(getFallbackAnalysis());
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  // 获取本地备选分析结果
  const getFallbackAnalysis = () => {
    // 在实际应用中，这应该是一个复杂的分析算法
    // 这里只是一个简单的示例
    
    let constitutionTypes = [];
    let recommendations = [];
    
    if (diagnosisResults.look && 'analysis' in diagnosisResults.look && diagnosisResults.look.analysis) {
      constitutionTypes.push(diagnosisResults.look.analysis.constitution);
      recommendations.push(diagnosisResults.look.analysis.recommendation);
    }
    
    if (diagnosisResults.listen && diagnosisResults.listen.analysis) {
      constitutionTypes.push(diagnosisResults.listen.analysis.constitution);
      recommendations.push(diagnosisResults.listen.analysis.recommendation);
    }
    
    if (diagnosisResults.inquiry && diagnosisResults.inquiry.analysis) {
      constitutionTypes.push(diagnosisResults.inquiry.analysis.constitution);
      recommendations.push(diagnosisResults.inquiry.analysis.recommendation);
    }
    
    if (diagnosisResults.palpation && diagnosisResults.palpation.analysis) {
      constitutionTypes.push(diagnosisResults.palpation.analysis.constitution);
      recommendations.push(diagnosisResults.palpation.analysis.recommendation);
    }
    
    // 获取最常出现的体质类型，在这里简化为取最后一个
    const constitution = constitutionTypes.length > 0 
      ? constitutionTypes[constitutionTypes.length - 1] 
      : '未定体质';
    
    return {
      constitution,
      recommendations,
      is_fallback: true
    };
  };
  
  // 处理诊断结果提交
  const handleDiagnosisComplete = (type: keyof DiagnosisResults, results: any) => {
    setDiagnosisResults({
      ...diagnosisResults,
      [type]: results
    });
    setActiveTab('summary');
  };
  
  // 取消诊断
  const handleDiagnosisCancel = () => {
    setActiveTab('intro');
  };
  
  // 获取已完成的诊断数量
  const getCompletedDiagnosisCount = () => {
    return Object.values(diagnosisResults).filter(result => result !== null).length;
  };
  
  // 渲染简介
  const renderIntro = () => {
    return (
      <ScrollView style={styles.container}>
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.title}>中医四诊</Title>
            <Paragraph style={styles.paragraph}>
              中医四诊是指望、闻、问、切四种诊断方法，是中医诊断疾病的基本手段，通过这四种方法全面收集病情资料，为辨证论治提供依据。
            </Paragraph>
            
            <Surface style={styles.surface}>
              <List.Item
                title="望诊"
                description="通过观察患者的精神状态、面色、舌象等，了解疾病的表现。"
                left={props => <List.Icon {...props} icon="eye" color={theme.colors.primary} />}
              />
              <Divider />
              <List.Item
                title="闻诊"
                description="通过听患者的声音、呼吸和嗅闻其气味，判断疾病的性质。"
                left={props => <List.Icon {...props} icon="ear-hearing" color={theme.colors.primary} />}
              />
              <Divider />
              <List.Item
                title="问诊"
                description="通过询问患者的症状、病史、生活习惯等，了解疾病的发展过程。"
                left={props => <List.Icon {...props} icon="comment-question" color={theme.colors.primary} />}
              />
              <Divider />
              <List.Item
                title="切诊"
                description="通过触摸患者的脉搏、腹部等，判断内脏功能和疾病状态。"
                left={props => <List.Icon {...props} icon="hand" color={theme.colors.primary} />}
              />
            </Surface>
            
            <Paragraph style={styles.paragraph}>
              通过四诊合参，收集全面的症状和体征，可以更准确地判断疾病的性质、部位和病因，指导治疗方案的制定。
            </Paragraph>
            
            <Title style={styles.subtitle}>开始四诊</Title>
            <Paragraph>
              请选择您想要进行的诊断方法：
            </Paragraph>
            
            <View style={styles.buttonContainer}>
              <Button 
                mode="contained" 
                icon="eye" 
                style={styles.button}
                onPress={() => setActiveTab('look')}
              >
                望诊
              </Button>
              <Button 
                mode="contained" 
                icon="ear-hearing" 
                style={styles.button}
                onPress={() => setActiveTab('listen')}
              >
                闻诊
              </Button>
              <Button 
                mode="contained" 
                icon="comment-question" 
                style={styles.button}
                onPress={() => setActiveTab('inquiry')}
              >
                问诊
              </Button>
              <Button 
                mode="contained" 
                icon="hand" 
                style={styles.button}
                onPress={() => setActiveTab('palpation')}
              >
                切诊
              </Button>
            </View>
            
            {getCompletedDiagnosisCount() > 0 && (
              <Button 
                mode="contained" 
                icon="clipboard-text" 
                style={[styles.summaryButton, { backgroundColor: theme.colors.secondary }]}
                onPress={() => setActiveTab('summary')}
              >
                查看综合结果 ({getCompletedDiagnosisCount()}/4)
              </Button>
            )}
          </Card.Content>
        </Card>
      </ScrollView>
    );
  };
  
  // 渲染结果摘要
  const renderSummary = () => {
    // 组合所有诊断结果
    const hasAnyResults = getCompletedDiagnosisCount() > 0;
    
    return (
      <ScrollView style={styles.container}>
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.title}>四诊合参结果</Title>
            
            <Surface style={styles.statusSurface}>
              <Text style={styles.statusText}>已完成: {getCompletedDiagnosisCount()}/4 诊断</Text>
              <View style={styles.progressContainer}>
                <View style={styles.progressItem}>
                  <Icon 
                    name="eye" 
                    size={24} 
                    color={diagnosisResults.look ? theme.colors.primary : theme.colors.backdrop}
                  />
                  <Text style={diagnosisResults.look ? styles.completedText : styles.incompleteText}>
                    望诊
                  </Text>
                </View>
                <View style={styles.progressItem}>
                  <Icon 
                    name="ear-hearing" 
                    size={24} 
                    color={diagnosisResults.listen ? theme.colors.primary : theme.colors.backdrop}
                  />
                  <Text style={diagnosisResults.listen ? styles.completedText : styles.incompleteText}>
                    闻诊
                  </Text>
                </View>
                <View style={styles.progressItem}>
                  <Icon 
                    name="comment-question" 
                    size={24} 
                    color={diagnosisResults.inquiry ? theme.colors.primary : theme.colors.backdrop}
                  />
                  <Text style={diagnosisResults.inquiry ? styles.completedText : styles.incompleteText}>
                    问诊
                  </Text>
                </View>
                <View style={styles.progressItem}>
                  <Icon 
                    name="hand" 
                    size={24} 
                    color={diagnosisResults.palpation ? theme.colors.primary : theme.colors.backdrop}
                  />
                  <Text style={diagnosisResults.palpation ? styles.completedText : styles.incompleteText}>
                    切诊
                  </Text>
                </View>
              </View>
            </Surface>
            
            {hasAnyResults ? (
              <View style={styles.resultsContainer}>
                <Title style={styles.subtitle}>综合分析</Title>
                
                {isAnalyzing ? (
                  <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={theme.colors.primary} />
                    <Text style={styles.loadingText}>正在综合分析四诊结果...</Text>
                  </View>
                ) : integratedAnalysis ? (
                  <View>
                    <List.Item
                      title="体质辨识"
                      description={integratedAnalysis.constitution}
                      left={props => <List.Icon {...props} icon="account-check" color={theme.colors.primary} />}
                    />
                    
                    <Title style={styles.subtitleSmall}>调理建议</Title>
                    {integratedAnalysis.recommendations.map((recommendation: string, index: number) => (
                      <Chip key={index} icon="lightbulb" style={styles.recommendationChip}>
                        {recommendation}
                      </Chip>
                    ))}
                    
                    {analysisError ? (
                      <Chip icon="alert" style={styles.errorChip}>
                        {analysisError}
                      </Chip>
                    ) : null}
                    
                    <Paragraph style={styles.note}>
                      注：以上分析基于您提供的信息。如有健康问题，请咨询专业中医师进行面诊。
                    </Paragraph>
                  </View>
                ) : (
                  <Paragraph style={styles.warningText}>
                    您尚未完成足够的诊断，无法生成综合分析结果。请至少完成一项诊断。
                  </Paragraph>
                )}
                
                <Divider style={styles.divider} />
                
                <View style={styles.buttonRow}>
                  {!diagnosisResults.look && (
                    <Button 
                      mode="outlined" 
                      icon="eye" 
                      style={styles.actionButton}
                      onPress={() => setActiveTab('look')}
                    >
                      进行望诊
                    </Button>
                  )}
                  
                  {!diagnosisResults.listen && (
                    <Button 
                      mode="outlined" 
                      icon="ear-hearing" 
                      style={styles.actionButton}
                      onPress={() => setActiveTab('listen')}
                    >
                      进行闻诊
                    </Button>
                  )}
                </View>
                
                <View style={styles.buttonRow}>
                  {!diagnosisResults.inquiry && (
                    <Button 
                      mode="outlined" 
                      icon="comment-question" 
                      style={styles.actionButton}
                      onPress={() => setActiveTab('inquiry')}
                    >
                      进行问诊
                    </Button>
                  )}
                  
                  {!diagnosisResults.palpation && (
                    <Button 
                      mode="outlined" 
                      icon="hand" 
                      style={styles.actionButton}
                      onPress={() => setActiveTab('palpation')}
                    >
                      进行切诊
                    </Button>
                  )}
                </View>
              </View>
            ) : (
              <View style={styles.noResultsContainer}>
                <Icon name="alert-circle-outline" size={48} color={theme.colors.error} />
                <Paragraph style={styles.warningText}>
                  您尚未完成任何诊断。请返回选择至少一种诊断方法。
                </Paragraph>
                <Button 
                  mode="contained" 
                  icon="arrow-left" 
                  onPress={() => setActiveTab('intro')}
                >
                  返回选择
                </Button>
              </View>
            )}
          </Card.Content>
        </Card>
      </ScrollView>
    );
  };
  
  // 根据当前选项卡渲染内容
  const renderContent = () => {
    switch (activeTab) {
      case 'look':
        return <LookDiagnosis onComplete={(results) => handleDiagnosisComplete('look', results)} onCancel={handleDiagnosisCancel} />;
      case 'listen':
        return <ListenDiagnosis onComplete={(results) => handleDiagnosisComplete('listen', results)} onCancel={handleDiagnosisCancel} />;
      case 'inquiry':
        return <InquiryDiagnosis onComplete={(results) => handleDiagnosisComplete('inquiry', results)} onCancel={handleDiagnosisCancel} />;
      case 'palpation':
        return <PalpationDiagnosis onComplete={(results) => handleDiagnosisComplete('palpation', results)} onCancel={handleDiagnosisCancel} />;
      case 'summary':
        return renderSummary();
      case 'intro':
      default:
        return renderIntro();
    }
  };
  
  return (
    <View style={styles.screenContainer}>
      {activeTab !== 'intro' && activeTab !== 'summary' && (
        <Button 
          icon="arrow-left" 
          onPress={() => setActiveTab('intro')}
          style={styles.backButton}
        >
          返回
        </Button>
      )}
      {renderContent()}
    </View>
  );
};

const styles = StyleSheet.create({
  screenContainer: {
    flex: 1
  },
  container: {
    flex: 1,
    padding: 16
  },
  card: {
    marginBottom: 16
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16
  },
  subtitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 24,
    marginBottom: 8
  },
  subtitleSmall: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 8
  },
  paragraph: {
    marginBottom: 16,
    fontSize: 16,
    lineHeight: 24
  },
  surface: {
    marginVertical: 16,
    elevation: 1,
    borderRadius: 8
  },
  buttonContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 16
  },
  button: {
    width: '48%',
    marginBottom: 16
  },
  summaryButton: {
    marginTop: 8
  },
  backButton: {
    margin: 8,
    alignSelf: 'flex-start'
  },
  statusSurface: {
    padding: 16,
    borderRadius: 8,
    marginVertical: 16,
    elevation: 1
  },
  statusText: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8
  },
  progressItem: {
    alignItems: 'center',
    flex: 1
  },
  completedText: {
    color: '#000',
    marginTop: 4
  },
  incompleteText: {
    color: '#888',
    marginTop: 4
  },
  resultsContainer: {
    marginVertical: 16
  },
  noResultsContainer: {
    alignItems: 'center',
    padding: 24
  },
  warningText: {
    fontStyle: 'italic',
    color: 'orange',
    textAlign: 'center',
    marginVertical: 16
  },
  note: {
    fontStyle: 'italic',
    fontSize: 12,
    marginTop: 16
  },
  recommendationChip: {
    marginVertical: 4
  },
  divider: {
    marginVertical: 16
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  actionButton: {
    flex: 1,
    marginHorizontal: 4
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666'
  },
  errorChip: {
    marginTop: 8,
    backgroundColor: '#ffebee'
  }
});

export default DiagnosisScreen;