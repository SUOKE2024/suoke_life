
import React from "react";
import Icon from "../../../components/common/Icon";
import { colors, spacing } from ../../../constants/theme"/
import React,{ useState, useEffect } from react"";
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
  onClose: () => void;
  diagnosisType: DiagnosisType;
  title: string;
  description: string;
}
interface DiagnosisStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
data?: unknown;
}
export const DiagnosisModal: React.FC<DiagnosisModalProps /> = ({/   const performanceMonitor = usePerformanceMonitor("DiagnosisModal, ";))
{/
    trackRender: true;
    trackMemory: true;
    warnThreshold: 50;});
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
            id: face_analysis";


            completed: false;
          },
          {
            id: tongue_analysis";


            completed: false;
          },
          {
            id: posture_analysis";


            completed: false;
          }
        ];
        break;
case auscultation":"
        diagnosisSteps = [
          {
      id: "voice_analysis,",


            completed: false;
          },
          {
      id: "breathing_analysis,",


            completed: false;
          },
          {
      id: "cough_analysis,",


            completed: false;
          }
        ];
        break;
case "inquiry:"
        diagnosisSteps = [
          {
      id: "symptoms_inquiry";


            completed: false;
          },
          {
      id: "medical_history";


            completed: false;
          },
          {
      id: "lifestyle_inquiry";


            completed: false;
          }
        ];
        break;
case "palpation":
        diagnosisSteps = [
          {
            id: pulse_analysis";


            completed: false;
          },
          {
            id: abdomen_palpation";


            completed: false;
          },
          {
            id: acupoint_check";


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

      }
    } catch (error) {

    }
  };
  const completeStep = useMemo() => async (stepData: unknown) => {;})
    if (!sessionId) { ///
    try {
      const result = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => await dispatch(;)
        submitDiagnosisData({
          sessionId,
          type: diagnosisType;
          data: {,
  stepId: steps[currentStep].id;
            stepData,
            timestamp: new Date().toISOString();}
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

    }
  };
  const completeDiagnosis = useMemo() => async() => {})
    if (!sessionId) { ///
    try {
      const result = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => await dispatch(completeDiagnosisSession(sessionI;d;);), []);)))));
      if (completeDiagnosisSession.fulfilled.match(result)) {
        Alert.alert()

          [{

      onPress: onClose;}]
        );
      }
    } catch (error) {

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
              onPress={() = accessibilityLabel="操作按钮" /> completeStep({,
  type: "image";
      captured: tr;u;e ;})}/                >
              <Text style={styles.actionButtonText}>拍照分析</Text>/            </TouchableOpacity>/          </View>/            )
      case voice_analysis":"
      case "breathing_analysis:"
      case "cough_analysis":
        return (;)
          <View style={styles.stepContent}>/            <Icon name="microphone" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="操作按钮" /> completeStep({ type: audio", recorded: tr;u;e ;})}/                >"
              <Text style={styles.actionButtonText}>开始录音</Text>/            </TouchableOpacity>/          </View>/            )
      case "symptoms_inquiry:"
      case "medical_history":
      case lifestyle_inquiry":"
        return (;)
          <View style={styles.stepContent}>/            <Icon name="clipboard-text" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TextInput;
style={styles.textInput}

              multiline;
numberOfLines={4}
              onChangeText={(text) = /> {/                 }}
            />/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="操作按钮" /> completeStep({ type: "text, content: "用户输入的内;容" ;})}/                >"
              <Text style={styles.actionButtonText}>提交信息</Text>/            </TouchableOpacity>/          </View>/            );
      case pulse_analysis":"
      case "abdomen_palpation:"
      case "acupoint_check":
        return (;)
          <View style={styles.stepContent}>/            <Icon name="hand-back-right" size={64} color={colors.primary} />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;
              style={styles.actionButton}
              onPress={() = accessibilityLabel="操作按钮" /> completeStep({ type: sensor", data: "sensor_dat;a ;})}/                >
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
              { backgroundColor: step.completed;? colors.success: index === currentStep;? colors.primary: colors.border;}}
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
              accessibilityLabel="操作按钮" />/                {loading ? ()
                  <ActivityIndicator color="white" />/                    ): (
                  <Text style= {styles.startButtonText} />开始诊断</Text>/                    )};
              </TouchableOpacity>/            </View>/              ) : (;
            renderStepContent;
          )}
        </ScrollView>/      </SafeAreaView>/    </Modal>/      );
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({container: {),
  flex: 1;
    backgroundColor: colors.background;
  },
  header: {,
  flexDirection: "row";
    alignItems: center";
    paddingHorizontal: spacing.lg;
    paddingVertical: spacing.md;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  closeButton: { padding: spacing.sm  ;},
  headerContent: {,
  flex: 1;
    marginLeft: spacing.md;
  },
  title: {,
  fontSize: 20;
    fontWeight: "bold,",
    color: colors.text;
  },
  description: {,
  fontSize: 14;
    color: colors.textSecondary;
    marginTop: 4;
  },
  progressContainer: {,
  flexDirection: "row";
    justifyContent: space-around";
    paddingHorizontal: spacing.lg;
    paddingVertical: spacing.md;
    backgroundColor: colors.surface;
  },
  progressItem: {,
  alignItems: "center,",
    flex: 1;
  },
  progressDot: {,
  width: 24;
    height: 24;
    borderRadius: 12;
    justifyContent: "center";
    alignItems: center";
    marginBottom: spacing.xs;
  },
  progressLabel: {,
  fontSize: 12;
    color: colors.textSecondary;
    textAlign: "center"
  ;},
  content: { flex: 1  ;},
  contentContainer: {,
  flexGrow: 1;
    padding: spacing.lg;
  },
  startContainer: {,
  flex: 1;
    justifyContent: "center";
    alignItems: center""
  ;},
  startTitle: {,
  fontSize: 24;
    fontWeight: "bold,",
    color: colors.text;
    marginTop: spacing.lg;
    marginBottom: spacing.md;
  },
  startDescription: {,
  fontSize: 16;
    color: colors.textSecondary;
    textAlign: "center";
    marginBottom: spacing.xl;
    paddingHorizontal: spacing.lg;
  },
  startButton: {,
  backgroundColor: colors.primary;
    paddingHorizontal: spacing.xl;
    paddingVertical: spacing.md;
    borderRadius: 8;
    minWidth: 120;
    alignItems: center""
  ;},
  startButtonText: {,
  color: "white,",
    fontSize: 16;
    fontWeight: "600"
  ;},
  stepContent: {,
  flex: 1;
    justifyContent: center";
    alignItems: "center"
  ;},
  stepDescription: {,
  fontSize: 18;
    color: colors.text;
    textAlign: "center";
    marginVertical: spacing.lg;
    paddingHorizontal: spacing.lg;
  },
  actionButton: {,
  backgroundColor: colors.primary;
    paddingHorizontal: spacing.xl;
    paddingVertical: spacing.md;
    borderRadius: 8;
    marginTop: spacing.lg;
  },
  actionButtonText: {,
  color: white";
    fontSize: 16;
    fontWeight: "600"
  ;},
  textInput: {,
  borderWidth: 1;
    borderColor: colors.border;
    borderRadius: 8;
    padding: spacing.md;
    width: "100%";
    minHeight: 100;
    textAlignVertical: top";
    fontSize: 16;
    color: colors.text;
    backgroundColor: colors.surface;
  }
}), []);
export default React.memo(DiagnosisModal);