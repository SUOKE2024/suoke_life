// 指标收集器 - 索克生活
export class MetricsCollector {
  private counters: Map<string, number> = new Map();
  private gauges: Map<string, number> = new Map();
  private histograms: Map<string, number[]> = new Map();

  incrementCounter(name: string, labels?: Record<string, string>): void {
    const key = this.buildKey(name, labels);
    const current = this.counters.get(key) || 0;
    this.counters.set(key, current + 1);
  }

  setGauge(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.buildKey(name, labels);
    this.gauges.set(key, value);
  }

  recordHistogram(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.buildKey(name, labels);
    const values = this.histograms.get(key) || [];
    values.push(value);
    this.histograms.set(key, values);
  }

  getCounter(name: string, labels?: Record<string, string>): number {
    const key = this.buildKey(name, labels);
    return this.counters.get(key) || 0;
  }

  getGauge(name: string, labels?: Record<string, string>): number {
    const key = this.buildKey(name, labels);
    return this.gauges.get(key) || 0;
  }

  getHistogram(name: string, labels?: Record<string, string>): number[] {
    const key = this.buildKey(name, labels);
    return this.histograms.get(key) || [];
  }

  private buildKey(name: string, labels?: Record<string, string>): string {
    if (!labels) {
      return name;
    }
    
    const labelStr = Object.entries(labels)
      .map(([k, v]) => `${k}=${v}`)
      .join(',');
    
    return `${name}{${labelStr}}`;
  }

  reset(): void {
    this.counters.clear();
    this.gauges.clear();
    this.histograms.clear();
  }

  // 获取所有指标
  getAllMetrics(): {
    counters: Record<string, number>;
    gauges: Record<string, number>;
    histograms: Record<string, number[]>;
  } {
    return {
      counters: Object.fromEntries(this.counters),
      gauges: Object.fromEntries(this.gauges),
      histograms: Object.fromEntries(this.histograms)
    };
  }

  // 计算直方图统计信息
  getHistogramStats(name: string, labels?: Record<string, string>): {
    count: number;
    sum: number;
    avg: number;
    min: number;
    max: number;
  } {
    const values = this.getHistogram(name, labels);
    
    if (values.length === 0) {
      return { count: 0, sum: 0, avg: 0, min: 0, max: 0 };
    }

    const sum = values.reduce((a, b) => a + b, 0);
    const avg = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    return { count: values.length, sum, avg, min, max };
  }
}