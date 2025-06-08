import React from "react";
interface AgentVoiceInputProps {
  // TODO: 定义组件属性类型children?: React.ReactNode *;
}
import React,{ useState } from "react";
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  { ActivityIndicator } from "react-native";
* / * / export const AgentVoiceInput: React.FC<AgentVoiceInputProps  /    > void;
/    }>  = ({ onResult }) => {}
  const [recording, setRecording] = useState<boolean>(fals;e;);
  const [loading, setLoading] = useState<boolean>(fals;e;);
  const startRecording = async() => {};
    setRecording(tru;e;);
    setLoading(true);
    setTimeout(); => {}
      setLoading(false);
      setRecording(false);
      onResult("模拟语音识别结果");
    }, 2000);
  };
  const stopRecording = async() => {}
    setRecording(fals;e;);
    setLoading(false);
  };
  return (;
    <View style={styles.container}>/          <TouchableOpacity;
        style={[styles.button, recording && styles.buttonActive]};
        onPress={recording ? stopRecording: startRecordi;n;g}
        disabled={loading}
      accessibilityLabel="TODO: 添加无障碍标签" />/        <Text style={styles.icon}>{recording ? "🛑" : "🎤"}</Text>/        <Text style={styles.text}>{recording ? "录音中..." : "按下说话"}</Text>/      </TouchableOpacity>/      {loading && <ActivityIndicator style={ marginLeft: 12}} />}/    </View>/      );
}
const styles = StyleSheet.create({container: {,
  flexDirection: "row",
    alignItems: "center",
    marginVertical: 12;
  },
  button: {,
  flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#E1F5FE",
    borderRadius: 24,
    paddingVertical: 10,
    paddingHorizontal: 20;
  },
  buttonActive: { backgroundColor: "#B3E5FC"  },
  icon: {,
  fontSize: 22,
    marginRight: 8;
  },
  text: {,
  fontSize: 16,color: "#0277BD"};};);