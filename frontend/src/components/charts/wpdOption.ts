import type { EChartsOption } from 'echarts'
import type { IWpdResult } from '@/types/analysis'

export function wpdOption(data: IWpdResult): EChartsOption {
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

  return {
    tooltip: { trigger: 'axis', valueFormatter: (v: any) => `${(v as number).toFixed(1)} W/m²` },
    grid: { left: 70, right: 20, top: 30, bottom: 50 },
    xAxis: { type: 'category', data: months },
    yAxis: {
      type: 'value',
      name: 'WPD (W/m²)',
      nameTextStyle: { fontSize: 12 },
    },
    series: [
      {
        type: 'bar',
        data: data.monthlyWpd,
        itemStyle: {
          color: (params: any) => {
            const val = params.value as number
            if (val >= 400) return '#1d4ed8'
            if (val >= 200) return '#3b82f6'
            return '#93c5fd'
          },
        },
        markLine: {
          data: [{ type: 'average', name: '年均', label: { formatter: '年均: {c} W/m²' } }],
          lineStyle: { color: '#dc2626', type: 'dashed' },
        },
      },
    ],
  }
}
