<template>
  <Teleport to="body">
    <!-- 背景蒙层 -->
    <Transition name="overlay">
      <div v-show="visible" class="fixed inset-0 z-50 bg-black/50" @click="isMobile ? handleMobileClose() : emit('close')" />
    </Transition>
    <!-- 模态框（移动端：底部 bottom sheet；PC 端：居中 modal） -->
    <div class="fixed inset-0 z-50 flex items-end sm:items-center p-0 sm:p-4 pointer-events-none">
      <Transition :name="isMobile ? 'slide' : 'modal'" appear>
        <!-- 移动端：全宽、顶部圆角、flex-col 可滚动；PC 端：还原原始居中 modal 样式 -->
        <div v-show="visible" class="bg-surface w-full pointer-events-auto
          rounded-t-2xl max-h-[90dvh] flex flex-col overflow-hidden
          sm:rounded-2xl sm:max-w-lg sm:max-h-none sm:flex-none sm:overflow-visible sm:mx-auto shadow-xl"
          @touchstart.passive="onDragStart"
          @touchend.passive="onDragEnd"
        >
          <!-- 移动端拖动指示条（点击关闭） -->
          <div
            class="sm:hidden flex-shrink-0 flex justify-center pt-3 pb-2 cursor-pointer"
            @click="handleMobileClose"
          >
            <div class="w-10 h-1 bg-border rounded-full"></div>
          </div>
          <!-- 头部 -->
          <div class="border-b border-border px-6 py-4 sm:flex-shrink-0 flex items-center justify-between">
            <h2 class="text-xl font-bold text-text">{{ mode === 'create' ? '手动录入账单' : '编辑账单' }}</h2>
            <!-- 关闭按钮仅 PC 端显示；移动端通过下滑遮罩关闭 -->
            <button
              @click="emit('close')"
              class="hidden sm:block p-2 hover:bg-border rounded-lg transition-colors duration-200"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

      <!-- 内容（移动端可滚动；PC 端随内容撑高） -->
      <div ref="scrollRef" class="p-6 space-y-4 overflow-y-auto flex-1 sm:overflow-visible sm:flex-none">
        <!-- 金额（负数=支出，正数=收入） -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">
            金额
            <span class="text-xs font-normal text-text-muted ml-1">（负数为支出）</span>
          </label>
          <input
            v-model.number="formData.amount"
            type="number"
            step="0.01"
            class="input"
            placeholder="0.00"
          />
        </div>

        <!-- 商户名称 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">商户名称</label>
          <input
            v-model="formData.merchant_name"
            type="text"
            class="input"
            placeholder="输入商户名称"
          />
        </div>

        <!-- 分类 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">分类</label>
          <p v-if="categoriesStore.isLoading && categories.length === 0" class="text-xs text-text-muted">加载中...</p>
          <div v-else class="grid grid-cols-3 gap-2">
            <button
              v-for="cat in categories"
              :key="cat.id"
              @click="formData.category_id = cat.id"
              :class="[
                'p-3 rounded-lg border-2 transition-all duration-200',
                formData.category_id === cat.id
                  ? 'border-primary bg-primary/10'
                  : 'border-border bg-surface hover:border-primary/50',
              ]"
            >
              <div class="text-lg mb-1">{{ cat.icon }}</div>
              <div class="text-xs text-text-secondary">{{ cat.name }}</div>
            </button>
          </div>
        </div>

        <!-- 交易日期 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">交易日期</label>
          <input
            v-model="formData.transaction_date"
            type="datetime-local"
            class="input"
          />
        </div>

        <!-- 备注 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">备注</label>
          <textarea
            v-model="formData.description"
            :maxlength="100"
            rows="2"
            placeholder="可选，最多 100 字"
            class="input resize-none"
          />
          <p class="text-xs text-text-muted mt-1 text-right">{{ (formData.description || '').length }}/100</p>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="p-3 bg-error/10 border border-error/30 rounded-lg">
          <p class="text-sm text-error">{{ errorMessage }}</p>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="border-t border-border px-6 py-4 flex flex-col gap-2 flex-shrink-0 sm:flex-row sm:justify-end">
        <button
          @click="handleSubmit"
          :disabled="isSubmitting"
          class="btn btn-primary py-3 sm:py-2 text-base sm:text-sm"
        >
          {{ isSubmitting ? '保存中...' : (mode === 'create' ? '确认录入' : '确认修改') }}
        </button>
        <button
          @click="isMobile ? handleMobileClose() : emit('close')"
          :disabled="isSubmitting"
          class="btn btn-secondary py-3 sm:py-2 text-base sm:text-sm"
        >
          取消
        </button>
      </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useBillsStore } from '@/stores/bills'
import { useCategoriesStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import type { BillRecord } from '@/types/bill'
import { format, parseISO } from 'date-fns'

const props = withDefaults(
  defineProps<{
    bill?: BillRecord
    mode?: 'create' | 'edit'
  }>(),
  { mode: 'edit' },
)

const emit = defineEmits<{
  close: []
  update: []
}>()

const billsStore = useBillsStore()
const categoriesStore = useCategoriesStore()
const authStore = useAuthStore()

// 移动端检测：根据视口宽度判断（< 640px 即 Tailwind sm: 断点）
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
const isMobile = computed(() => windowWidth.value < 640)
function onResize() { windowWidth.value = window.innerWidth }
onMounted(() => window.addEventListener('resize', onResize, { passive: true }))
onUnmounted(() => window.removeEventListener('resize', onResize))

const categories = computed(() => categoriesStore.sortedCategories)

const isSubmitting = ref(false)
const errorMessage = ref('')

function todayDatetimeLocal(): string {
  return format(new Date(), "yyyy-MM-dd'T'HH:mm")
}

function convertToDatetimeLocal(dateStr: string): string {
  try {
    const date = parseISO(dateStr)
    return format(date, "yyyy-MM-dd'T'HH:mm")
  } catch {
    return dateStr
  }
}

const formData = reactive({
  type: (props.bill && props.bill.value > 0 ? 'income' : 'expense') as 'expense' | 'income',
  // 金额保留原始正负号（负=支出）
  amount: props.bill ? props.bill.value : 0,
  merchant_name: props.bill?.merchant_name ?? '',
  category_id: props.bill?.category_id ?? 0,
  transaction_date: props.bill
    ? convertToDatetimeLocal(props.bill.transaction_date)
    : todayDatetimeLocal(),
  description: props.bill?.description ?? '',
})

onMounted(() => {
  categoriesStore.getOrFetch()
})

const scrollRef = ref<HTMLElement | null>(null)

// 移动端下滑关闭：先播放 leave 动画（~260ms）再 emit close
const visible = ref(true)
function handleMobileClose() {
  if (!isMobile.value) { emit('close'); return }
  visible.value = false
  setTimeout(() => emit('close'), 280)
}

// touch 拖动下滑关闭：仅当内容已滚到顶部时触发
let dragStartY = 0
function onDragStart(e: TouchEvent) { dragStartY = e.touches[0].clientY }
function onDragEnd(e: TouchEvent) {
  const dy = e.changedTouches[0].clientY - dragStartY
  const atTop = !scrollRef.value || scrollRef.value.scrollTop === 0
  if (dy > 60 && atTop) handleMobileClose()
}

const handleSubmit = async () => {
  errorMessage.value = ''

  if (!formData.merchant_name.trim()) {
    errorMessage.value = '请输入商户名称'
    return
  }

  if (!formData.amount || formData.amount === 0) {
    errorMessage.value = '金额不能为 0'
    return
  }

  if (!formData.category_id) {
    errorMessage.value = '请选择分类'
    return
  }

  // 金额直接作为 value（负数=支出，正数=收入）
  const signedValue = formData.amount

  isSubmitting.value = true

  try {
    if (props.mode === 'create') {
      await billsStore.createBill({
        user_id: authStore.userId!,
        value: signedValue,
        merchant_name: formData.merchant_name,
        category_id: formData.category_id,
        transaction_date: new Date(formData.transaction_date).toISOString(),
        description: formData.description || undefined,
      })
    } else {
      await billsStore.updateBill(props.bill!.id, {
        value: signedValue,
        merchant_name: formData.merchant_name,
        category_id: formData.category_id,
        transaction_date: new Date(formData.transaction_date).toISOString(),
        description: formData.description || undefined,
      })
    }

    emit('update')
  } catch (e) {
    errorMessage.value = (e as Error).message
  } finally {
    isSubmitting.value = false
  }
}
</script>
