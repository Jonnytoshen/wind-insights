import type { EChartsOption } from 'echarts'
import type { IWeibullResult } from '@/types/analysis'

export function weibullOption(data: IWeibullResult): EChartsOption {
  const { histogram, fittedPdf } = data

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['实测频率', 'Weibull 拟合'] },
    grid: { left: 60, right: 20, top: 30, bottom: 60 },
    xAxis: {
      type: 'category',
      data: histogram.bins,
      name: '风速 (m/s)',
      nameLocation: 'end',
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: '频率 (%)',
      nameTextStyle: { fontSize: 12 },
    },
    series: [
      {
        name: '实测频率',
        type: 'bar',
        data: histogram.frequencies,
        itemStyle: { color: '#93c5fd' },
        barWidth: '90%',
      },
      {
        name: 'Weibull 拟合',
        type: 'line',
        data: fittedPdf,
        smooth: true,
        showSymbol: false,
        lineStyle: { color: '#dc2626', width: 2 },
      },
    ],
  }
}
