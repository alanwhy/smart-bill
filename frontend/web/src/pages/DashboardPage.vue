<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <!-- 顶部操作栏 -->
    <div class="sticky top-0 z-30 bg-surface border-b border-border">
      <div class="px-4 sm:px-6 lg:px-8 py-4 space-y-4 sm:space-y-0 sm:flex sm:items-center sm:justify-between">
        <!-- 统计信息 -->
        <div class="flex items-center gap-4">
          <div class="flex flex-col">
            <p class="text-xs text-text-muted uppercase tracking-wider">本月支出</p>
            <p class="text-2xl font-bold text-primary">¥{{ totalExpense.toFixed(2) }}</p>
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
    <transition name="slide">
      <div
        v-if="isFilterSheetOpen"
        class="fixed inset-0 z-40 lg:hidden"
      >
        <!-- 背景 -->
        <div
          @click="closeFilterSheet"
          class="absolute inset-0 bg-black/50"
        />

        <!-- 筛选面板 -->
        <div class="absolute bottom-0 left-0 right-0 bg-surface border-t border-border rounded-t-2xl p-6 animate-in slide-in-from-bottom">
          <BillFilters @apply="applyFilters" @close="closeFilterSheet" />
        </div>
      </div>
    </transition>

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
      <div v-else class="space-y-3">
        <BillCard
          v-for="bill in billsStore.bills"
          :key="bill.id"
          :bill="bill"
          @edit="(b) => editBill(b)"
          @delete="(b) => deleteBill(b)"
        />
      </div>
    </div>

    <!-- 上传模态框 -->
    <BillUploadModal
      v-if="showUploadModal"
      @close="showUploadModal = false"
      @success="onUploadSuccess"
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
import BillCard from '@/components/bills/BillCard.vue'
import BillFilters from '@/components/bills/BillFilters.vue'
import BillUploadModal from '@/components/bills/BillUploadModal.vue'
import BillEditModal from '@/components/bills/BillEditModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import Toast from '@/components/common/Toast.vue'

const billsStore = useBillsStore()
const uiStore = useUiStore()
const authStore = useAuthStore()

const showUploadModal = ref(false)
const editingBill = ref<BillRecord | null>(null)
const deletingBillId = ref<number | null>(null)
const toastMessage = ref<string | null>(null)

const isLoading = computed(() => billsStore.isLoading)
const totalExpense = computed(() => billsStore.totalExpense)

const isFilterSheetOpen = computed(() => uiStore.isFilterSheetOpen)

// 生命周期
onMounted(async () => {
  if (!authStore.userId) return
  await billsStore.fetchBills(authStore.userId)
})

// 方法
const applyFilters = async () => {
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

const onUploadSuccess = () => {
  showUploadModal.value = false
}

const onBillUpdated = () => {
  editingBill.value = null
}
</script>
