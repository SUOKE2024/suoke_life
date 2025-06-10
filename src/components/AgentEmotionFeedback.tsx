import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

interface FeedbackItem {
  key: string;
  label: string;
  desc: string;
}

interface AgentEmotionFeedbackProps {
  onFeedback: (feedbackKey: string) => void;
  disabled?: boolean;
  children?: React.ReactNode;
}

const FEEDBACKS: FeedbackItem[] = [
  {
    key: 'like',
    label: '👍',
    desc: '喜欢',
  },
  {
    key: 'care',
    label: '🤗',
    desc: '关怀',
  },
  {
    key: 'suggest',
    label: '💡',
    desc: '建议',
  },
  {
    key: 'dislike',
    label: '👎',
    desc: '不喜欢',
  },
];

export const AgentEmotionFeedback: React.FC<AgentEmotionFeedbackProps> = ({
  onFeedback,
  disabled = false,
}) => {
  const handleFeedback = (feedbackKey: string) => {
    if (!disabled) {
      onFeedback(feedbackKey);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>您的反馈</Text>
      <View style={styles.row}>
        {FEEDBACKS.map((fb) => (
          <TouchableOpacity
            key={fb.key}
            style={[styles.btn, disabled && styles.btnDisabled]}
            onPress={() => handleFeedback(fb.key)}
            disabled={disabled}
            accessibilityLabel={`${fb.desc}反馈`}
            accessibilityRole="button"
            accessibilityState={{ disabled }}
          >
            <Text style={[styles.icon, disabled && styles.iconDisabled]}>
              {fb.label}
            </Text>
            <Text style={[styles.desc, disabled && styles.descDisabled]}>
              {fb.desc}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  btn: {
    alignItems: 'center',
    marginHorizontal: 10,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
    minWidth: 60,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  icon: {
    fontSize: 22,
    marginBottom: 4,
  },
  iconDisabled: {
    opacity: 0.6,
  },
  desc: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  descDisabled: {
    color: '#999',
  },
});
