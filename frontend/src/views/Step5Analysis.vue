<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAnalysisStore } from '@/stores/analysis'
import WindSpeedLineChart from '@/components/charts/WindSpeedLineChart.vue'
import WindRoseChart from '@/components/charts/WindRoseChart.vue'
import WeibullChart from '@/components/charts/WeibullChart.vue'
import WpdChart from '@/components/charts/WpdChart.vue'
import ShearProfileChart from '@/components/charts/ShearProfileChart.vue'
import TurbulenceChart from '@/components/charts/TurbulenceChart.vue'
import ExtremeWindChart from '@/components/charts/ExtremeWindChart.vue'
import RepYearChart from '@/components/charts/RepYearChart.vue'
import MultiHeightCompare from '@/components/charts/MultiHeightCompare.vue'

const analysisStore = useAnalysisStore()
const { result } = storeToRefs(analysisStore)

const heights = computed(() => result.value?.analysisHeights ?? [])
const hasMultiHeight = computed(() => heights.value.length >= 2)
const activeHeight = ref('')

if (heights.value.length > 0) {
  activeHeight.value = `${heights.value[0]}m`
}

const heightKey = computed(() =>
  activeHeight.value || `${heights.value[0] ?? 100}m`
)

const modules = computed(() => {
  const list = [
    { key: 'basic',       label: '基础统计',        needsHeight: true },
    { key: 'windrose',    label: '风速风向玫瑰图',   needsHeight: true },
    { key: 'weibull',     label: 'Weibull 分布',    needsHeight: true },
    { key: 'wpd',         label: '风功率密度',       needsHeight: true },
    { key: 'shear',       label: '风切变分析',       needsHeight: false },
    { key: 'turbulence',  label: '湍流强度',         needsHeight: true },
    { key: 'extreme',     label: '极端风速',         needsHeight: true },
    { key: 'repyear',     label: '代表年分析',       needsHeight: true },
  ]
  if (hasMultiHeight.value) {
    list.push({ key: 'compare', label: '多高度对比', needsHeight: false })
  }
  return list
})

// Lazy rendering — chart is only mounted once its card scrolls into view
const mounted = reactive<Record<string, boolean>>({})

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const key = (entry.target as HTMLElement).dataset.moduleKey
        if (key && !mounted[key]) {
          mounted[key] = true
          observer.unobserve(entry.target)
        }
      }
    })
  },
  { rootMargin: '150px 0px' }
)

onUnmounted(() => observer.disconnect())

function registerCard(el: Element | null, key: string) {
  if (el) observer.observe(el)
}
</script>

<template>
  <div class="px-4 sm:px-6 py-5 max-w-5xl mx-auto">
    <div v-if="!result" class="text-center py-20 text-gray-400 text-sm">
      暂无数据，请先完成数据加载步骤
    </div>
    <template v-else>
      <!-- 全局高度切换（多高度时显示） -->
      <div v-if="heights.length > 1" class="flex items-center gap-2 flex-wrap mb-5">
        <span class="text-sm text-gray-500 shrink-0">分析高度：</span>
        <button
          v-for="h in heights"
          :key="h"
          class="px-3 py-1 rounded-full text-xs border transition-colors"
          :class="activeHeight === `${h}m`
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'"
          @click="activeHeight = `${h}m`"
        >
          {{ h }} m
        </button>
      </div>

      <!-- 模块 Card 列表（平铺） -->
      <div class="space-y-5">
        <section
          v-for="mod in modules"
          :key="mod.key"
          :ref="(el) => registerCard(el as Element | null, mod.key)"
          :data-module-key="mod.key"
          class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
        >
          <!-- Card 标题 -->
          <header class="px-4 sm:px-5 py-3 border-b border-gray-100 bg-gray-50/80">
            <h3 class="text-sm font-semibold text-gray-800">{{ mod.label }}</h3>
          </header>

          <!-- 图表区域（懒渲染） -->
          <div class="p-3 sm:p-4" style="min-height: 320px">
            <template v-if="mounted[mod.key]">
              <WindSpeedLineChart
                v-if="mod.key === 'basic'"
                :data="result.basicStats[heightKey]"
                :height="parseInt(heightKey)"
              />
              <WindRoseChart
                v-else-if="mod.key === 'windrose'"
                :data="result.windRoseData[heightKey]"
                :height="parseInt(heightKey)"
              />
              <WeibullChart
                v-else-if="mod.key === 'weibull'"
                :data="result.weibullResults[heightKey]"
                :height="parseInt(heightKey)"
              />
              <WpdChart
                v-else-if="mod.key === 'wpd'"
                :data="result.wpdResults[heightKey]"
                :height="parseInt(heightKey)"
              />
              <ShearProfileChart
                v-else-if="mod.key === 'shear' && result.shearResult"
                :data="result.shearResult"
              />
              <div
                v-else-if="mod.key === 'shear'"
                class="flex items-center justify-center text-sm text-gray-400 py-20"
              >
                多高度数据不足，无法计算风切变
              </div>
              <TurbulenceChart
                v-else-if="mod.key === 'turbulence'"
                :data="result.turbulenceData[heightKey]"
                :height="parseInt(heightKey)"
              />
              <ExtremeWindChart
                v-else-if="mod.key === 'extreme'"
                :data="result.extremeWindResults[heightKey]"
                :height="parseInt(heightKey)"
              />
              <RepYearChart
                v-else-if="mod.key === 'repyear'"
                :data="result.representativeYearResults[heightKey]"
                :height="parseInt(heightKey)"
              />
              <MultiHeightCompare
                v-else-if="mod.key === 'compare'"
                :result="result"
              />
            </template>
            <!-- 占位：卡片尚未进入视口 -->
            <div v-else class="flex items-center justify-center h-full py-24 text-gray-300 text-xs gap-1.5">
              <svg class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              滚动至此处加载图表
            </div>
          </div>
        </section>
      </div>
    </template>
</template>
