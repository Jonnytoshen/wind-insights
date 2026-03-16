<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { ITurbulenceData } from '@/types/analysis'
import { turbulenceOption } from './turbulenceOption'

const props = defineProps<{
  data: ITurbulenceData
  height: number
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(turbulenceOption(props.data))

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(() => [props.data, props.height], () => {
  chart?.setOption(turbulenceOption(props.data), true)
})

defineExpose({
  getDataURL: () => chart?.getDataURL({ type: 'png', pixelRatio: 2 }),
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-6 text-sm bg-amber-50 rounded-lg p-3">
      <span class="text-slate-600">15 m/s 处 TI</span>
      <span class="text-2xl font-bold text-amber-700">{{ data.ti15?.toFixed(3) ?? '-' }}</span>
      <span class="text-slate-500">年均 TI: {{ data.annualMeanTi?.toFixed(3) ?? '-' }}</span>
    </div>
    <div ref="chartEl" class="w-full h-72" />
  </div>
</template>
