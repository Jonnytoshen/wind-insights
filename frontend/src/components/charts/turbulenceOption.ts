import type { EChartsOption } from 'echarts'
import type { ITurbulenceData } from '@/types/analysis'

export function turbulenceOption(data: ITurbulenceData): EChartsOption {
  const bins = data.windSpeedBins
  const tiMean = data.tiMeanByBin
  const tiStd = data.tiStdByBin

  const errorBarData = bins.map((_, i) => ({
    value: [tiMean[i], tiMean[i] + tiStd[i], tiMean[i] - tiStd[i]],
  }))

  return {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        return `风速: ${p.axisValue} m/s<br/>TI均值: ${tiMean[p.dataIndex]?.toFixed(3) ?? '-'}`
      },
    },
    grid: { left: 70, right: 20, top: 30, bottom: 50 },
    xAxis: {
      type: 'category',
      data: bins.map((b) => `${b}`),
      name: '风速 (m/s)',
      nameLocation: 'end',
    },
    yAxis: {
      type: 'value',
      name: '湍流强度 TI',
      nameTextStyle: { fontSize: 12 },
    },
    series: [
      {
        type: 'bar',
        data: tiMean,
        itemStyle: { color: '#3b82f6' },
        name: 'TI 均值',
      },
      {
        type: 'custom',
        name: 'TI 标准差',
        data: errorBarData,
        renderItem: (params: any, api: any) => {
          const xVal = api.value(0)
          const highPoint = api.coord([xVal, api.value(1)])
          const lowPoint = api.coord([xVal, api.value(2)])
          const xSpan = api.size([1, 0])[0] * 0.3
          return {
            type: 'group',
            children: [
              {
                type: 'line',
                shape: { x1: highPoint[0], y1: highPoint[1], x2: lowPoint[0], y2: lowPoint[1] },
                style: { stroke: '#dc2626', lineWidth: 1.5 },
              },
              {
                type: 'line',
                shape: {
                  x1: highPoint[0] - xSpan,
                  y1: highPoint[1],
                  x2: highPoint[0] + xSpan,
                  y2: highPoint[1],
                },
                style: { stroke: '#dc2626', lineWidth: 1.5 },
              },
              {
                type: 'line',
                shape: {
                  x1: lowPoint[0] - xSpan,
                  y1: lowPoint[1],
                  x2: lowPoint[0] + xSpan,
                  y2: lowPoint[1],
                },
                style: { stroke: '#dc2626', lineWidth: 1.5 },
              },
            ],
          }
        },
        z: 5,
      },
    ],
  }
}
