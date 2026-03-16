import type { EChartsOption } from 'echarts'

export interface IWindSpeedLineData {
  timestamps: string[]
  values: number[]
}

export function windSpeedLineOption(data: IWindSpeedLineData): EChartsOption {
  return {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        return `${p.axisValue}<br/>${p.marker}风速: <b>${p.value?.toFixed(2)} m/s</b>`
      },
    },
    grid: { left: 60, right: 20, top: 20, bottom: 50 },
    xAxis: {
      type: 'category',
      data: data.timestamps,
      axisLabel: {
        rotate: 30,
        interval: Math.floor(data.timestamps.length / 12),
        fontSize: 11,
      },
    },
    yAxis: {
      type: 'value',
      name: '风速 (m/s)',
      nameTextStyle: { fontSize: 12 },
    },
    series: [
      {
        type: 'line',
        data: data.values,
        smooth: false,
        showSymbol: false,
        lineStyle: { color: '#2563eb', width: 1 },
        areaStyle: { color: 'rgba(37,99,235,0.08)' },
      },
    ],
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', height: 20, bottom: 5 },
    ],
  }
}
