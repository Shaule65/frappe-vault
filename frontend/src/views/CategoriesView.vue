<template>
  <div class="flex-1 overflow-auto p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Categories</h1>
        <p class="text-gray-500 mt-1">Organize your secrets</p>
      </div>
      <Button variant="solid" theme="green" @click="showNewDialog = true">
        <template #prefix><FeatherIcon name="plus" class="w-4 h-4" /></template>
        Add Category
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="categories.loading && !categories.data" class="text-center py-12">
      <LoadingText />
    </div>

    <!-- Categories grid -->
    <div v-else-if="categoryList.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="cat in categoryList"
        :key="cat.name"
        class="vault-card p-4 cursor-pointer hover:border-vault-200"
        @click="$router.push(`/secrets?category=${cat.name}`)"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: cat.color ? cat.color + '20' : '#f3f4f6' }"
          >
            <FeatherIcon
              :name="cat.icon || 'folder'"
              class="w-5 h-5"
              :style="{ color: cat.color || '#6b7280' }"
            />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-gray-900 truncate">{{ cat.category_name }}</h3>
            <p class="text-sm text-gray-500">{{ getCategorySecretCount(cat.name) }} secrets</p>
          </div>
          <FeatherIcon name="chevron-right" class="w-5 h-5 text-gray-400" />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else
      icon="folder"
      title="No categories yet"
      description="Create categories to organize your secrets"
    >
      <template #actions>
        <Button variant="solid" theme="green" @click="showNewDialog = true">
          Create Category
        </Button>
      </template>
    </EmptyState>

    <!-- New Category Dialog -->
    <Dialog
      v-model="showNewDialog"
      :options="{ title: 'Add Category' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            v-model="newCategory.category_name"
            label="Name"
            placeholder="e.g., Work"
            :required="true"
          />
          <FormControl
            v-model="newCategory.icon"
            label="Icon"
            placeholder="folder"
          />
          <div>
            <label class="text-sm font-medium text-gray-700 mb-2 block">Color</label>
            <div class="flex gap-2">
              <button
                v-for="color in colorOptions"
                :key="color"
                type="button"
                class="w-8 h-8 rounded-full border-2 transition-transform hover:scale-110"
                :class="newCategory.color === color ? 'border-gray-900 scale-110' : 'border-transparent'"
                :style="{ backgroundColor: color }"
                @click="newCategory.color = color"
              />
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showNewDialog = false">Cancel</Button>
        <Button variant="solid" theme="green" @click="createCategory" :loading="creating">
          Create
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Button, Dialog, FeatherIcon, FormControl, LoadingText } from 'frappe-ui'
import { call } from 'frappe-ui'
import { useCategories, useStats } from '@/data/vault'
import EmptyState from '@/components/EmptyState.vue'

const categories = useCategories()
const stats = useStats()

const showNewDialog = ref(false)
const creating = ref(false)

const newCategory = reactive({
  category_name: '',
  icon: 'folder',
  color: '#22c55e',
})

const colorOptions = [
  '#22c55e', // green
  '#3b82f6', // blue
  '#8b5cf6', // purple
  '#f59e0b', // amber
  '#ef4444', // red
  '#ec4899', // pink
  '#14b8a6', // teal
  '#6b7280', // gray
]

const categoryList = computed(() => categories.data || [])

function getCategorySecretCount(categoryName) {
  // This would need a proper endpoint - showing placeholder
  return '—'
}

async function createCategory() {
  creating.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Vault Category',
        ...newCategory,
      },
    })
    showNewDialog.value = false
    categories.reload()
    // Reset form
    newCategory.category_name = ''
    newCategory.icon = 'folder'
    newCategory.color = '#22c55e'
  } catch (e) {
    console.error('Failed to create category:', e)
  }
  creating.value = false
}
</script>
