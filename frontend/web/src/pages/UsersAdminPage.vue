<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold text-text mb-2">用户管理</h1>
          <p class="text-text-muted">管理系统用户账号</p>
        </div>
        <button @click="openCreate" class="btn btn-primary">新增用户</button>
      </div>

      <!-- 加载骨架 -->
      <div v-if="isLoading && users.length === 0" class="space-y-3">
        <div v-for="i in 3" :key="i" class="card h-16 animate-pulse bg-surface/50" />
      </div>

      <!-- 用户表格 -->
      <div v-else class="card overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="border-b border-border bg-surface/60">
              <th class="text-left text-xs font-semibold text-text-muted px-4 py-3">用户名</th>
              <th class="text-left text-xs font-semibold text-text-muted px-4 py-3">角色</th>
              <th class="text-left text-xs font-semibold text-text-muted px-4 py-3 hidden sm:table-cell">状态</th>
              <th class="text-left text-xs font-semibold text-text-muted px-4 py-3 hidden sm:table-cell">创建时间</th>
              <th class="text-right text-xs font-semibold text-text-muted px-4 py-3">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              class="border-b border-border last:border-b-0 hover:bg-surface/40 transition-colors"
            >
              <td class="px-4 py-3">
                <span class="text-sm font-medium text-text">{{ user.username }}</span>
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                  :class="user.role === 'admin' ? 'bg-primary/10 text-primary' : 'bg-surface border border-border text-text-muted'"
                >
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span
                  v-if="user.must_change_password"
                  class="inline-flex items-center gap-1 text-xs text-warning"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                  需要改密
                </span>
                <span v-else class="text-xs text-text-muted">正常</span>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span class="text-xs text-text-muted">{{ formatDate(user.created_at) }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <!-- 改名：自己（admin）不可对自己改名 -->
                  <button
                    v-if="user.id !== authStore.userId"
                    @click="openRename(user)"
                    class="px-2.5 py-1.5 text-xs text-text-secondary hover:bg-surface rounded-lg transition-colors"
                    title="修改用户名"
                  >
                    改名
                  </button>
                  <!-- 重置密码 -->
                  <button
                    @click="confirmReset(user)"
                    class="px-2.5 py-1.5 text-xs text-error hover:bg-error/10 rounded-lg transition-colors"
                    title="重置密码"
                  >
                    重置密码
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增用户模态 -->
    <div v-if="createModalOpen" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div class="bg-surface rounded-2xl shadow-xl w-full max-w-md">
        <div class="border-b border-border px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold text-text">新增用户</h2>
          <button @click="closeCreateModal" class="p-2 hover:bg-border rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="px-6 py-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1.5">用户名</label>
            <input
              v-model="createForm.username"
              type="text"
              placeholder="请输入用户名"
              class="input"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1.5">初始密码</label>
            <input
              v-model="createForm.password"
              type="text"
              placeholder="请输入初始密码"
              class="input"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1.5">角色</label>
            <select v-model="createForm.role" class="input">
              <option value="user">普通用户</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <p v-if="createError" class="text-sm text-error">{{ createError }}</p>
        </div>
        <div class="border-t border-border px-6 py-4 flex justify-end gap-3">
          <button @click="closeCreateModal" class="btn btn-secondary">取消</button>
          <button
            @click="submitCreate"
            :disabled="isSaving || !createForm.username || !createForm.password"
            class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSaving ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 改名模态 -->
    <div v-if="renameModalOpen" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div class="bg-surface rounded-2xl shadow-xl w-full max-w-md">
        <div class="border-b border-border px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold text-text">修改用户名</h2>
          <button @click="closeRenameModal" class="p-2 hover:bg-border rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="px-6 py-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1.5">
              新用户名（当前：{{ renamingUser?.username }}）
            </label>
            <input
              v-model="renameForm.username"
              type="text"
              placeholder="请输入新用户名"
              class="input"
            />
          </div>
          <p v-if="renameError" class="text-sm text-error">{{ renameError }}</p>
        </div>
        <div class="border-t border-border px-6 py-4 flex justify-end gap-3">
          <button @click="closeRenameModal" class="btn btn-secondary">取消</button>
          <button
            @click="submitRename"
            :disabled="isSaving || !renameForm.username || renameForm.username === renamingUser?.username"
            class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSaving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 重置密码确认 -->
    <ConfirmDialog
      v-if="resetTargetUser"
      title="重置密码"
      :message="`确认重置「${resetTargetUser.username}」的密码？将生成一个随机临时密码，用户下次登录须修改密码。`"
      confirmLabel="确认重置"
      cancelLabel="取消"
      :danger="true"
      @confirm="doReset"
      @cancel="resetTargetUser = null"
    />

    <!-- 临时密码展示模态 -->
    <div v-if="tempPasswordResult" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div class="bg-surface rounded-2xl shadow-xl w-full max-w-md">
        <div class="border-b border-border px-6 py-4">
          <h2 class="text-xl font-bold text-text">密码已重置</h2>
        </div>
        <div class="px-6 py-5 space-y-4">
          <div class="rounded-xl bg-warning/10 border border-warning/30 p-4 flex items-start gap-3">
            <svg class="w-5 h-5 text-warning shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            <p class="text-sm text-warning">此临时密码仅显示一次，请立即记录并告知用户</p>
          </div>
          <div>
            <p class="text-sm text-text-muted mb-2">用户名：<span class="text-text font-medium">{{ tempPasswordResult.username }}</span></p>
            <p class="text-sm text-text-muted mb-2">临时密码：</p>
            <div class="flex items-center gap-2">
              <code class="flex-1 text-lg font-mono font-bold text-primary bg-primary/10 rounded-lg px-4 py-2 tracking-widest select-all">
                {{ tempPasswordResult.temp_password }}
              </code>
              <button
                @click="copyTempPassword"
                class="p-2.5 hover:bg-surface border border-border rounded-lg transition-colors"
                :title="copied ? '已复制' : '复制'"
              >
                <svg v-if="!copied" class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <svg v-else class="w-4 h-4 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="border-t border-border px-6 py-4 flex justify-end">
          <button @click="tempPasswordResult = null; copied = false" class="btn btn-primary">我已记录</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Toast
      v-if="toastMessage"
      :message="toastMessage.text"
      :type="toastMessage.type"
      @close="toastMessage = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi, type AdminUser, type ResetPasswordResult } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import Toast from '@/components/common/Toast.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const authStore = useAuthStore()

const users = ref<AdminUser[]>([])
const isLoading = ref(false)
const isSaving = ref(false)

const toastMessage = ref<{ text: string; type: 'success' | 'error' | 'info' } | null>(null)

function showToast(text: string, type: 'success' | 'error' | 'info' = 'success') {
  toastMessage.value = { text, type }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// --- 加载 ---
async function loadUsers() {
  isLoading.value = true
  try {
    users.value = await usersApi.list()
  } catch {
    showToast('加载用户列表失败', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(loadUsers)

// --- 新增用户 ---
const createModalOpen = ref(false)
const createForm = ref({ username: '', password: '', role: 'user' as 'admin' | 'user' })
const createError = ref('')

function openCreate() {
  createForm.value = { username: '', password: '', role: 'user' }
  createError.value = ''
  createModalOpen.value = true
}

function closeCreateModal() {
  createModalOpen.value = false
}

async function submitCreate() {
  createError.value = ''
  isSaving.value = true
  try {
    const newUser = await usersApi.create(createForm.value)
    users.value.push(newUser)
    closeCreateModal()
    showToast(`用户「${newUser.username}」创建成功`)
  } catch (e) {
    createError.value = (e as Error).message || '创建失败'
  } finally {
    isSaving.value = false
  }
}

// --- 改名 ---
const renameModalOpen = ref(false)
const renamingUser = ref<AdminUser | null>(null)
const renameForm = ref({ username: '' })
const renameError = ref('')

function openRename(user: AdminUser) {
  renamingUser.value = user
  renameForm.value = { username: user.username }
  renameError.value = ''
  renameModalOpen.value = true
}

function closeRenameModal() {
  renameModalOpen.value = false
  renamingUser.value = null
}

async function submitRename() {
  if (!renamingUser.value) return
  renameError.value = ''
  isSaving.value = true
  try {
    const updated = await usersApi.updateUsername(renamingUser.value.id, renameForm.value.username)
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
    closeRenameModal()
    showToast('用户名已更新')
  } catch (e) {
    renameError.value = (e as Error).message || '更新失败'
  } finally {
    isSaving.value = false
  }
}

// --- 重置密码 ---
const resetTargetUser = ref<AdminUser | null>(null)
const tempPasswordResult = ref<ResetPasswordResult | null>(null)
const copied = ref(false)

function confirmReset(user: AdminUser) {
  resetTargetUser.value = user
}

async function doReset() {
  if (!resetTargetUser.value) return
  const target = resetTargetUser.value
  resetTargetUser.value = null
  try {
    const result = await usersApi.resetPassword(target.id)
    // 刷新列表中该用户状态
    const idx = users.value.findIndex(u => u.id === target.id)
    if (idx !== -1) users.value[idx].must_change_password = true
    copied.value = false
    tempPasswordResult.value = result
  } catch (e) {
    showToast((e as Error).message || '重置失败', 'error')
  }
}

async function copyTempPassword() {
  if (!tempPasswordResult.value) return
  try {
    await navigator.clipboard.writeText(tempPasswordResult.value.temp_password)
    copied.value = true
  } catch {
    // 降级：选中文本
  }
}
</script>
