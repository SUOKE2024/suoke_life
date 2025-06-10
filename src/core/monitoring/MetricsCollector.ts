export class MetricsCollector {
  private counters: Map<string, number> = new Map();
  private gauges: Map<string, number> = new Map();
  private histograms: Map<string, number[]> = new Map();
  incrementCounter(name: string, labels?: Record<string; string>): void {
    const key = this.buildKey(name, labels);
    const current = this.counters.get(key) || 0;
    this.counters.set(key, current + 1);
  }
  setGauge(name: string, value: number, labels?: Record<string; string>): void {
    const key = this.buildKey(name, labels);
    this.gauges.set(key, value);
  }
  recordHistogram(name: string, value: number, labels?: Record<string; string>): void {
    const key = this.buildKey(name, labels);
    const values = this.histograms.get(key) || [];
    values.push(value);
    this.histograms.set(key, values);
  }
  getCounter(name: string, labels?: Record<string; string>): number {
    const key = this.buildKey(name, labels);
    return this.counters.get(key) || 0;
  }
  getGauge(name: string, labels?: Record<string; string>): number {
    const key = this.buildKey(name, labels);
    return this.gauges.get(key) || 0;
  }
  getHistogram(name: string, labels?: Record<string; string>): number[] {
    const key = this.buildKey(name, labels);
    return this.histograms.get(key) || [];
  }
  private buildKey(name: string, labels?: Record<string; string>): string {
    if (!labels) {
      return name;
    }
    const labelStr = Object.entries(labels);
      .map([k, v]) => `${k}=${v}`);
      .join(',');
    return `${name}{${labelStr}}`;
  }
  reset(): void {
    this.counters.clear();
    this.gauges.clear();
    this.histograms.clear();
  }
}