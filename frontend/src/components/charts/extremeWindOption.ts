import type { EChartsOption } from 'echarts'
import type { IExtremeWindResult } from '@/types/analysis'

export function extremeWindOption(data: IExtremeWindResult): EChartsOption {
  const years = data.annualMaxYears
  const maxValues = data.annualMaxValues

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['年最大风速', 'Gumbel 拟合分位值'] },
    grid: { left: 60, right: 20, top: 30, bottom: 60 },
    xAxis: {
      type: 'category',
      data: years.map(String),
      name: '年份',
      nameLocation: 'end',
    },
    yAxis: {
      type: 'value',
      name: '风速 (m/s)',
      nameTextStyle: { fontSize: 12 },
    },
    series: [
      {
        name: '年最大风速',
        type: 'bar',
        data: maxValues,
        itemStyle: { color: '#3b82f6' },
      },
      {
        name: 'Gumbel 拟合分位值',
        type: 'scatter',
        data: [
          { name: 'V50', value: [years.length - 1, data.v50], label: { show: true, formatter: `V50=${data.v50.toFixed(1)}m/s`, position: 'top', color: '#dc2626' } },
          { name: 'V100', value: [years.length - 1, data.v100], label: { show: true, formatter: `V100=${data.v100.toFixed(1)}m/s`, position: 'bottom', color: '#7c3aed' } },
        ],
        symbolSize: 12,
        itemStyle: { color: '#dc2626' },
      },
    ],
  }
}
