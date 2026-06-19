<template>
  <div class="space-y-2">
    <!-- 面包屑导航（当不在根层时显示） -->
    <div v-if="breadcrumb.length > 0" class="flex items-center gap-1 flex-wrap">
      <button
        @click="drillTo(null)"
        class="text-[11px] text-text-muted hover:text-primary transition-colors"
      >全部</button>
      <template v-for="(crumb, i) in breadcrumb" :key="crumb.id">
        <span class="text-[11px] text-border">/</span>
        <button
          @click="drillTo(i === breadcrumb.length - 1 ? (crumb.parentId ?? null) : crumb.id)"
          class="text-[11px] transition-colors"
          :class="i === breadcrumb.length - 1 ? 'text-primary font-medium' : 'text-text-muted hover:text-primary'"
        >{{ crumb.name }}</button>
      </template>
    </div>

    <!-- 当前层级的分类格子 -->
    <div :class="gridClass">
      <!-- 「全部」按钮（仅根层 + showAll 时显示） -->
      <button
        v-if="showAll && currentParentId === null"
        @click="emit('clear')"
        :class="[
          itemClass,
          modelValue === undefined
            ? 'border-primary bg-primary/10'
            : 'border-border bg-surface hover:border-primary/50',
        ]"
      >
        <div :class="iconClass">🔍</div>
        <div :class="labelClass"><span class="truncate">全部</span></div>
      </button>

      <!-- 「选当前层父节点本身」选项（不在根层时显示） -->
      <button
        v-if="currentParent"
        @click="emit('select', currentParent!.id)"
        :class="[
          itemClass,
          modelValue === currentParent!.id
            ? 'border-primary bg-primary/10'
            : 'border-border bg-surface hover:border-primary/50',
        ]"
      >
        <div :class="iconClass">{{ currentParent!.icon || '📦' }}</div>
        <div :class="labelClass">
          <span class="truncate">不分类</span>
        </div>
      </button>

      <!-- 当前层级的分类列表 -->
      <button
        v-for="cat in currentLevelItems"
        :key="cat.id"
        @click="handleClick(cat)"
        :class="[
          itemClass,
          isSelected(cat.id)
            ? 'border-primary bg-primary/10'
            : 'border-border bg-surface hover:border-primary/50',
        ]"
      >
        <div :class="iconClass">{{ cat.icon || '📦' }}</div>
        <div :class="labelClass">
          <span class="truncate max-w-[3.5rem]">{{ cat.name }}</span>
          <span v-if="childrenOf(cat.id).length > 0" class="text-[8px] text-text-muted flex-shrink-0">▶</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import type { Category } from '@/types/bill'

interface Props {
  modelValue: number | undefined  // 当前选中的 category_id
  size?: 'sm' | 'md'              // 按钮大小
  showAll?: boolean               // 是否在根层第一格显示「全部」按钮
}

const props = withDefaults(defineProps<Props>(), { size: 'md', showAll: false })
const emit = defineEmits<{
  'update:modelValue': [id: number | undefined]
  'select': [id: number]
  'clear': []
}>()

const categoriesStore = useCategoriesStore()
const childrenOf = (id: number) => categoriesStore.childrenOf(id)

// 当前下钻到的父节点 id（null = 根层）
const currentParentId = ref<number | null>(null)

// 当前层的父节点对象
const currentParent = computed(() =>
  currentParentId.value != null ? categoriesStore.byId.get(currentParentId.value) : null
)

// 当前层显示的分类列表
const currentLevelItems = computed(() =>
  currentParentId.value == null
    ? categoriesStore.rootCategories
    : childrenOf(currentParentId.value)
)

// 构建面包屑（从根到当前层的路径）
interface Crumb { id: number; name: string; parentId: number | null }
const breadcrumb = computed((): Crumb[] => {
  if (currentParentId.value == null) return []
  const path: Crumb[] = []
  let id: number | null = currentParentId.value
  while (id != null) {
    const cat = categoriesStore.byId.get(id)
    if (!cat) break
    path.unshift({ id: cat.id, name: cat.name, parentId: cat.parent_id ?? null })
    id = cat.parent_id ?? null
  }
  return path
})

// 下钻到指定父节点（null = 回根）
const drillTo = (id: number | null) => {
  currentParentId.value = id
}

// 点击分类：有子则下钻，无子则选中
const handleClick = (cat: Category) => {
  if (childrenOf(cat.id).length > 0) {
    currentParentId.value = cat.id
  } else {
    emit('select', cat.id)
    emit('update:modelValue', cat.id)
  }
}

// 判断是否选中（自身或其后代被选中时高亮）
const isSelected = (id: number): boolean => {
  if (props.modelValue == null) return false
  // 检查 modelValue 是否等于 id 或是其后代
  let cur = categoriesStore.byId.get(props.modelValue)
  while (cur) {
    if (cur.id === id) return true
    cur = cur.parent_id != null ? categoriesStore.byId.get(cur.parent_id) : undefined
  }
  return false
}

// 初始化：根据 modelValue 还原到正确层级
const initDrillDown = () => {
  if (props.modelValue == null) {
    currentParentId.value = null
    return
  }
  const cat = categoriesStore.byId.get(props.modelValue)
  if (!cat) { currentParentId.value = null; return }
  // 定位到该分类的父层
  currentParentId.value = cat.parent_id ?? null
}

watch(() => props.modelValue, initDrillDown, { immediate: true })
watch(() => categoriesStore.isLoaded, (loaded) => { if (loaded) initDrillDown() })

// 样式计算
const gridClass = computed(() =>
  props.size === 'sm'
    ? 'grid grid-cols-5 md:grid-cols-6 lg:grid-cols-8 gap-1.5'
    : 'flex flex-wrap gap-1.5'
)

const itemClass = computed(() =>
  props.size === 'sm'
    ? 'p-1.5 rounded-lg border-2 transition-all duration-200 flex flex-col items-center justify-center'
    : 'px-4 py-2 rounded-lg border-2 transition-all duration-200 flex flex-col items-center justify-center'
)

const iconClass = computed(() =>
  props.size === 'sm' ? 'text-sm' : 'text-base mb-0.5'
)

const labelClass = computed(() =>
  props.size === 'sm'
    ? 'text-[10px] text-text-secondary leading-tight mt-0.5 text-center flex items-center gap-0.5 w-full justify-center'
    : 'text-[11px] text-text-secondary text-center flex items-center justify-center gap-0.5 mt-0.5'
)
</script>
