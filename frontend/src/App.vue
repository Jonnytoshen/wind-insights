<script setup lang="ts">
import { onMounted } from 'vue'
import WizardShell from '@/components/wizard/WizardShell.vue'
import { useWizardStore } from '@/stores/wizard'

const wizardStore = useWizardStore()
onMounted(() => wizardStore.restore())
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部导航栏 -->
    <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🌬️</span>
        <span class="text-xl font-semibold text-gray-800">Wind Insights</span>
        <span class="text-xs text-gray-400 ml-2">基于 MERRA-2 的虚拟测风塔分析平台</span>
      </div>
      <nav class="flex items-center gap-4 text-sm text-gray-600">
        <span>历史记录</span>
        <span class="text-gray-300">|</span>
        <span>帮助</span>
      </nav>
    </header>

    <!-- 主内容区 -->
    <main class="flex-1 flex flex-col">
      <WizardShell />
    </main>
  </div>
</template>
