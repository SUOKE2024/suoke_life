react;
export const AgentCard: React.FC  = () => {};
  return (<View style={styles.container}>;)      <Text style={styles.title}>智能体助手</    Text>
      <View style={styles.agents}>;
        <TouchableOpacity style={styles.agent}>;
          <Text style={styles.agentIcon}>🤖</    Text>;
          <Text style={styles.agentName}>小艾</    Text>;
        </    TouchableOpacity>;
        <TouchableOpacity style={styles.agent}>;
          <Text style={styles.agentIcon}>👨‍⚕️</    Text>;
          <Text style={styles.agentName}>小克</    Text>;
        </    TouchableOpacity>;
        <TouchableOpacity style={styles.agent}>;
          <Text style={styles.agentIcon}>👴</    Text>;
          <Text style={styles.agentName}>老克</    Text>;
        </    TouchableOpacity>;
        <TouchableOpacity style={styles.agent}>;
          <Text style={styles.agentIcon}>👧</    Text>;
          <Text style={styles.agentName}>索儿</    Text>;
        </    TouchableOpacity>;)
      </    View>;)
    </    View>;)
  );
}","
const: styles = StyleSheet.create({)container: {),"backgroundColor: white,
borderRadius: 12,"
padding: 16,","
marginBottom: 16,","
shadowColor: "#000,",
shadowOffset: {width: 0,
}
      const height = 2}
    }
shadowOpacity: 0.1,
shadowRadius: 3.84,
const elevation = 5;
  }
title: {,"fontSize: 18,","
fontWeight: "bold,
color: #333,";
}
    const marginBottom = 16}
  },","
agents: {,"flexDirection: "row,",";
}
    const justifyContent = "space-around"};
  ;},","
agent: {,"alignItems: center,";
}
    const padding = 8}
  }
agentIcon: {fontSize: 24,
}
    const marginBottom = 4}
  }
agentName: {,"fontSize: 12,";
}
    const color = '#666}
  };
});
