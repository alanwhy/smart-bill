<template>
  <div class="min-h-full pb-20 lg:pb-0" style="padding-bottom: calc(5rem + env(safe-area-inset-bottom))">
    <!-- 桌面端窗口过窄提示 Banner -->
    <Transition name="banner">
      <div
        v-if="showNarrowBanner"
        class="flex items-center justify-between gap-3 px-4 py-2 bg-warning/15 border-b border-warning/30 text-warning text-sm"
      >
        <span class="flex items-center gap-2">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M4.929 4.929l14.142 14.142M12 2a10 10 0 110 20A10 10 0 0112 2z" />
          </svg>
          当前窗口较窄，建议放大窗口以获得更好的桌面体验
        </span>
        <button
          @click="dismissNarrowBanner"
          class="flex-shrink-0 p-1 rounded hover:bg-warning/20 transition-colors"
          aria-label="关闭提示"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </Transition>

    <!-- 顶部操作栏 -->
    <div class="sticky top-0 z-30 bg-surface border-b border-border">
      <div class="px-4 sm:px-6 lg:px-8 py-4 space-y-4 sm:space-y-0 sm:flex sm:items-center sm:justify-between">
        <!-- 统计信息 -->
        <div class="flex items-center gap-4">
          <div class="flex flex-col">
            <p class="text-xs text-text-muted uppercase tracking-wider">{{ expenseLabel }}</p>
            <p class="text-2xl font-bold text-primary">¥{{ totalExpense.toFixed(2) }}</p>
          </div>
          <div v-if="totalIncome > 0" class="flex flex-col">
            <p class="text-xs text-text-muted uppercase tracking-wider">收入</p>
            <p class="text-2xl font-bold text-success">+¥{{ totalIncome.toFixed(2) }}</p>
          </div>
          <!-- 周期快捷按钮 -->
          <div class="flex gap-1 ml-2">
            <button
              @click="switchCycle(0)"
              :class="[
                'px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150',
                cycleOffset === 0
                  ? 'bg-primary text-white'
                  : 'bg-surface border border-border text-text-secondary hover:border-primary/50',
              ]"
            >
              本期
            </button>
            <button
              @click="switchCycle(-1)"
              :class="[
                'px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150',
                cycleOffset === -1
                  ? 'bg-primary text-white'
                  : 'bg-surface border border-border text-text-secondary hover:border-primary/50',
              ]"
            >
              上期
            </button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-3">
          <button
            @click="openFilterSheet"
            class="btn btn-secondary btn-sm lg:hidden"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span>筛选</span>
          </button>
          <button
            @click="showCreateModal = true"
            class="btn btn-secondary btn-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <span>录入</span>
          </button>
          <button
            @click="showUploadModal = true"
            class="btn btn-primary btn-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>上传</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 筛选面板（移动端） -->
    <Teleport to="body">
      <Transition name="overlay">
        <div
          v-if="isFilterSheetOpen"
          class="fixed inset-0 z-40 lg:hidden bg-black/50"
          @click="closeFilterSheet"
        />
      </Transition>
      <Transition name="slide">
        <div
          v-if="isFilterSheetOpen"
          class="fixed bottom-0 left-0 right-0 z-40 lg:hidden bg-surface border-t border-border rounded-t-2xl p-6"
        >
          <BillFilters @apply="applyFilters" @close="closeFilterSheet" />
        </div>
      </Transition>
    </Teleport>

    <!-- 筛选栏（桌面端） -->
    <div class="hidden lg:block px-8 py-4 border-b border-border bg-surface/50">
      <BillFilters @apply="applyFilters" />
    </div>

    <!-- 账单列表 -->
    <div class="px-4 sm:px-6 lg:px-8 py-6">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="card h-24 animate-pulse bg-surface/50" />
      </div>

      <!-- 空状态 -->
      <div v-else-if="billsStore.bills.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-text-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="text-lg font-semibold text-text mb-2">还没有账单</h3>
        <p class="text-text-muted mb-6">上传账单图片开始记账</p>
        <button
          @click="showUploadModal = true"
          class="btn btn-primary"
        >
          上传第一张账单
        </button>
      </div>

      <!-- 账单列表 -->
      <TransitionGroup v-else name="bill-list" tag="div" class="space-y-3">
        <BillCard
          v-for="(bill, index) in billsStore.bills"
          :key="bill.id"
          :bill="bill"
          :style="{ transitionDelay: `${index * 35}ms` }"
          @edit="(b) => editBill(b)"
          @delete="(b) => deleteBill(b)"
        />
      </TransitionGroup>
    </div>

    <!-- 上传模态框 -->
    <BillUploadModal
      v-if="showUploadModal"
      @close="showUploadModal = false"
      @success="onUploadSuccess"
    />

    <!-- 手动录入模态框 -->
    <BillEditModal
      v-if="showCreateModal"
      mode="create"
      @close="showCreateModal = false"
      @update="onBillCreated"
    />

    <!-- 编辑模态框 -->
    <BillEditModal
      v-if="editingBill"
      :bill="editingBill"
      @close="editingBill = null"
      @update="onBillUpdated"
    />

    <!-- 删除确认弹窗 -->
    <ConfirmDialog
      v-if="deletingBillId !== null"
      title="删除账单"
      message="确定删除这条账单吗？此操作无法撤销。"
      confirm-label="删除"
      :danger="true"
      @confirm="confirmDelete"
      @cancel="deletingBillId = null"
    />
    <!-- 错误提示 -->
    <Toast
      v-if="toastMessage"
      :message="toastMessage"
      type="error"
      @close="toastMessage = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBillsStore } from '@/stores/bills'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import type { BillRecord } from '@/types/bill'
