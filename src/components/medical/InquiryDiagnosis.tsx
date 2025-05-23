import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Button, Divider, Avatar, Title, Paragraph, List, Chip, TextInput, Checkbox, Surface } from 'react-native-paper';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { inquiryService } from '../../services/diagnostic';

interface InquiryDiagnosisProps {
  onComplete: (results: any) => void;
  onCancel: () => void;
}

type SymptomCategory = {
  id: string;
  title: string;
  symptoms: {
    id: string;
    name: string;
    selected: boolean;
  }[];
};

const InquiryDiagnosis: React.FC<InquiryDiagnosisProps> = ({ onComplete, onCancel }) => {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [currentComplaints, setCurrentComplaints] = useState('');
  const [medicalHistory, setMedicalHistory] = useState('');
  const [familyHistory, setFamilyHistory] = useState('');
  const [lifestyleHabits, setLifestyleHabits] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [recommendedSymptoms, setRecommendedSymptoms] = useState<Array<{id: string, name: string}>>([]);
  const [isSearchingSymptoms, setIsSearchingSymptoms] = useState(false);
  
  // 问诊步骤
  const steps = [
    { title: '主诉', description: '描述当前的主要症状和不适' },
    { title: '症状选择', description: '选择存在的相关症状' },
    { title: '既往史和家族史', description: '记录过往病史和家族病史' },
    { title: '生活习惯', description: '记录生活习惯、饮食偏好等信息' }
  ];
  
  // 症状分类列表
  const [symptomCategories, setSymptomCategories] = useState<SymptomCategory[]>([
    {
      id: 'pain',
      title: '疼痛不适',
      symptoms: [
        { id: 'headache', name: '头痛', selected: false },
        { id: 'chestPain', name: '胸痛', selected: false },
        { id: 'abdominalPain', name: '腹痛', selected: false },
        { id: 'jointPain', name: '关节痛', selected: false },
        { id: 'backPain', name: '背痛', selected: false }
      ]
    },
    {
      id: 'digestion',
      title: '消化系统',
      symptoms: [
        { id: 'nausea', name: '恶心', selected: false },
        { id: 'vomiting', name: '呕吐', selected: false },
        { id: 'diarrhea', name: '腹泻', selected: false },
        { id: 'constipation', name: '便秘', selected: false },
        { id: 'poorAppetite', name: '食欲不振', selected: false },
        { id: 'bloating', name: '腹胀', selected: false }
      ]
    },
    {
      id: 'sleep',
      title: '睡眠情况',
      symptoms: [
        { id: 'insomnia', name: '失眠', selected: false },
        { id: 'drowsiness', name: '嗜睡', selected: false },
        { id: 'nightmares', name: '噩梦', selected: false },
        { id: 'sleepwalking', name: '梦游', selected: false }
      ]
    },
    {
      id: 'emotions',
      title: '情志状态',
      symptoms: [
        { id: 'anxiety', name: '焦虑', selected: false },
        { id: 'depression', name: '抑郁', selected: false },
        { id: 'irritability', name: '易怒', selected: false },
        { id: 'apathy', name: '淡漠', selected: false },
        { id: 'stress', name: '压力大', selected: false }
      ]
    },
    {
      id: 'energy',
      title: '气血情况',
      symptoms: [
        { id: 'fatigue', name: '疲劳', selected: false },
        { id: 'dizziness', name: '头晕', selected: false },
        { id: 'palpitations', name: '心悸', selected: false },
        { id: 'shortnessOfBreath', name: '气短', selected: false },
        { id: 'coldExtremities', name: '手脚冰凉', selected: false }
      ]
    }
  ]);

  // 根据主诉搜索推荐症状
  const searchSymptomRecommendations = async () => {
    if (!currentComplaints || currentComplaints.length < 3) return;
    
    setIsSearchingSymptoms(true);
    
    try {
      const response = await inquiryService.getSymptomRecommendations(currentComplaints);
      
      if (response.success && response.data.length > 0) {
        setRecommendedSymptoms(response.data);
      }
    } catch (error) {
      console.error('Error fetching symptom recommendations:', error);
    } finally {
      setIsSearchingSymptoms(false);
    }
  };
  
  // 处理推荐症状的添加
  const handleRecommendedSymptomAdd = (symptomId: string, symptomName: string) => {
    // 检查症状是否已存在于某个分类中
    let existingCategory = symptomCategories.find(category => 
      category.symptoms.some(s => s.id === symptomId)
    );
    
    if (existingCategory) {
      // 如果存在，只需标记为选中
      handleSymptomToggle(existingCategory.id, symptomId);
    } else {
      // 如果不存在，添加到"其他症状"分类
      let otherCategory = symptomCategories.find(c => c.id === 'other');
      
      if (!otherCategory) {
        // 如果没有"其他症状"分类，创建一个
        otherCategory = {
          id: 'other',
          title: '其他症状',
          symptoms: []
        };
        setSymptomCategories([...symptomCategories, otherCategory]);
      }
      
      // 添加新症状并标记为选中
      const newSymptom = { id: symptomId, name: symptomName, selected: true };
      const updatedCategories = symptomCategories.map(category => {
        if (category.id === 'other') {
          return {
            ...category,
            symptoms: [...category.symptoms, newSymptom]
          };
        }
        return category;
      });
      
      setSymptomCategories(updatedCategories);
      setSelectedSymptoms([...selectedSymptoms, symptomId]);
    }
  };
  
  // 处理症状选择
  const handleSymptomToggle = (categoryId: string, symptomId: string) => {
    const updatedCategories = symptomCategories.map(category => {
      if (category.id === categoryId) {
        const updatedSymptoms = category.symptoms.map(symptom => {
          if (symptom.id === symptomId) {
            const newSelectedState = !symptom.selected;
            
            // 更新selectedSymptoms列表
            if (newSelectedState) {
              if (!selectedSymptoms.includes(symptomId)) {
                setSelectedSymptoms([...selectedSymptoms, symptomId]);
              }
            } else {
              setSelectedSymptoms(selectedSymptoms.filter(id => id !== symptomId));
            }
            
            return { ...symptom, selected: newSelectedState };
          }
          return symptom;
        });
        return { ...category, symptoms: updatedSymptoms };
      }
      return category;
    });
    
    setSymptomCategories(updatedCategories);
  };
  
  // 提交问诊数据到后端
  const submitToApi = async () => {
    // 准备提交的数据
    const diagnosisData = {
      current_complaints: currentComplaints,
      selected_symptoms: getSelectedSymptomsWithNames(),
      medical_history: medicalHistory,
      family_history: familyHistory,
      lifestyle_habits: lifestyleHabits
    };
    
    setIsLoading(true);
    setApiError('');
    
    try {
      // 调用服务API
      const response = await inquiryService.submitDiagnosis(diagnosisData);
      
      if (response.success) {
        const finalResult = {
          ...diagnosisData,
          analysis: response.data.analysis || getAnalysisResults()
        };
        
        onComplete(finalResult);
      } else {
        setApiError(response.message || '分析失败，已使用本地分析结果');
        
        // 依然使用本地分析结果继续
        const fallbackResult = {
          ...diagnosisData,
          analysis: getAnalysisResults(),
          api_error: response.message
        };
        
        onComplete(fallbackResult);
      }
    } catch (error) {
      console.error('Inquiry diagnosis error:', error);
      setApiError('服务连接失败，已使用本地分析结果');
      
      // 使用本地分析结果作为备选
      const fallbackResult = {
        ...diagnosisData,
        analysis: getAnalysisResults(),
        api_error: '服务连接失败'
      };
      
      onComplete(fallbackResult);
    } finally {
      setIsLoading(false);
    }
  };
  
  // 下一步
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 完成所有步骤，提交API
      submitToApi();
    }
  };
  
  // 获取已选症状的详细信息
  const getSelectedSymptomsWithNames = () => {
    const result: { id: string; name: string; category: string }[] = [];
    
    symptomCategories.forEach(category => {
      category.symptoms.forEach(symptom => {
        if (symptom.selected) {
          result.push({
            id: symptom.id,
            name: symptom.name,
            category: category.title
          });
        }
      });
    });
    
    return result;
  };
  
  // 生成诊断分析结果
  const getAnalysisResults = () => {
    // 这里应该有更复杂的分析逻辑
    // 目前只是一个简单的演示
    
    let constitution = '气血两虚';
    let recommendation = '建议调理气血，注意休息';
    
    // 基于症状进行简单判断
    if (selectedSymptoms.includes('anxiety') || 
        selectedSymptoms.includes('irritability') ||
        selectedSymptoms.includes('insomnia')) {
      constitution = '肝郁气滞';
      recommendation = '建议疏肝理气，保持情绪稳定';
    } else if (selectedSymptoms.includes('diarrhea') || 
               selectedSymptoms.includes('poorAppetite') ||
               selectedSymptoms.includes('fatigue')) {
      constitution = '脾胃虚弱';
      recommendation = '建议健脾益气，调整饮食';
    } else if (selectedSymptoms.includes('coldExtremities') || 
               selectedSymptoms.includes('backPain') ||
               selectedSymptoms.includes('dizziness')) {
      constitution = '肾阳虚衰';
      recommendation = '建议温补肾阳，避免受寒';
    }
    
    return {
      constitution,
      recommendation
    };
  };
  
  // 上一步
  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      onCancel();
    }
  };
  
  // 检查当前步骤是否完成
  const isStepComplete = () => {
    switch (currentStep) {
      case 0:
        return currentComplaints.trim() !== '';
      case 1:
        return selectedSymptoms.length > 0;
      case 2:
        return true; // 既往史和家族史可以为空
      case 3:
        return true; // 生活习惯可以为空
      default:
        return false;
    }
  };
  
  // 渲染当前步骤内容
  const renderStepContent = () => {
    const step = steps[currentStep];
    
    return (
      <Card style={styles.stepCard}>
        <Card.Title
          title={step.title}
          subtitle={step.description}
          left={(props) => <Avatar.Icon {...props} icon="comment-question-outline" color="#fff" style={{ backgroundColor: theme.colors.primary }} />}
        />
        <Divider />
        <Card.Content style={styles.cardContent}>
          {currentStep === 0 && (
            <View>
              <TextInput
                label="当前主诉"
                value={currentComplaints}
                onChangeText={(text) => {
                  setCurrentComplaints(text);
                  // 当文本变化时，延迟搜索推荐症状
                  if (text.length >= 3) {
                    setTimeout(() => {
                      searchSymptomRecommendations();
                    }, 500);
                  }
                }}
                placeholder="请详细描述您目前的不适或症状"
                mode="outlined"
                multiline
                numberOfLines={6}
                style={styles.textInput}
              />
              
              {isSearchingSymptoms && (
                <Paragraph style={styles.hintText}>正在分析症状...</Paragraph>
              )}
              
              {recommendedSymptoms.length > 0 && (
                <View style={styles.recommendationsContainer}>
                  <Title style={styles.recommendationsTitle}>推荐的相关症状</Title>
                  <View style={styles.chipsContainer}>
                    {recommendedSymptoms.map(symptom => (
                      <Chip
                        key={symptom.id}
                        onPress={() => handleRecommendedSymptomAdd(symptom.id, symptom.name)}
                        style={styles.recommendationChip}
                        icon="plus"
                      >
                        {symptom.name}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}
              
              <Paragraph style={styles.hint}>
                请尽可能详细地描述症状，包括:
                <Text style={styles.boldText}> 持续时间、症状位置、严重程度、加重或缓解因素</Text>等。
              </Paragraph>
              
              <Button
                mode="outlined"
                icon="lightbulb-outline"
                onPress={searchSymptomRecommendations}
                style={styles.searchButton}
                loading={isSearchingSymptoms}
                disabled={currentComplaints.length < 3 || isSearchingSymptoms}
              >
                获取症状建议
              </Button>
            </View>
          )}
          
          {currentStep === 1 && (
            <View>
              <Paragraph style={styles.symptomInstruction}>
                请选择您目前存在的症状（可多选）:
              </Paragraph>
              
              {symptomCategories.map(category => (
                <View key={category.id} style={styles.categoryContainer}>
                  <Title style={styles.categoryTitle}>{category.title}</Title>
                  <Surface style={styles.symptomsGrid}>
                    {category.symptoms.map(symptom => (
                      <Chip
                        key={symptom.id}
                        selected={symptom.selected}
                        onPress={() => handleSymptomToggle(category.id, symptom.id)}
                        style={[
                          styles.symptomChip,
                          symptom.selected && { backgroundColor: theme.colors.primary }
                        ]}
                        textStyle={symptom.selected ? { color: 'white' } : undefined}
                      >
                        {symptom.name}
                      </Chip>
                    ))}
                  </Surface>
                </View>
              ))}
              
              {selectedSymptoms.length === 0 && (
                <Paragraph style={styles.warningText}>
                  请至少选择一个症状以继续。
                </Paragraph>
              )}
            </View>
          )}
          
          {currentStep === 2 && (
            <View>
              <TextInput
                label="既往病史"
                value={medicalHistory}
                onChangeText={setMedicalHistory}
                placeholder="例如: 高血压、糖尿病、手术史等"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
              
              <TextInput
                label="家族病史"
                value={familyHistory}
                onChangeText={setFamilyHistory}
                placeholder="例如: 父母或直系亲属的慢性疾病等"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
              
              <Paragraph style={styles.hint}>
                以上信息将帮助我们更全面地了解您的健康状况，请如实填写。
              </Paragraph>
            </View>
          )}
          
          {currentStep === 3 && (
            <View>
              <TextInput
                label="生活习惯"
                value={lifestyleHabits}
                onChangeText={setLifestyleHabits}
                placeholder="请描述您的饮食、睡眠、运动等习惯"
                mode="outlined"
                multiline
                numberOfLines={4}
                style={styles.textInput}
              />
              
              <Divider style={styles.divider} />
              
              <Title style={styles.analysisTitle}>症状分析</Title>
              
              {selectedSymptoms.length > 0 ? (
                <List.Section>
                  <List.Item
                    title="体质判断"
                    description={getAnalysisResults().constitution}
                    left={props => <List.Icon {...props} icon="account-cog" />}
                  />
                  <List.Item
                    title="建议"
                    description={getAnalysisResults().recommendation}
                    left={props => <List.Icon {...props} icon="notebook" />}
                  />
                  
                  {apiError ? (
                    <Chip icon="alert" style={styles.errorChip}>
                      {apiError}
                    </Chip>
                  ) : null}
                  
                  <Paragraph style={styles.noteText}>
                    注: 此分析仅基于问诊所提供的信息，最终诊断需结合四诊合参。
                  </Paragraph>
                </List.Section>
              ) : (
                <Paragraph style={styles.warningText}>
                  未选择任何症状，无法提供分析。
                </Paragraph>
              )}
            </View>
          )}
        </Card.Content>
        <Card.Actions style={styles.cardActions}>
          <Button 
            mode="outlined" 
            onPress={handlePrevious}
            icon="arrow-left"
          >
            {currentStep === 0 ? '取消' : '上一步'}
          </Button>
          <Button 
            mode="contained" 
            onPress={handleNext}
            icon={currentStep === steps.length - 1 ? "check" : "arrow-right"}
            disabled={!isStepComplete() || isLoading}
            loading={isLoading}
          >
            {currentStep === steps.length - 1 ? '完成' : '下一步'}
          </Button>
        </Card.Actions>
      </Card>
    );
  };
  
  // 渲染进度指示器
  const renderProgress = () => {
    return (
      <View style={styles.progressContainer}>
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            <View 
              style={[
                styles.progressStep, 
                { 
                  backgroundColor: index <= currentStep 
                    ? theme.colors.primary 
                    : theme.colors.backdrop 
                }
              ]}
            >
              <Text style={styles.progressStepText}>{index + 1}</Text>
            </View>
            {index < steps.length - 1 && (
              <View 
                style={[
                  styles.progressLine, 
                  { 
                    backgroundColor: index < currentStep 
                      ? theme.colors.primary 
                      : theme.colors.backdrop 
                  }
                ]} 
              />
            )}
          </React.Fragment>
        ))}
      </View>
    );
  };
  
  return (
    <ScrollView style={styles.container}>
      <Title style={styles.mainTitle}>问诊</Title>
      <Paragraph style={styles.description}>
        问诊是中医四诊之一，通过询问患者的症状、病史及生活习惯等，全面了解疾病的发生、发展和演变过程。
      </Paragraph>
      
      {renderProgress()}
      {renderStepContent()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16
  },
  mainTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8
  },
  description: {
    marginBottom: 24
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24
  },
  progressStep: {
    width: 30,
    height: 30,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center'
  },
  progressStepText: {
    color: 'white',
    fontWeight: 'bold'
  },
  progressLine: {
    flex: 1,
    height: 3,
    marginHorizontal: 8
  },
  stepCard: {
    marginBottom: 24
  },
  cardContent: {
    padding: 16
  },
  cardActions: {
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingBottom: 16
  },
  textInput: {
    marginBottom: 16
  },
  hint: {
    fontStyle: 'italic',
    opacity: 0.7,
    marginBottom: 16
  },
  boldText: {
    fontWeight: 'bold'
  },
  divider: {
    marginVertical: 16
  },
  symptomInstruction: {
    marginBottom: 16
  },
  categoryContainer: {
    marginBottom: 20
  },
  categoryTitle: {
    fontSize: 16,
    marginBottom: 8
  },
  symptomsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
    borderRadius: 8,
    elevation: 1
  },
  symptomChip: {
    margin: 4
  },
  warningText: {
    color: 'orange',
    fontStyle: 'italic',
    marginVertical: 8
  },
  analysisTitle: {
    fontSize: 18,
    marginVertical: 8
  },
  noteText: {
    fontStyle: 'italic',
    fontSize: 12,
    opacity: 0.7,
    marginTop: 16
  },
  recommendationsContainer: {
    marginVertical: 16
  },
  recommendationsTitle: {
    fontSize: 16,
    marginBottom: 8
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap'
  },
  recommendationChip: {
    margin: 4,
    backgroundColor: '#f0f8ff'
  },
  hintText: {
    fontStyle: 'italic',
    fontSize: 14,
    color: '#666'
  },
  searchButton: {
    marginTop: 8
  },
  errorChip: {
    marginTop: 8,
    backgroundColor: '#ffebee'
  }
});

export default InquiryDiagnosis; 