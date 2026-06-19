<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between mb-8 gap-3">
        <div class="min-w-0">
          <h1 class="text-3xl font-bold text-text mb-2">分类管理</h1>
          <p class="text-text-muted">维护账单分类，全部用户共用同一份分类</p>
        </div>
        <button @click="openCreate(null)" class="btn btn-primary whitespace-nowrap flex-shrink-0">新建分类</button>
      </div>

      <!-- 列表 -->
      <div v-if="isLoading && categories.length === 0" class="space-y-3">
        <div v-for="i in 3" :key="i" class="card h-20 animate-pulse bg-surface/50" />
      </div>
      <div v-else-if="rootCategories.length === 0" class="text-center py-12 text-text-muted">
        暂无分类，点击右上角新建一个吧
      </div>
      <div v-else class="space-y-3">
        <!-- 根分类卡片 -->
        <div v-for="root in rootCategories" :key="root.id" class="rounded-xl border border-border overflow-hidden">
          <!-- 根分类行 -->
          <div class="card p-4 flex items-center gap-4 rounded-none border-0">
            <button
              v-if="childrenOf(root.id).length > 0"
              @click="toggleExpand(root.id)"
              class="flex-shrink-0 w-5 h-5 flex items-center justify-center text-text-muted hover:text-text transition-colors"
            >
              <svg :class="['w-4 h-4 transition-transform duration-200', expanded.has(root.id) ? 'rotate-90' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <div v-else class="flex-shrink-0 w-5" />
            <div
              class="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-xl"
              :style="{ backgroundColor: root.color + '22' }"
            >
              {{ root.icon || '📦' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-sm font-semibold text-text truncate">{{ root.name }}</h3>
                <span class="text-[10px] px-1.5 py-0.5 rounded text-text-muted bg-surface border border-border">#{{ root.sort_order }}</span>
                <span v-if="childrenOf(root.id).length > 0" class="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                  {{ childrenOf(root.id).length }} 个子分类
                </span>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <span class="inline-block w-3 h-3 rounded-full border border-border" :style="{ backgroundColor: root.color }" />
                <span class="text-xs text-text-muted">{{ root.color }}</span>
              </div>
            </div>
            <div class="flex gap-1 flex-shrink-0">
              <button @click="openCreate(root.id)" class="p-2 hover:bg-primary/10 rounded-lg transition-colors duration-200" title="添加子分类">
                <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button @click="openEdit(root)" class="p-2 hover:bg-surface rounded-lg transition-colors duration-200" title="编辑">
                <svg class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button @click="handleDelete(root)" class="p-2 hover:bg-error/10 rounded-lg transition-colors duration-200" title="删除">
                <svg class="w-4 h-4 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 子分类（递归展开，支持无限层级） -->
          <Transition name="expand">
            <div v-if="expanded.has(root.id) && childrenOf(root.id).length > 0" class="border-t border-border bg-surface/20">
              <CategoryNodeRow
                v-for="(child, idx) in childrenOf(root.id)"
                :key="child.id"
                :cat="child"
                :children="childrenOf(child.id)"
                :depth="1"
                :is-last="idx === childrenOf(root.id).length - 1"
                :expanded="expanded.has(child.id)"
                :get-children="childrenOf"
                :expanded-set="expanded"
                @toggle="toggleExpand"
                @create-child="openCreate"
                @edit="openEdit"
                @delete="handleDelete"
              />
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 编辑/新建模态 -->
    <Teleport to="body">
      <Transition name="overlay">
        <div v-if="modalOpen" class="fixed inset-0 z-50 bg-black/50" @click="handleMobileClose" />
      </Transition>
      <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-end sm:items-center p-0 sm:p-4 pointer-events-none">
        <Transition :name="isMobile ? 'slide' : 'modal'" appear>
          <div v-show="sheetVisible" class="bg-surface w-full pointer-events-auto
            rounded-t-2xl max-h-[90dvh] flex flex-col overflow-hidden
            sm:rounded-2xl sm:max-w-md sm:max-h-none sm:flex-none sm:overflow-visible sm:mx-auto shadow-xl"
            @touchstart.passive="onDragStart"
            @touchend.passive="onDragEnd"
          >
            <div class="sm:hidden flex-shrink-0 flex justify-center pt-3 pb-2 cursor-pointer" @click="handleMobileClose">
              <div class="w-10 h-1 bg-border rounded-full"></div>
            </div>
            <div class="border-b border-border px-6 py-4 flex-shrink-0 flex items-center justify-between">
              <h2 class="text-xl font-bold text-text">{{ editingId ? '编辑分类' : (form.parent_id ? '新建子分类' : '新建分类') }}</h2>
              <button @click="closeModal" class="hidden sm:block p-2 hover:bg-border rounded-lg transition-colors duration-200">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div ref="scrollRef" class="p-6 space-y-4 overflow-y-auto flex-1 sm:overflow-visible sm:flex-none">
              <!-- 父分类选择 -->
              <div>
                <label class="block text-sm font-medium text-text mb-2">父分类（可选）</label>
                <select v-model="form.parent_id" class="input">
                  <option :value="null">— 根分类（无父分类）</option>
                  <option
                    v-for="cat in availableParents"
                    :key="cat.id"
                    :value="cat.id"
                  >
                    {{ cat.parent_id == null ? '' : '　' }}{{ cat.icon }} {{ cat.name }}
                  </option>
                </select>
                <p v-if="form.parent_id != null" class="text-xs text-text-muted mt-1">
                  父分类：{{ byId.get(form.parent_id)?.icon }} {{ byId.get(form.parent_id)?.name }}
                </p>
              </div>
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
                <div class="input-number-wrap">
                  <input v-model.number="form.sort_order" type="number" min="0" class="input" placeholder="数值越小越靠前" />
                  <div class="input-number-controls">
                    <button type="button" tabindex="-1" @click="form.sort_order = (form.sort_order || 0) + 1">
                      <svg viewBox="0 0 10 6" width="10" height="6" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 5L5 1L9 5"/></svg>
                    </button>
                    <button type="button" tabindex="-1" @click="form.sort_order = Math.max(0, (form.sort_order || 0) - 1)">
                      <svg viewBox="0 0 10 6" width="10" height="6" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 1L5 5L9 1"/></svg>
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="modalError" class="p-3 bg-error/10 border border-error/30 rounded-lg">
                <p class="text-sm text-error">{{ modalError }}</p>
              </div>
            </div>

            <div class="border-t border-border px-6 py-4 flex flex-col gap-2 flex-shrink-0 sm:flex-row sm:justify-end">
              <button @click="handleSubmit" :disabled="isSubmitting" class="btn btn-primary py-3 sm:py-2 text-base sm:text-sm">
                {{ isSubmitting ? '保存中...' : '保存' }}
              </button>
              <button @click="closeModal" :disabled="isSubmitting" class="btn btn-secondary py-3 sm:py-2 text-base sm:text-sm">
                取消
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Teleport>

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
import { useDevice } from '@/utils/useDevice'
import { useCategoriesStore } from '@/stores/categories'
import type { Category } from '@/types/bill'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import Toast from '@/components/common/Toast.vue'
import CategoryNodeRow from '@/components/categories/CategoryNodeRow.vue'

const categoriesStore = useCategoriesStore()
const { isMobile } = useDevice()

const scrollRef = ref<HTMLElement | null>(null)

const categories = computed(() => categoriesStore.sortedCategories)
const rootCategories = computed(() => categoriesStore.rootCategories)
const byId = computed(() => categoriesStore.byId)
const childrenOf = (id: number) => categoriesStore.childrenOf(id)
const isLoading = computed(() => categoriesStore.isLoading)

const toastMessage = ref<string | null>(null)
const deletingCategory = ref<Category | null>(null)

// 展开状态（存根分类 id）
const expanded = ref<Set<number>>(new Set())
const toggleExpand = (id: number) => {
  const s = new Set(expanded.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expanded.value = s
}

const modalOpen = ref(false)
const sheetVisible = ref(true)
const editingId = ref<number | null>(null)
const isSubmitting = ref(false)
const modalError = ref('')

const form = reactive({
  name: '',
  icon: '',
  color: '#6B7280',
  sort_order: 0 as number | undefined,
  parent_id: null as number | null,
})

// 可作为父分类的选项（编辑时排除自身及其后代以防循环引用）
const availableParents = computed(() => {
  if (!editingId.value) return categories.value
  // 收集当前节点的所有后代 id
  const getDescendants = (id: number): Set<number> => {
    const result = new Set<number>([id])
    categoriesStore.childrenOf(id).forEach((c) => {
      getDescendants(c.id).forEach((d) => result.add(d))
    })
    return result
  }
  const excluded = getDescendants(editingId.value)
  return categories.value.filter((c) => !excluded.has(c.id))
})

onMounted(() => {
  categoriesStore.getOrFetch().then(() => {
    // 默认展开所有有子分类的根分类
    rootCategories.value.forEach((r) => {
      if (childrenOf(r.id).length > 0) {
        expanded.value = new Set([...expanded.value, r.id])
      }
    })
  })
})

const openCreate = (parentId: number | null) => {
  editingId.value = null
  form.name = ''
  form.icon = ''
  form.color = '#6B7280'
  form.sort_order = undefined
  form.parent_id = parentId
  modalError.value = ''
  sheetVisible.value = true
  modalOpen.value = true
}

const openEdit = (cat: Category) => {
  editingId.value = cat.id
  form.name = cat.name
  form.icon = cat.icon
  form.color = cat.color
  form.sort_order = cat.sort_order
  form.parent_id = cat.parent_id ?? null
  modalError.value = ''
  sheetVisible.value = true
  modalOpen.value = true
}

function handleMobileClose() {
  if (isSubmitting.value) return
  if (isMobile.value) {
    sheetVisible.value = false
    setTimeout(() => { modalOpen.value = false }, 280)
  } else {
    modalOpen.value = false
  }
}

const closeModal = () => handleMobileClose()

let dragStartY = 0
function onDragStart(e: TouchEvent) { dragStartY = e.touches[0].clientY }
function onDragEnd(e: TouchEvent) {
  const dy = e.changedTouches[0].clientY - dragStartY
  const atTop = !scrollRef.value || scrollRef.value.scrollTop === 0
  if (dy > 60 && atTop) handleMobileClose()
}

const HEX_RE = /^#[0-9A-Fa-f]{6}$/

const handleSubmit = async () => {
  modalError.value = ''
  if (!form.name.trim()) { modalError.value = '名称不能为空'; return }
  if (!HEX_RE.test(form.color)) { modalError.value = '颜色必须是 #RRGGBB 格式'; return }
  isSubmitting.value = true
  try {
    if (editingId.value) {
      await categoriesStore.updateCategory(editingId.value, {
        name: form.name.trim(),
        icon: form.icon,
        color: form.color,
        sort_order: form.sort_order,
        parent_id: form.parent_id,
      })
    } else {
      const created = await categoriesStore.createCategory({
        name: form.name.trim(),
        icon: form.icon,
        color: form.color,
        sort_order: form.sort_order,
        parent_id: form.parent_id,
      })
      // 创建子分类后自动展开父节点
      if (form.parent_id != null) {
        // 找到根祖先以确保展开
        let cur: Category | undefined = byId.value.get(form.parent_id)
        while (cur) {
          expanded.value = new Set([...expanded.value, cur.id])
          cur = cur.parent_id != null ? byId.value.get(cur.parent_id) : undefined
        }
      }
      void created
    }
    modalOpen.value = false
  } catch (e) {
    modalError.value = (e as Error).message
  } finally {
    isSubmitting.value = false
  }
}

const handleDelete = (cat: Category) => { deletingCategory.value = cat }

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

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: max-height 0.25s ease, opacity 0.2s ease;
  max-height: 800px;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
