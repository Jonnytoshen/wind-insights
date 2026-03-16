<script setup lang="ts">
import { computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useWizardStore } from '@/stores/wizard'
import AppIcon from '@/components/AppIcon.vue'
import Step1Location from '@/views/Step1Location.vue'
import Step2Params from '@/views/Step2Params.vue'
import Step3Loading from '@/views/Step3Loading.vue'
import Step4Overview from '@/views/Step4Overview.vue'
import Step5Analysis from '@/views/Step5Analysis.vue'
import Step6Report from '@/views/Step6Report.vue'

const wizardStore = useWizardStore()
const { currentStep, canGoNext } = storeToRefs(wizardStore)

const steps = [
  { label: '选择点位', icon: 'map-pin' },
  { label: '配置参数', icon: 'settings' },
  { label: '数据加载', icon: 'signal' },
  { label: '分析总览', icon: 'bar-chart' },
  { label: '详细分析', icon: 'search' },
  { label: '生成报告', icon: 'document' },
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
  <div class="flex flex-col flex-1 min-h-0">
    <!-- 步骤条 -->
    <div class="bg-white border-b border-gray-100 px-2 sm:px-4 py-3 overflow-x-auto">
      <ol class="flex items-center justify-start sm:justify-center gap-0 min-w-max sm:min-w-0">
        <template v-for="(step, idx) in steps" :key="idx">
          <li class="flex items-center">
            <button
              class="flex items-center gap-1.5 px-2 sm:px-3 py-1.5 rounded-full text-xs sm:text-sm transition-colors"
              :class="{
                'bg-blue-600 text-white font-semibold': idx === currentStep,
                'text-blue-600 cursor-pointer hover:bg-blue-50': idx < currentStep,
                'text-gray-400 cursor-default': idx > currentStep,
              }"
              :disabled="idx > currentStep"
              @click="idx < currentStep && wizardStore.goToStep(idx)"
            >
              <AppIcon :name="step.icon" class="w-4 h-4 shrink-0" />
              <span class="hidden sm:inline">{{ step.label }}</span>
            </button>
          </li>
          <li v-if="idx < steps.length - 1" class="w-4 sm:w-6 h-px bg-gray-200 mx-0.5 sm:mx-1 shrink-0" />
        </template>
      </ol>
    </div>

    <!-- 步骤内容 -->
    <div class="flex-1 overflow-auto min-h-0">
      <component :is="currentComponent" />
    </div>

    <!-- 底部导航按钮 -->
    <div
      v-if="showNavButtons"
      class="bg-white border-t border-gray-100 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-3"
    >
      <button
        class="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-4 sm:px-6 py-2.5 rounded-lg border border-gray-300 text-gray-600 text-sm hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="isFirstStep"
        @click="wizardStore.prevStep()"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
        </svg>
        上一步
      </button>

      <button
        class="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-4 sm:px-6 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="!canGoNext"
        @click="wizardStore.nextStep()"
      >
        {{ isLastStep ? '完成' : '下一步' }}
        <svg v-if="!isLastStep" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M3 10a.75.75 0 0 1 .75-.75h10.638L10.23 5.29a.75.75 0 1 1 1.04-1.08l5.5 5.25a.75.75 0 0 1 0 1.08l-5.5 5.25a.75.75 0 1 1-1.04-1.08l4.158-3.96H3.75A.75.75 0 0 1 3 10Z" clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
</template>
