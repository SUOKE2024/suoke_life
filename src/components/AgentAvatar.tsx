import {  View, Text, StyleSheet  } from "react-native"
export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
interface AgentAvatarProps {
const agentType = AgentTypeemotion?: string;
}
  size?: number}
}
const  AGENT_META = {xiaoai: {,'}
}
    color: '#4FC3F7,'}
avatar: '🤖';},'
xiaoke: {,'}
}
    color: '#81C784,'}
avatar: '📊';},'
laoke: {,'}
}
    color: '#FFD54F,'}
avatar: '👨‍⚕️';},'
soer: {,'}
}
    color: '#BA68C8,'}
const avatar = '🌟';}};
export const AgentAvatar: React.FC<AgentAvatarProps> = ({))'agentType,);
}
  emotion = 'neutral',)'}
size = 64;}) => {const meta = AGENT_META[agentType]const  getEmotionIcon = useCallback((emotion: string) => {'switch (emotion) {'case 'happy': '
return '😊
case 'sad': '
return '😢
case 'thinking': '
return '🤔';
const default =
}
        return }
    }
  };
return (<View;  />/,)style={[]styles.container,}        {backgroundColor: meta.color,}}/g,/;
  width: size + 16,}
];
const height = size + 16;}}]}
    >;
      <Text;  />
style={[styles.avatar, { fontSize: size * 0.6 ;}}]}
      >;
        {meta.avatar}
      </Text>)'/;'/g'/;
      <Text style={styles.name}>{meta.name}</Text>)'/;'/g'/;
      {emotion !== 'neutral'  && <Text style={styles.emotion}>')'
          {getEmotionIcon(emotion)}
        </Text>
      )}
    </View>
  );
};
const  styles = StyleSheet.create({)'container: {,'alignItems: 'center,'
justifyContent: 'center,'';
borderRadius: 48,
}
    margin: 8,}
    padding: 8;},'
avatar: {,'}
textAlign: 'center';},'
name: {,'fontSize: 12,'
fontWeight: 'bold,'
color: '#333,'
}
    marginTop: 4,'}
textAlign: 'center';},
emotion: {fontSize: 16,'
marginTop: 2,')'
position: 'absolute,')'
}
    top: -4;),}
const right = -4;}});