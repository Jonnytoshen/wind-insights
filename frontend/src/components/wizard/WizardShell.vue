<script setup lang="ts">
import { computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useWizardStore } from '@/stores/wizard'
import Step1Location from '@/views/Step1Location.vue'
import Step2Params from '@/views/Step2Params.vue'
import Step3Loading from '@/views/Step3Loading.vue'
import Step4Overview from '@/views/Step4Overview.vue'
import Step5Analysis from '@/views/Step5Analysis.vue'
import Step6Report from '@/views/Step6Report.vue'

const wizardStore = useWizardStore()
const { currentStep, canGoNext } = storeToRefs(wizardStore)

const steps = [
  { label: '选择点位', icon: '📍' },
  { label: '配置参数', icon: '⚙️' },
  { label: '数据加载', icon: '📡' },
  { label: '分析总览', icon: '📊' },
  { label: '详细分析', icon: '🔍' },
  { label: '生成报告', icon: '📄' },
]

const stepComponents = [
  Step1Location,
  Step2Params,
  Step3Loading,
  Step4Overview,
  Step5Analysis,
  Step6Report,
]

const currentComponent = computed(() => stepComponents[currentStep.value])

const isFirstStep = computed(() => currentStep.value === 0)
const isLastStep = computed(() => currentStep.value === 5)
// 数据加载步骤（步骤 2，索引为 2）由数据加载完成后自动跳转，不显示导航按钮
const showNavButtons = computed(() => currentStep.value !== 2)

watch(currentStep, () => wizardStore.persist())
</script>

<template>
  <div class="flex flex-col flex-1">
    <!-- 步骤条 -->
    <div class="bg-white border-b border-gray-100 px-6 py-4">
      <ol class="flex items-center justify-center gap-0">
        <template v-for="(step, idx) in steps" :key="idx">
          <li class="flex items-center">
            <button
              class="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-colors"
              :class="{
                'bg-blue-600 text-white font-semibold': idx === currentStep,
                'text-blue-600 cursor-pointer hover:bg-blue-50': idx < currentStep,
                'text-gray-400 cursor-default': idx > currentStep,
              }"
              :disabled="idx > currentStep"
              @click="idx < currentStep && wizardStore.goToStep(idx)"
            >
              <span>{{ step.icon }}</span>
              <span class="hidden sm:inline">{{ step.label }}</span>
            </button>
          </li>
          <li v-if="idx < steps.length - 1" class="w-6 h-px bg-gray-200 mx-1" />
        </template>
      </ol>
    </div>

    <!-- 步骤内容 -->
    <div class="flex-1 overflow-auto">
      <component :is="currentComponent" />
    </div>

    <!-- 底部导航按钮 -->
    <div
      v-if="showNavButtons"
      class="bg-white border-t border-gray-100 px-6 py-4 flex items-center justify-between"
    >
      <button
        class="px-6 py-2 rounded-lg border border-gray-300 text-gray-600 text-sm hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="isFirstStep"
        @click="wizardStore.prevStep()"
      >
        ← 上一步
      </button>

      <button
        class="px-6 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="!canGoNext"
        @click="wizardStore.nextStep()"
      >
        {{ isLastStep ? '完成' : '下一步 →' }}
      </button>
    </div>
  </div>
</template>
