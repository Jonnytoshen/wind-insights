import type { EChartsOption } from 'echarts'
import type { IRepresentativeYearResult } from '@/types/analysis'

export function repYearOption(data: IRepresentativeYearResult): EChartsOption {
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

  return {
    tooltip: { trigger: 'axis', valueFormatter: (v: any) => `${(v as number).toFixed(2)} m/s` },
    legend: { bottom: 0, data: ['多年月均', `代表年 ${data.representativeYear}`] },
    grid: { left: 60, right: 20, top: 30, bottom: 60 },
    xAxis: { type: 'category', data: months },
    yAxis: {
      type: 'value',
      name: '风速 (m/s)',
      nameTextStyle: { fontSize: 12 },
    },
    series: [
      {
        name: '多年月均',
        type: 'bar',
        data: data.longTermMonthlyMean,
        itemStyle: { color: '#93c5fd' },
      },
      {
        name: `代表年 ${data.representativeYear}`,
        type: 'line',
        data: data.repYearMonthlyMean,
        smooth: true,
        showSymbol: true,
        lineStyle: { color: '#dc2626', width: 2 },
        itemStyle: { color: '#dc2626' },
      },
    ],
  }
}
