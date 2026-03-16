<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { IWindRoseData } from '@/types/analysis'
import { windRoseOption } from './windRoseOption'

const props = defineProps<{
  data: IWindRoseData
  height: number
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(windRoseOption(props.data))

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(() => [props.data, props.height], () => {
  chart?.setOption(windRoseOption(props.data), true)
})

defineExpose({
  getDataURL: (opts?: { type?: 'png' | 'jpeg' | 'svg'; pixelRatio?: number; backgroundColor?: string }) =>
    chart?.getDataURL({ type: 'png', pixelRatio: 2, ...opts }),
})
</script>

<template>
  <div ref="chartEl" class="w-full h-96" />
</template>
