import type { EChartsOption } from 'echarts'
import type { IShearResult } from '@/types/analysis'

export function shearProfileOption(data: IShearResult): EChartsOption {
  const heights = data.heights
  const meanSpeeds = data.meanSpeeds
  const fittedSpeeds = data.fittedSpeeds

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['实测平均风速', '幂律拟合'] },
    grid: { left: 70, right: 40, top: 30, bottom: 60 },
    xAxis: {
      type: 'value',
      name: '风速 (m/s)',
      nameLocation: 'end',
    },
    yAxis: {
      type: 'category',
      data: heights.map((h) => `${h}m`),
      name: '高度',
    },
    series: [
      {
        name: '实测平均风速',
        type: 'scatter',
        data: meanSpeeds.map((v, i) => [v, `${heights[i]}m`]),
        symbolSize: 10,
        itemStyle: { color: '#2563eb' },
      },
      {
        name: '幂律拟合',
        type: 'line',
        data: fittedSpeeds.map((v, i) => [v, `${heights[i]}m`]),
        smooth: true,
        showSymbol: false,
        lineStyle: { color: '#dc2626', width: 2, type: 'dashed' },
      },
    ],
  }
}
