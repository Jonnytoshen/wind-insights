<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { IRepresentativeYearResult } from '@/types/analysis'
import { repYearOption } from './repYearOption'

const props = defineProps<{
  data: IRepresentativeYearResult
  height: number
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(repYearOption(props.data))

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(() => [props.data, props.height], () => {
  chart?.setOption(repYearOption(props.data), true)
})

defineExpose({
  getDataURL: () => chart?.getDataURL({ type: 'png', pixelRatio: 2 }),
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-6 text-sm bg-green-50 rounded-lg p-3">
      <span class="text-slate-600">代表年</span>
      <span class="text-2xl font-bold text-green-700">{{ data.representativeYear }}</span>
      <span class="text-slate-500">年均风速偏差: {{ data.biasFromLongTerm?.toFixed(2) ?? '-' }} m/s</span>
    </div>
    <div ref="chartEl" class="w-full h-72" />
  </div>
</template>
