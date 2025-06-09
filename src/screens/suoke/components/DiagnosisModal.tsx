import { SafeAreaView } from "react-native-safe-area-context";
import { usePerformanceMonitor } from "../hooks/usePerformanceMonitor/      View,";
import React from "react";
import Icon from "../../../components/common/Icon";
import { colors, spacing } from ../../../constants/theme"/import { useAppDispatch, useAppSelector } from "../../../store/import { DiagnosisType  } from ;../../../types";// "
import React,{ useState, useEffect } from react""
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Image,
  { TextInput } from ";react-native";
  startDiagnosisSession,
  submitDiagnosisData,
  completeDiagnosisSession,
  uploadTongueImage,
  recordVoiceData,
  selectDiagnosisLoading,
  { selectCurrentSession } from ../../../store/slices/diagnosisSlice";/    interface DiagnosisModalProps {
  visible: boolean,"
  onClose: () => void;,
  diagnosisType: DiagnosisType;,
  title: string;,
  description: string;
}
interface DiagnosisStep {
  id: string;,
  title: string;,
  description: string;,
  completed: boolean;
data?: unknown;
}
export const DiagnosisModal: React.FC<DiagnosisModalProps /> = ({/   const performanceMonitor = usePerformanceMonitor("DiagnosisModal, ";))
{/
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50});
  visible,
  onClose,
  diagnosisType,
  title,
  description;
}) => {}
  const dispatch = useMemo() => useAppDispatch(), []);)))));
  const loading = useMemo() => useAppSelector(selectDiagnosisLoading), []);)))));
  const currentSession = useMemo() => useAppSelector(selectCurrentSession), []);)))));
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [sessionId, setSessionId] = useState<string | null>(nul;l;);
  const [steps, setSteps] = useState<DiagnosisStep[] />([;];); 初始化诊断步骤 // useEffect() => {
    const effectStart = performance.now();
    if (visible) {initializeDiagnosisSteps();
    }
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [visible, diagnosisType]);
  const initializeDiagnosisSteps = useCallback(); => {}
    let diagnosisSteps: DiagnosisStep[] = [];
    switch (diagnosisType) {
      case "inspection":
        diagnosisSteps = [
          {
            id: face_analysis",
            title: "面部分析,",
            description: "请正视摄像头，保持自然表情",
            completed: false;
          },
          {
            id: tongue_analysis",
            title: "舌象分析,",
            description: "请伸出舌头，保持良好光线",
            completed: false;
          },
          {
            id: posture_analysis",
            title: "体态分析,",
            description: "请站立，展示整体体态",
            completed: false;
          }
        ];
        break;
case auscultation":"
        diagnosisSteps = [
          {
      id: "voice_analysis,",
      title: "语音分析", "
            description: 请说话30秒，描述您的感受",
            completed: false;
          },
          {
      id: "breathing_analysis,",
      title: "呼吸音分析", "
            description: 请深呼吸5次",
            completed: false;
          },
          {
      id: "cough_analysis,",
      title: "咳嗽分析", "
            description: 如有咳嗽，请咳嗽几声",
            completed: false;
          }
        ];
        break;
case "inquiry:"
        diagnosisSteps = [
          {
      id: "symptoms_inquiry",
      title: 症状询问",
            description: "请详细描述您的症状,",
            completed: false;
          },
          {
      id: "medical_history",
      title: 病史采集",
            description: "请提供相关病史信息,",
            completed: false;
          },
          {
      id: "lifestyle_inquiry",
      title: 生活习惯",
            description: "请描述您的生活习惯,",
            completed: false;
          }
        ];
        break;
case "palpation":
        diagnosisSteps = [
          {
            id: pulse_analysis",
            title: "脉象分析,",
            description: "请将手指放在传感器上",
            completed: false;
          },
          {
            id: abdomen_palpation",
            title: "腹部触诊,",
            description: "请按照指示进行腹部检查",
            completed: false;
          },
          {
            id: acupoint_check",
            title: "穴位检查,",
            description: "请按压指定穴位", "
            completed: false;
          }
        ];
        break;
    }
    setSteps(diagnosisSteps);
    setCurrentStep(0);
  };
  const startDiagnosis = useMemo() => async() => {})
    try {
      const result = await dispatch(startDiagnosisSessi;o;n), []);
      if (startDiagnosisSession.fulfilled.match(result);) {
        setSessionId(result.payload.id);
        Alert.alert(诊断开始", "诊断会话已启动，请按步骤进行);
      }
    } catch (error) {
      Alert.alert("启动失败", " 无法启动诊断会话，请稍后重试");"
    }
  };
  const completeStep = useMemo() => async (stepData: unknown) => {})
    if (!sessionId) { ///
    try {
      const result = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => await dispatch(;)
        submitDiagnosisData({
          sessionId,
          type: diagnosisType,
          data: {,
  stepId: steps[currentStep].id,
            stepData,
            timestamp: new Date().toISOString()}
        });
      ), [;];);
      if (submitDiagnosisData.fulfilled.match(result);) {
        const updatedSteps = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => [...steps], []);)))))
        updatedSteps[currentStep].completed = true;
        updatedSteps[currentStep].data = stepData;
        setSteps(updatedSteps);
        if (currentStep < steps.length - 1) {
          setCurrentStep(currentStep + 1);
        } else {
          await completeDiagnosis(;);
        }
      }
    } catch (error) {
      Alert.alert("提交失败, "步骤数据提交失败，请重试");"
    }
  };
  const completeDiagnosis = useMemo() => async() => {})
    if (!sessionId) { ///
    try {
      const result = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => await dispatch(completeDiagnosisSession(sessionI;d;);), []);)))));
      if (completeDiagnosisSession.fulfilled.match(result)) {
        Alert.alert()
          诊断完成", "您的诊断已完成，结果已保存到健康档案中,"
          [{
      text: "确定", "
      onPress: onClose}]
        );
      }
    } catch (error) {
      Alert.alert(完成失败", "诊断完成时发生错误);
    }
  };
  const renderStepContent = useCallback => {}
    if (!step) {return nu;l;l}
    switch (step.id) {
      case "face_analysis":
      case tongue_analysis":"
      case "posture_analysis:"
        performanceMonitor.recordRender();
        return (;)
          <View style={styles.stepContent}>/            <Icon name="camera" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> completeStep({,
  type: "image",
      captured: tr;u;e ;})}/                >
              <Text style={styles.actionButtonText}>拍照分析</Text>/            </TouchableOpacity>/          </View>/            )
      case voice_analysis":"
      case "breathing_analysis:"
      case "cough_analysis":
        return (;)
          <View style={styles.stepContent}>/            <Icon name="microphone" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> completeStep({ type: audio", recorded: tr;u;e ;})}/                >"
              <Text style={styles.actionButtonText}>开始录音</Text>/            </TouchableOpacity>/          </View>/            )
      case "symptoms_inquiry:"
      case "medical_history":
      case lifestyle_inquiry":"
        return (;)
          <View style={styles.stepContent}>/            <Icon name="clipboard-text" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TextInput;
style={styles.textInput}
              placeholder="请详细描述..."
              multiline;
numberOfLines={4}
              onChangeText={(text) = /> {/                 }}
            />/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> completeStep({ type: "text, content: "用户输入的内;容" ;})}/                >"
              <Text style={styles.actionButtonText}>提交信息</Text>/            </TouchableOpacity>/          </View>/            );
      case pulse_analysis":"
      case "abdomen_palpation:"
      case "acupoint_check":
        return (;)
          <View style={styles.stepContent}>/            <Icon name="hand-back-right" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> completeStep({ type: sensor", data: "sensor_dat;a ;})}/                >
              <Text style={styles.actionButtonText}>开始检测</Text>/            </TouchableOpacity>/          </View>/            );
      default:
        return nu;l;l;
    }
  };
  //
    <View style={styles.progressContainer}>/          {steps.map(step, index); => ()
        <View key={step.id} style={styles.progressItem}>/              <View;
style={[
              styles.progressDot,
              { backgroundColor: step.completed;? colors.success: index === currentStep;? colors.primary: colors.border}}
            ]} />/                {step.completed  && <Icon name="check" size={12} color="white" />/                )}
          </View>/          <Text style={styles.progressLabel}>{step.title}</Text>/        </View>/          ))}
    </View>/      ), [])
  return (;)
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" />/      <SafeAreaView style={styles.container}>/        {///;
        {///            {renderProgressBar()};
        {///                  <TouchableOpacity;
style={styles.startButton}
                onPress={startDiagnosis}
                disabled={loading}
              accessibilityLabel="TODO: 添加无障碍标签" />/                {loading ? ()
                  <ActivityIndicator color="white" />/                    ): (
                  <Text style= {styles.startButtonText} />开始诊断</Text>/                    )};
              </TouchableOpacity>/            </View>/              ) : (;
            renderStepContent;
          )}
        </ScrollView>/      </SafeAreaView>/    </Modal>/      );
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({container: {),
  flex: 1,
    backgroundColor: colors.background;
  },
  header: {,
  flexDirection: "row",
    alignItems: center",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border;
  },
  closeButton: { padding: spacing.sm  },
  headerContent: {,
  flex: 1,
    marginLeft: spacing.md;
  },
  title: {,
  fontSize: 20,
    fontWeight: "bold,",
    color: colors.text;
  },
  description: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginTop: 4;
  },
  progressContainer: {,
  flexDirection: "row",
    justifyContent: space-around",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface;
  },
  progressItem: {,
  alignItems: "center,",
    flex: 1;
  },
  progressDot: {,
  width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: center",
    marginBottom: spacing.xs;
  },
  progressLabel: {,
  fontSize: 12,
    color: colors.textSecondary,
    textAlign: "center"
  },
  content: { flex: 1  },
  contentContainer: {,
  flexGrow: 1,
    padding: spacing.lg;
  },
  startContainer: {,
  flex: 1,
    justifyContent: "center",
    alignItems: center""
  },
  startTitle: {,
  fontSize: 24,
    fontWeight: "bold,",
    color: colors.text,
    marginTop: spacing.lg,
    marginBottom: spacing.md;
  },
  startDescription: {,
  fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center",
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.lg;
  },
  startButton: {,
  backgroundColor: colors.primary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: 8,
    minWidth: 120,
    alignItems: center""
  },
  startButtonText: {,
  color: "white,",
    fontSize: 16,
    fontWeight: "600"
  },
  stepContent: {,
  flex: 1,
    justifyContent: center",
    alignItems: "center"
  },
  stepDescription: {,
  fontSize: 18,
    color: colors.text,
    textAlign: "center",
    marginVertical: spacing.lg,
    paddingHorizontal: spacing.lg;
  },
  actionButton: {,
  backgroundColor: colors.primary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: 8,
    marginTop: spacing.lg;
  },
  actionButtonText: {,
  color: white",
    fontSize: 16,
    fontWeight: "600"
  },
  textInput: {,
  borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: spacing.md,
    width: "100%",
    minHeight: 100,
    textAlignVertical: top",
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface;
  }
}), []);
export default React.memo(DiagnosisModal);