import React, { useMemo } from 'react';
import { Dimensions, StyleSheet, Text, View } from 'react-native';

interface HealthDataPoint {
  date: string;
  value: number;
}

interface HealthTrendChartProps {
  title: string;
  data: HealthDataPoint[];
  unit: string;
  children?: React.ReactNode;
}

export const HealthTrendChart: React.FC<HealthTrendChartProps> = ({
  title,
  data,
  unit,
;}) => {
  const max = useMemo(() => {
    return Math.max(...data.map((d) => d.value), 1);
  }, [data]);

  const min = useMemo(() => {
    return Math.min(...data.map((d) => d.value), 0);
  }, [data]);

  const width = useMemo(() => {
    return Dimensions.get('window').width - 40;
  }, []);

  const height = 120;

  const renderChart = () => {
    if (data.length < 2) return null;

    return data.map((d, i) => {
      if (i === 0) return null;

      const x1 = ((i - 1) / (data.length - 1)) * width;
      const x2 = (i / (data.length - 1)) * width;
      const y1 = height - ((data[i - 1].value - min) / (max - min)) * height;
      const y2 = height - ((d.value - min) / (max - min)) * height;

      return (
        <View
          key={`${d.date}-${i}`}
          style={[
            styles.chartLine,
            {
              left: x1;
              top: Math.min(y1, y2),
              width: Math.max(2, x2 - x1),
              height: Math.abs(y2 - y1) || 2;
            },
          ]}
        />
      );
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <View style={[styles.chart, { width, height }]}>{renderChart()}</View>
      <View style={styles.labels}>
        <Text style={styles.label}>{data[0]?.date}</Text>
        <Text style={styles.label}>{data[data.length - 1]?.date}</Text>
      </View>
      <Text style={styles.unit}>{unit}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 16;
    backgroundColor: '#fff';
    borderRadius: 12;
    padding: 12;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
  },
  title: {
    fontSize: 16;
    fontWeight: 'bold';
    marginBottom: 8;
    color: '#333';
  },
  chart: {
    backgroundColor: '#E3F2FD';
    borderRadius: 8;
    overflow: 'hidden';
    marginBottom: 8;
    alignSelf: 'center';
    position: 'relative';
  },
  chartLine: {
    position: 'absolute';
    backgroundColor: '#4FC3F7';
    borderRadius: 2;
  },
  labels: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    marginTop: 4;
  },
  label: {
    fontSize: 12;
    color: '#888';
  },
  unit: {
    fontSize: 12;
    color: '#4FC3F7';
    alignSelf: 'flex-end';
    marginTop: 2;
  },
});