import { getCycleDates } from '@/utils/cycle'
import BillCard from '@/components/bills/BillCard.vue'
import BillFilters from '@/components/bills/BillFilters.vue'
import BillUploadModal from '@/components/bills/BillUploadModal.vue'
import BillEditModal from '@/components/bills/BillEditModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import Toast from '@/components/common/Toast.vue'
import { useDevice } from '@/utils/useDevice'

const { isDesktop, isViewportTooSmall } = useDevice()
// 本会话是否已手动关闭窄屏 Banner
const narrowBannerDismissed = ref(
  typeof sessionStorage !== 'undefined' && sessionStorage.getItem('narrowBannerDismissed') === '1'
)
const showNarrowBanner = computed(() => isDesktop.value && isViewportTooSmall.value && !narrowBannerDismissed.value)
function dismissNarrowBanner() {
  narrowBannerDismissed.value = true
  sessionStorage.setItem('narrowBannerDismissed', '1')
}

const billsStore = useBillsStore()
const uiStore = useUiStore()
const authStore = useAuthStore()

const showUploadModal = ref(false)
const showCreateModal = ref(false)
const editingBill = ref<BillRecord | null>(null)
const deletingBillId = ref<number | null>(null)
const toastMessage = ref<string | null>(null)

// 当前周期偏移：0=本期，-1=上期，null=自定义
const cycleOffset = ref<0 | -1 | null>(0)

const isLoading = computed(() => billsStore.isLoading)
const totalExpense = computed(() => billsStore.totalExpense)
const totalIncome = computed(() => billsStore.totalIncome)
const isFilterSheetOpen = computed(() => uiStore.isFilterSheetOpen)

const expenseLabel = computed(() => {
  if (cycleOffset.value === null) return '自定义支出'
  return getCycleDates(authStore.cycleStartDay, cycleOffset.value).label
})

// 生命周期
onMounted(async () => {
  if (!authStore.userId) return
  // 先拉取周期设置，再初始化日期范围
  await authStore.fetchCycle()
  const { startDate, endDate } = getCycleDates(authStore.cycleStartDay, 0)
  uiStore.setFilters({ startDate, endDate })
  await billsStore.fetchBills(authStore.userId, uiStore.filters)
})

// 方法
const switchCycle = async (offset: 0 | -1) => {
  cycleOffset.value = offset
  const { startDate, endDate } = getCycleDates(authStore.cycleStartDay, offset)
  uiStore.setFilters({ startDate, endDate, category_id: undefined, searchText: undefined })
  if (!authStore.userId) return
  await billsStore.fetchBills(authStore.userId, uiStore.filters)
}

const applyFilters = async () => {
  // 手动筛选时取消周期快捷按钮高亮
  cycleOffset.value = null
  if (!authStore.userId) return
  await billsStore.fetchBills(authStore.userId, uiStore.filters)
  uiStore.closeFilterSheet()
}

const openFilterSheet = () => {
  uiStore.openFilterSheet()
}

const closeFilterSheet = () => {
  uiStore.closeFilterSheet()
}

const editBill = (bill: BillRecord) => {
  editingBill.value = bill
}

const deleteBill = (bill: BillRecord) => {
  deletingBillId.value = bill.id
}

const confirmDelete = async () => {
  if (deletingBillId.value === null) return
  try {
    await billsStore.deleteBill(deletingBillId.value)
  } catch (e) {
    toastMessage.value = `删除失败: ${(e as Error).message}`
  } finally {
    deletingBillId.value = null
  }
}

const onUploadSuccess = (fileCount: number) => {
  showUploadModal.value = false
  billsStore.addPlaceholders(fileCount)
  billsStore.startPolling(authStore.userId!, fileCount, uiStore.filters)
}

const onBillCreated = () => {
  showCreateModal.value = false
}

const onBillUpdated = () => {
  editingBill.value = null
}
</script>

<style scoped>
.banner-enter-active,
.banner-leave-active {
  transition: max-height 0.25s ease, opacity 0.2s ease;
  overflow: hidden;
}
.banner-enter-from,
.banner-leave-to {
  max-height: 0;
  opacity: 0;
}
.banner-enter-to,
.banner-leave-from {
  max-height: 60px;
  opacity: 1;
}
</style>
