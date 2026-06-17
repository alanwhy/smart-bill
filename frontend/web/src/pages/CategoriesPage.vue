<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold text-text mb-2">分类管理</h1>
          <p class="text-text-muted">维护账单分类，全部用户共用同一份分类</p>
        </div>
        <button @click="openCreate" class="btn btn-primary">新建分类</button>
      </div>

      <!-- 列表 -->
      <div v-if="isLoading && categories.length === 0" class="space-y-3">
        <div v-for="i in 3" :key="i" class="card h-20 animate-pulse bg-surface/50" />
      </div>
      <div v-else-if="categories.length === 0" class="text-center py-12 text-text-muted">
        暂无分类，点击右上角新建一个吧
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="card p-4 flex items-center gap-4"
        >
          <div
            class="flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
            :style="{ backgroundColor: cat.color + '22' }"
          >
            {{ cat.icon || '📦' }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-semibold text-text truncate">{{ cat.name }}</h3>
              <span class="text-[10px] px-1.5 py-0.5 rounded text-text-muted bg-surface border border-border">
                #{{ cat.sort_order }}
              </span>
            </div>
            <div class="flex items-center gap-2 mt-1">
              <span
                class="inline-block w-3 h-3 rounded-full border border-border"
                :style="{ backgroundColor: cat.color }"
              />
              <span class="text-xs text-text-muted">{{ cat.color }}</span>
            </div>
          </div>
          <div class="flex gap-1">
            <button
              @click="openEdit(cat)"
              class="p-2 hover:bg-surface rounded-lg transition-colors duration-200"
              title="编辑"
            >
              <svg class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click="handleDelete(cat)"
              class="p-2 hover:bg-error/10 rounded-lg transition-colors duration-200"
              title="删除"
            >
              <svg class="w-4 h-4 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑/新建模态 -->    <div v-if="modalOpen" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div class="bg-surface rounded-2xl shadow-xl w-full max-w-md">
        <div class="border-b border-border px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold text-text">{{ editingId ? '编辑分类' : '新建分类' }}</h2>
          <button @click="closeModal" class="p-2 hover:bg-border rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-text mb-2">名称</label>
            <input v-model="form.name" type="text" class="input" placeholder="分类名称" maxlength="50" />
          </div>
          <div>
            <label class="block text-sm font-medium text-text mb-2">图标 (emoji)</label>
            <input v-model="form.icon" type="text" class="input" placeholder="🍽️" maxlength="16" />
          </div>
          <div>
            <label class="block text-sm font-medium text-text mb-2">颜色</label>
            <div class="flex items-center gap-3">
              <input v-model="form.color" type="color" class="h-10 w-16 rounded-lg border border-border bg-surface cursor-pointer" />
              <input v-model="form.color" type="text" class="input flex-1 font-mono text-sm" placeholder="#6B7280" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-text mb-2">排序权重</label>
            <input v-model.number="form.sort_order" type="number" min="0" class="input" placeholder="数值越小越靠前" />
          </div>

          <div v-if="modalError" class="p-3 bg-error/10 border border-error/30 rounded-lg">
            <p class="text-sm text-error">{{ modalError }}</p>
          </div>
        </div>

        <div class="border-t border-border px-6 py-4 flex gap-2 justify-end">
          <button @click="closeModal" :disabled="isSubmitting" class="btn btn-secondary">取消</button>
          <button @click="handleSubmit" :disabled="isSubmitting" class="btn btn-primary">
            {{ isSubmitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
    <!-- 删除确认弹窗 -->
    <ConfirmDialog
      v-if="deletingCategory !== null"
      title="删除分类"
      :message="`确定删除分类「${deletingCategory?.name}」吗？此操作无法撤销。`"
      confirm-label="删除"
      :danger="true"
      @confirm="confirmDelete"
      @cancel="deletingCategory = null"
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import type { Category } from '@/types/bill'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import Toast from '@/components/common/Toast.vue'

const categoriesStore = useCategoriesStore()

const categories = computed(() => categoriesStore.sortedCategories)
const isLoading = computed(() => categoriesStore.isLoading)

const toastMessage = ref<string | null>(null)
const deletingCategory = ref<Category | null>(null)

const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const isSubmitting = ref(false)
const modalError = ref('')

const form = reactive({
  name: '',
  icon: '',
  color: '#6B7280',
  sort_order: 0 as number | undefined,
})

onMounted(() => {
  categoriesStore.getOrFetch()
})

const openCreate = () => {
  editingId.value = null
  form.name = ''
  form.icon = ''
  form.color = '#6B7280'
  // 新建时让后端默认追加在末尾
  form.sort_order = undefined
  modalError.value = ''
  modalOpen.value = true
}

const openEdit = (cat: Category) => {
  editingId.value = cat.id
  form.name = cat.name
  form.icon = cat.icon
  form.color = cat.color
  form.sort_order = cat.sort_order
  modalError.value = ''
  modalOpen.value = true
}

const closeModal = () => {
  if (isSubmitting.value) return
  modalOpen.value = false
}

const HEX_RE = /^#[0-9A-Fa-f]{6}$/

const handleSubmit = async () => {
  modalError.value = ''
  if (!form.name.trim()) {
    modalError.value = '名称不能为空'
    return
  }
  if (!HEX_RE.test(form.color)) {
    modalError.value = '颜色必须是 #RRGGBB 格式'
    return
  }
  isSubmitting.value = true
  try {
    if (editingId.value) {
      await categoriesStore.updateCategory(editingId.value, {
        name: form.name.trim(),
        icon: form.icon,
        color: form.color,
        sort_order: form.sort_order,
      })
    } else {
      await categoriesStore.createCategory({
        name: form.name.trim(),
        icon: form.icon,
        color: form.color,
        sort_order: form.sort_order,
      })
    }
    modalOpen.value = false
  } catch (e) {
    modalError.value = (e as Error).message
  } finally {
    isSubmitting.value = false
  }
}

const handleDelete = (cat: Category) => {
  deletingCategory.value = cat
}

const confirmDelete = async () => {
  if (!deletingCategory.value) return
  try {
    await categoriesStore.removeCategory(deletingCategory.value.id)
  } catch (e) {
    toastMessage.value = (e as Error).message
  } finally {
    deletingCategory.value = null
  }
}
</script>
