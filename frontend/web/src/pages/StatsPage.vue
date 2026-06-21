<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <!-- 顶部操作栏 -->
    <div class="sticky top-0 z-30 bg-surface border-b border-border">
      <div class="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
        <!-- 标题 + 周期快捷按钮 -->
        <div class="flex items-center gap-3">
          <h2 class="text-lg font-bold text-text hidden lg:block">数据统计</h2>
          <div class="flex gap-1">
            <button
              @click="switchCycle(0)"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150"
              :class="cycleOffset === 0 ? 'bg-primary text-white' : 'bg-surface border border-border text-text-secondary hover:border-primary/50'"
            >
              本期
            </button>
            <button
              @click="switchCycle(-1)"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150"
              :class="cycleOffset === -1 ? 'bg-primary text-white' : 'bg-surface border border-border text-text-secondary hover:border-primary/50'"
            >
              上期
            </button>
          </div>
          <!-- 汇总数字 -->
          <div class="flex items-center gap-3 pl-2 border-l border-border">
            <div class="flex flex-col">
              <p class="text-xs text-text-muted">支出</p>
              <p class="text-base font-bold text-primary leading-tight">¥{{ statsStore.totalExpense.toFixed(2) }}</p>
            </div>
            <div v-if="statsStore.totalIncome > 0" class="flex flex-col">
              <p class="text-xs text-text-muted">收入</p>
              <p class="text-base font-bold text-success leading-tight">+¥{{ statsStore.totalIncome.toFixed(2) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选栏（桌面端，与 Dashboard 风格一致） -->
    <div class="hidden lg:block px-8 py-4 border-b border-border bg-surface/50">
      <BillFilters
        :external-filters="statsFilters"
        @apply="onFiltersApply"
        @update:external-filters="onExternalFiltersUpdate"
      />
    </div>

    <!-- 移动端提示（lt:lg 显示） -->
    <div class="lg:hidden flex flex-col items-center justify-center py-20 px-6 text-center">
      <svg class="w-16 h-16 text-text-muted mb-4 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <p class="text-text-muted text-sm">请在桌面端查看数据统计</p>
    </div>

    <!-- PC 端图表区域 -->
    <div class="hidden lg:block px-8 py-6">
      <!-- 加载中 -->
      <div v-if="statsStore.isLoading" class="grid grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="card h-80 animate-pulse bg-surface/50" />
      </div>

      <!-- 图表三栏 -->
      <div v-else class="grid grid-cols-3 gap-6 items-stretch">
        <PieChart
          :data="statsStore.statsByRootCategory"
          :total-expense="statsStore.totalExpense"
          :total-income="statsStore.totalIncome"
        />
        <TrendChart :data="statsStore.trendByDay" />
        <RankChart :data="statsStore.topMerchants" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useStatsStore } from '@/stores/stats'
import { getCycleDates } from '@/utils/cycle'
import BillFilters from '@/components/bills/BillFilters.vue'
import PieChart from '@/components/stats/PieChart.vue'
import TrendChart from '@/components/stats/TrendChart.vue'
import RankChart from '@/components/stats/RankChart.vue'
import type { StatsFilter } from '@/stores/stats'

const authStore = useAuthStore()
const statsStore = useStatsStore()

const cycleOffset = ref<0 | -1 | null>(0)
const statsFilters = reactive<StatsFilter>({
  startDate: undefined,
  endDate: undefined,
  category_ids: undefined,
  searchText: undefined,
})

async function loadData() {
  if (!authStore.userId) return
  await statsStore.fetchBills(authStore.userId, { ...statsFilters })
}

async function switchCycle(offset: 0 | -1) {
  cycleOffset.value = offset
  const { startDate, endDate } = getCycleDates(authStore.cycleStartDay, offset)
  statsFilters.startDate = startDate
  statsFilters.endDate = endDate
  statsFilters.category_ids = undefined
  statsFilters.searchText = undefined
  await loadData()
}

function onExternalFiltersUpdate(newFilters: StatsFilter | undefined) {
  if (!newFilters) return
  Object.assign(statsFilters, {
    startDate: newFilters.startDate,
    endDate: newFilters.endDate,
    category_ids: newFilters.category_ids,
    searchText: newFilters.searchText,
  })
}

async function onFiltersApply() {
  cycleOffset.value = null
  await loadData()
}

onMounted(async () => {
  await authStore.fetchCycle()
  const { startDate, endDate } = getCycleDates(authStore.cycleStartDay, 0)
  statsFilters.startDate = startDate
  statsFilters.endDate = endDate
  await loadData()
})
</script>
