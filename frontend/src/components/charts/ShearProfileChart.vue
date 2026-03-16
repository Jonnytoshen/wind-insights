<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { IShearResult } from '@/types/analysis'
import { shearProfileOption } from './shearProfileOption'

const props = defineProps<{
  data: IShearResult
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(shearProfileOption(props.data))

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(() => props.data, () => {
  chart?.setOption(shearProfileOption(props.data), true)
})

defineExpose({
  getDataURL: () => chart?.getDataURL({ type: 'png', pixelRatio: 2 }),
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-6 text-sm bg-blue-50 rounded-lg p-3">
      <span class="text-slate-600">风切变指数 α</span>
      <span class="text-2xl font-bold text-blue-700">{{ data.alpha.toFixed(3) }}</span>
      <span class="text-slate-500">R² = {{ data.r2.toFixed(4) }}</span>
    </div>
    <div ref="chartEl" class="w-full h-72" />
  </div>
</template>
