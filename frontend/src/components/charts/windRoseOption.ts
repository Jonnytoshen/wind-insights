import type { EChartsOption } from 'echarts'
import type { IWindRoseData } from '@/types/analysis'

export function windRoseOption(data: IWindRoseData): EChartsOption {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
  const speedBins = ['0–3', '3–6', '6–9', '9–12', '>12']
  const palette = ['#93c5fd', '#3b82f6', '#1d4ed8', '#1e3a8a', '#172554']

  const series = data.speedBinFreqs.map((binData, i) => ({
    type: 'bar',
    name: `${speedBins[i]} m/s`,
    stack: 'rose',
    coordinateSystem: 'polar',
    data: binData,
    itemStyle: { color: palette[i] },
  }))

  return {
    polar: {},
    angleAxis: {
      type: 'category',
      data: directions,
      startAngle: 90,
      clockwise: false,
    },
    radiusAxis: {
      min: 0,
      axisLabel: { formatter: '{value}%' },
    },
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, data: speedBins.map((b) => `${b} m/s`) },
    series: series as EChartsOption['series'],
  }
}
