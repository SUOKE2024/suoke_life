{"monitoring": {
    "enabled": true,
    "interval": 1000,
    "bufferSize": 1000,
    "autoReport": true;
  },
  "thresholds": {
    "component": {
      "renderTime": {
        "excellent": 16,
        "good": 33,
        "acceptable": 50,
        "poor": 100;
      },
      "memoryUsage": {
        "excellent": 10,
        "good": 25,
        "acceptable": 50,
        "poor": 100;
      },
      "bundleSize": {
        "excellent": 100,
        "good": 250,
        "acceptable": 500,
        "poor": 1000;
      }
    },
    "api": {
      "responseTime": {
        "excellent": 200,
        "good": 500,
        "acceptable": 1000,
        "poor": 2000;
      },
      "throughput": {
        "excellent": 1000,
        "good": 500,
        "acceptable": 100,
        "poor": 50;
      },
      "errorRate": {
        "excellent": 0.1,
        "good": 1,
        "acceptable": 5,
        "poor": 10;
      }
    },
    "agent": {
      "decisionTime": {
        "excellent": 500,
        "good": 1000,
        "acceptable": 2000,
        "poor": 5000;
      },
      "accuracy": {
        "excellent": 95,
        "good": 90,
        "acceptable": 85,
        "poor": 80;
      },
      "learningRate": {
        "excellent": 0.9,
        "good": 0.7,
        "acceptable": 0.5,
        "poor": 0.3;
      }
    }
  },
  "alerts": {
    "email": {
      "enabled": false,
      "recipients": []
    },
    "webhook": {
      "enabled": false,
      "url": ""
    },
    "console": {
      "enabled": true,
      "level": "warn"
    }
  },
  "reporting": {
    "enabled": true,
    "format": "json",destination": "logs/    performance",retention": 30;
  }
};