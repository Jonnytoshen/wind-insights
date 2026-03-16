<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { IAnalysisResult } from '@/types/analysis'

const props = defineProps<{
  result: IAnalysisResult
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

const heights = computed(() => props.result.analysisHeights)

const compareOption = computed(() => {
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  const palette = ['#2563eb', '#dc2626', '#16a34a', '#d97706', '#7c3aed', '#0891b2']

  const series = heights.value.map((h, i) => {
    const key = `${h}m`
    const data = props.result.basicStats[key]?.monthlyMeanValues ?? []
    return {
      name: `${h}m 高度`,
      type: 'line' as const,
      data,
      smooth: true,
      showSymbol: true,
      lineStyle: { color: palette[i % palette.length], width: 2 },
      itemStyle: { color: palette[i % palette.length] },
    }
  })

  return {
    tooltip: { trigger: 'axis', valueFormatter: (v: any) => `${(v as number).toFixed(2)} m/s` },
    legend: { bottom: 0, data: heights.value.map((h) => `${h}m 高度`) },
    grid: { left: 60, right: 20, top: 30, bottom: 60 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: '月均风速 (m/s)', nameTextStyle: { fontSize: 12 } },
    series,
  }
})

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(compareOption.value)

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(compareOption, (opt) => {
  chart?.setOption(opt, true)
})

defineExpose({
  getDataURL: () => chart?.getDataURL({ type: 'png', pixelRatio: 2 }),
})
</script>

<template>
  <div class="space-y-6">
    <!-- Summary table -->
    <div class="overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="bg-slate-100">
            <th class="border border-slate-200 px-3 py-2 text-left">高度</th>
            <th class="border border-slate-200 px-3 py-2 text-right">年均风速 (m/s)</th>
            <th class="border border-slate-200 px-3 py-2 text-right">年均 WPD (W/m²)</th>
            <th class="border border-slate-200 px-3 py-2 text-right">Weibull k</th>
            <th class="border border-slate-200 px-3 py-2 text-right">Weibull c</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in heights" :key="h" class="hover:bg-slate-50">
            <td class="border border-slate-200 px-3 py-2 font-medium">{{ h }}m</td>
            <td class="border border-slate-200 px-3 py-2 text-right">
              {{ result.basicStats[`${h}m`]?.annualMeanWs?.toFixed(2) ?? '-' }}
            </td>
            <td class="border border-slate-200 px-3 py-2 text-right">
              {{ result.wpdResults[`${h}m`]?.annualWpd?.toFixed(1) ?? '-' }}
            </td>
            <td class="border border-slate-200 px-3 py-2 text-right">
              {{ result.weibullResults[`${h}m`]?.k?.toFixed(3) ?? '-' }}
            </td>
            <td class="border border-slate-200 px-3 py-2 text-right">
              {{ result.weibullResults[`${h}m`]?.c?.toFixed(3) ?? '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Monthly wind speed comparison chart -->
    <div>
      <h4 class="text-sm font-medium text-slate-600 mb-2">各高度月均风速对比</h4>
      <div ref="chartEl" class="w-full h-72" />
    </div>
  </div>
</template>
