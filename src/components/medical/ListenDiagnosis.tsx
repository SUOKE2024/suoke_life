import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Button, Divider, Avatar, Title, Paragraph, List, Chip, RadioButton, TextInput } from 'react-native-paper';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { listenService } from '../../services/diagnostic';

interface ListenDiagnosisProps {
  onComplete: (results: any) => void;
  onCancel: () => void;
}

const ListenDiagnosis: React.FC<ListenDiagnosisProps> = ({ onComplete, onCancel }) => {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(0);
  const [breathSmell, setBreathSmell] = useState('');
  const [bodyOdor, setBodyOdor] = useState('');
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [selectedSmellIntensity, setSelectedSmellIntensity] = useState('medium');
  const [selectedSmellType, setSelectedSmellType] = useState<string[]>([]);
  const [voiceCharacteristics, setVoiceCharacteristics] = useState<string[]>([]);
  const [breathingPattern, setBreathingPattern] = useState('');
  const [coughSound, setCoughSound] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState('');
  const [isAnalyzingVoice, setIsAnalyzingVoice] = useState(false);
  const [voiceAnalysisResult, setVoiceAnalysisResult] = useState<any>(null);
  
  // 闻诊步骤
  const steps = [
    { title: '语音分析', description: '分析语音、呼吸和咳嗽特征' },
    { title: '气味特征', description: '记录体表、口气等气味特征' },
    { title: '分析结果', description: '闻诊综合分析' }
  ];
  
  // 气味类型选项
  const smellTypes = [
    { value: 'sour', label: '酸臭（肝病）' },
    { value: 'burnt', label: '焦糊（心病）' },
    { value: 'sweet', label: '甜腻（脾病）' },
    { value: 'rotten', label: '腐臭（肺病）' },
    { value: 'putrid', label: '腥臭（肾病）' }
  ];
  
  // 声音特征选项
  const voiceOptions = [
    { value: 'loud', label: '高亢有力（阳证）' },
    { value: 'weak', label: '低弱无力（阴证）' },
    { value: 'urgent', label: '急促（热证）' },
    { value: 'slow', label: '缓慢（寒证）' },
    { value: 'clear', label: '清晰（表证）' },
    { value: 'muffled', label: '含糊（里证）' }
  ];
  
  // 处理气味类型选择
  const handleSmellTypeToggle = (value: string) => {
    if (selectedSmellType.includes(value)) {
      setSelectedSmellType(selectedSmellType.filter(item => item !== value));
    } else {
      setSelectedSmellType([...selectedSmellType, value]);
    }
  };
  
  // 处理声音特征选择
  const handleVoiceToggle = (value: string) => {
    if (voiceCharacteristics.includes(value)) {
      setVoiceCharacteristics(voiceCharacteristics.filter(item => item !== value));
    } else {
      setVoiceCharacteristics([...voiceCharacteristics, value]);
    }
  };

  // 分析语音特征
  const analyzeVoice = async () => {
    // 模拟录音数据，实际应用中应该从麦克风获取
    const mockAudioData = "base64encodedaudiodata";
    
    setIsAnalyzingVoice(true);
    
    try {
      const response = await listenService.analyzeVoiceFeatures(mockAudioData);
      
      if (response.success) {
        setVoiceAnalysisResult(response.data);
        
        // 根据API返回的分析结果自动设置声音特征
        if (response.data.voice_features) {
          const detectedFeatures = response.data.voice_features.map((feature: any) => feature.name);
          setVoiceCharacteristics(detectedFeatures);
        }
      } else {
        console.error('Voice analysis failed:', response.message);
      }
    } catch (error) {
      console.error('Error analyzing voice:', error);
    } finally {
      setIsAnalyzingVoice(false);
    }
  };
  
  // 提交闻诊数据到API
  const submitToApi = async () => {
    // 准备提交的数据
    const diagnosisData = {
      voice_characteristics: voiceCharacteristics,
      breathing_pattern: breathingPattern,
      cough_sound: coughSound,
      breath_smell: breathSmell,
      body_odor: bodyOdor,
      smell_intensity: selectedSmellIntensity,
      smell_types: selectedSmellType,
      additional_notes: additionalNotes,
      voice_analysis: voiceAnalysisResult
    };
    
    setIsSubmitting(true);
    setApiError('');
    
    try {
      // 调用服务API
      const response = await listenService.submitDiagnosis(diagnosisData);
      
      // 处理API响应
      if (response.success) {
        // 成功响应，获取分析结果
        const finalResult = {
          ...diagnosisData,
          analysis: response.data.analysis || getAnalysisResults()
        };
        
        onComplete(finalResult);
      } else {
        // API调用成功但处理失败
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
      // API调用异常处理
      console.error('Listen diagnosis error:', error);
      setApiError('服务连接失败，已使用本地分析结果');
      
      // 使用本地分析结果作为备选
      const fallbackResult = {
        ...diagnosisData,
        analysis: getAnalysisResults(),
        api_error: '服务连接失败'
      };
      
      onComplete(fallbackResult);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // 下一步
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 最后一步，调用API提交数据
      submitToApi();
    }
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
        return voiceCharacteristics.length > 0 || breathingPattern !== '';
      case 1:
        return selectedSmellType.length > 0;
      case 2:
        return true; // 分析结果总是可完成
      default:
        return false;
    }
  };
  
  // 生成分析结果
  const getAnalysisResults = () => {
    // 这里应该有更复杂的分析逻辑
    // 目前只是一个简单的演示
    
    let constitution = '';
    let recommendation = '';
    
    // 基于声音特征分析
    if (voiceCharacteristics.includes('loud') || voiceCharacteristics.includes('urgent')) {
      constitution = '阳热证';
      recommendation = '建议清热泻火';
    } else if (voiceCharacteristics.includes('weak') || voiceCharacteristics.includes('slow')) {
      constitution = '阴寒证';
      recommendation = '建议温阳散寒';
    } else if (voiceCharacteristics.includes('clear')) {
      constitution = '表证';
      recommendation = '建议解表';
    } else if (voiceCharacteristics.includes('muffled')) {
      constitution = '里证';
      recommendation = '建议和解';
    }
    
    // 如果没有声音特征，则基于气味特征分析
    if (constitution === '') {
      if (selectedSmellType.includes('sour')) {
        constitution = '肝郁气滞';
        recommendation = '建议疏肝解郁';
      } else if (selectedSmellType.includes('burnt')) {
        constitution = '心火亢盛';
        recommendation = '建议清心泻火';
      } else if (selectedSmellType.includes('sweet')) {
        constitution = '脾虚湿盛';
        recommendation = '建议健脾化湿';
      } else if (selectedSmellType.includes('rotten')) {
        constitution = '肺热壅盛';
        recommendation = '建议清肺化痰';
      } else if (selectedSmellType.includes('putrid')) {
        constitution = '肾阴亏虚';
        recommendation = '建议滋肾固精';
      }
    }
    
    if (constitution === '') {
      constitution = '未定体质';
      recommendation = '需结合其他诊法确定';
    }
    
    return {
      constitution,
      recommendation
    };
  };
  
  // 渲染当前步骤内容
  const renderStepContent = () => {
    const step = steps[currentStep];
    
    return (
      <Card style={styles.stepCard}>
        <Card.Title
          title={step.title}
          subtitle={step.description}
          left={(props) => <Avatar.Icon {...props} icon="ear-hearing" color="#fff" style={{ backgroundColor: theme.colors.primary }} />}
        />
        <Divider />
        <Card.Content style={styles.cardContent}>
          {currentStep === 0 && (
            <View>
              <Title style={styles.sectionTitle}>声音特征分析</Title>
              <Paragraph style={styles.instruction}>
                请选择相符的声音特征（可多选）:
              </Paragraph>
              
              <Button 
                mode="contained" 
                icon="microphone" 
                onPress={analyzeVoice}
                loading={isAnalyzingVoice}
                disabled={isAnalyzingVoice}
                style={styles.voiceButton}
              >
                录制声音分析
              </Button>
              
              {voiceAnalysisResult && (
                <Card style={styles.analysisCard}>
                  <Card.Content>
                    <Title style={styles.cardTitle}>自动分析结果</Title>
                    <List.Item
                      title="语速"
                      description={`${voiceAnalysisResult.speech_rate || 'N/A'} 字/分钟`}
                      left={props => <List.Icon {...props} icon="speedometer" />}
                    />
                    <List.Item
                      title="音调"
                      description={`平均: ${voiceAnalysisResult.pitch_avg || 'N/A'} Hz, 范围: ${voiceAnalysisResult.pitch_range || 'N/A'} Hz`}
                      left={props => <List.Icon {...props} icon="tune" />}
                    />
                    <List.Item
                      title="声音稳定性"
                      description={`${(voiceAnalysisResult.voice_stability || 0) * 100}%`}
                      left={props => <List.Icon {...props} icon="waveform" />}
                    />
                  </Card.Content>
                </Card>
              )}
              
              <View style={styles.chipsContainer}>
                {voiceOptions.map((option) => (
                  <Chip
                    key={option.value}
                    selected={voiceCharacteristics.includes(option.value)}
                    onPress={() => handleVoiceToggle(option.value)}
                    style={[
                      styles.chip,
                      voiceCharacteristics.includes(option.value) && { backgroundColor: theme.colors.primary }
                    ]}
                    textStyle={voiceCharacteristics.includes(option.value) ? { color: 'white' } : undefined}
                  >
                    {option.label}
                  </Chip>
                ))}
              </View>
              
              <TextInput
                label="呼吸特征"
                value={breathingPattern}
                onChangeText={setBreathingPattern}
                placeholder="描述呼吸的频率、深度、是否有异常声音等"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
              
              <TextInput
                label="咳嗽声特征"
                value={coughSound}
                onChangeText={setCoughSound}
                placeholder="描述咳嗽声音的特征，如清脆、低沉、痰鸣等"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
            </View>
          )}
          
          {currentStep === 1 && (
            <View>
              <Title style={styles.sectionTitle}>气味特征分析</Title>
              
              <Text style={styles.sectionSubtitle}>气味强度:</Text>
              <RadioButton.Group
                onValueChange={value => setSelectedSmellIntensity(value)}
                value={selectedSmellIntensity}
              >
                <View style={styles.radioGroup}>
                  <RadioButton.Item label="轻微" value="light" />
                  <RadioButton.Item label="中等" value="medium" />
                  <RadioButton.Item label="强烈" value="strong" />
                </View>
              </RadioButton.Group>
              
              <Text style={styles.sectionSubtitle}>气味类型（可多选）:</Text>
              <View style={styles.chipsContainer}>
                {smellTypes.map((type) => (
                  <Chip
                    key={type.value}
                    selected={selectedSmellType.includes(type.value)}
                    onPress={() => handleSmellTypeToggle(type.value)}
                    style={[
                      styles.chip,
                      selectedSmellType.includes(type.value) && { backgroundColor: theme.colors.primary }
                    ]}
                    textStyle={selectedSmellType.includes(type.value) ? { color: 'white' } : undefined}
                  >
                    {type.label}
                  </Chip>
                ))}
              </View>
              
              <TextInput
                label="口气描述"
                value={breathSmell}
                onChangeText={setBreathSmell}
                placeholder="描述口气的特征"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
              
              <TextInput
                label="体表气味"
                value={bodyOdor}
                onChangeText={setBodyOdor}
                placeholder="描述体表、汗液等气味特征"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
              
              <TextInput
                label="补充说明"
                value={additionalNotes}
                onChangeText={setAdditionalNotes}
                placeholder="其他任何相关的气味观察"
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.textInput}
              />
            </View>
          )}
          
          {currentStep === 2 && (
            <View>
              <Title style={styles.sectionTitle}>闻诊分析结果</Title>
              
              {(voiceCharacteristics.length > 0 || selectedSmellType.length > 0) ? (
                <List.Section>
                  {voiceCharacteristics.length > 0 && (
                    <List.Item
                      title="声音分析"
                      description={voiceCharacteristics.map(v => 
                        voiceOptions.find(option => option.value === v)?.label).join(', ')}
                      left={props => <List.Icon {...props} icon="volume-high" />}
                    />
                  )}
                  
                  {breathingPattern && (
                    <List.Item
                      title="呼吸特征"
                      description={breathingPattern}
                      left={props => <List.Icon {...props} icon="lungs" />}
                    />
                  )}
                  
                  {selectedSmellType.length > 0 && (
                    <List.Item
                      title="气味特征"
                      description={selectedSmellType.map(s => 
                        smellTypes.find(type => type.value === s)?.label).join(', ')}
                      left={props => <List.Icon {...props} icon="scent" />}
                    />
                  )}
                  
                  <Divider style={styles.divider} />
                  
                  <List.Item
                    title="体质判断"
                    description={getAnalysisResults().constitution}
                    left={props => <List.Icon {...props} icon="account-cog" />}
                  />
                  
                  <List.Item
                    title="调理建议"
                    description={getAnalysisResults().recommendation}
                    left={props => <List.Icon {...props} icon="medical-bag" />}
                  />
                  
                  <Chip icon="information" style={styles.infoChip}>
                    闻诊结果应结合望、问、切三诊共同分析，形成完整诊断。
                  </Chip>
                  
                  {apiError ? (
                    <Chip icon="alert" style={styles.errorChip}>
                      {apiError}
                    </Chip>
                  ) : null}
                </List.Section>
              ) : (
                <Paragraph style={styles.warningText}>
                  未录入足够的声音或气味信息，无法提供分析结果。请返回前面的步骤录入更多数据。
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
            disabled={!isStepComplete() || isSubmitting}
            loading={isSubmitting}
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
      <Title style={styles.mainTitle}>闻诊</Title>
      <Paragraph style={styles.description}>
        闻诊是中医四诊之一，通过听声音和闻气味来观察异常，帮助诊断疾病病因及性质。
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
  sectionTitle: {
    fontSize: 18,
    marginBottom: 16
  },
  sectionSubtitle: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 8
  },
  instruction: {
    marginBottom: 16
  },
  radioGroup: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16
  },
  chip: {
    margin: 4
  },
  textInput: {
    marginVertical: 8
  },
  divider: {
    marginVertical: 16
  },
  warningText: {
    color: 'orange',
    fontStyle: 'italic',
    marginVertical: 8
  },
  infoChip: {
    marginTop: 16
  },
  errorChip: {
    marginTop: 8,
    backgroundColor: '#ffebee'
  },
  voiceButton: {
    marginBottom: 16
  },
  analysisCard: {
    marginBottom: 16
  },
  cardTitle: {
    fontSize: 16,
    marginBottom: 8
  }
});

export default ListenDiagnosis; 