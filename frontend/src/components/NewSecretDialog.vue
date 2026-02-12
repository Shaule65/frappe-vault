<template>
  <Dialog
    :modelValue="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    :options="{ title: 'Add New Secret', size: 'lg' }"
  >
    <template #body-content>
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <FormControl
          v-model="form.title"
          label="Title"
          placeholder="e.g., GitHub Account"
          :required="true"
        />

        <FormControl
          v-model="form.secret_type"
          label="Secret Type"
          type="select"
          :options="secretTypeOptions"
        />

        <FormControl
          v-model="form.category"
          label="Category"
          type="select"
          :options="categoryOptions"
        />

        <FormControl
          v-model="form.url"
          label="URL"
          placeholder="https://example.com"
        />

        <FormControl
          v-model="form.username"
          label="Username"
          placeholder="your@email.com"
        />

        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700">Password</label>
          <div class="flex gap-2">
            <div class="flex-1 relative">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-vault-500 focus:border-vault-500"
                placeholder="Enter password"
              />
              <button
                type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                @click="showPassword = !showPassword"
              >
                <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
              </button>
            </div>
            <Button type="button" variant="outline" @click="generatePassword">
              <FeatherIcon name="refresh-cw" class="w-4 h-4" />
            </Button>
          </div>
          <PasswordStrengthBar v-if="form.password" :password="form.password" />
        </div>

        <FormControl
          v-model="form.notes"
          label="Notes"
          type="textarea"
          :rows="3"
          placeholder="Additional notes..."
        />

        <div class="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_favorite"
            v-model="form.is_favorite"
            class="rounded border-gray-300 text-vault-600 focus:ring-vault-500"
          />
          <label for="is_favorite" class="text-sm text-gray-700">Add to favorites</label>
        </div>
      </form>
    </template>

    <template #actions>
      <Button variant="outline" @click="$emit('update:modelValue', false)">
        Cancel
      </Button>
      <Button
        variant="solid"
        theme="green"
        @click="handleSubmit"
        :loading="createSecret.loading"
      >
        Create Secret
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Button, Dialog, FormControl, FeatherIcon } from 'frappe-ui'
import { useCreateSecret, useCategories, usePasswordGenerator } from '@/data/vault'
import PasswordStrengthBar from './PasswordStrengthBar.vue'

const props = defineProps({
  modelValue: Boolean,
})

const emit = defineEmits(['update:modelValue', 'created'])

const createSecret = useCreateSecret()
const categories = useCategories()
const passwordGenerator = usePasswordGenerator()

const showPassword = ref(false)

const form = reactive({
  title: '',
  secret_type: 'Password',
  category: '',
  url: '',
  username: '',
  password: '',
  notes: '',
  is_favorite: false,
})

const secretTypeOptions = [
  { label: 'Password', value: 'Password' },
  { label: 'API Key', value: 'API Key' },
  { label: 'Note', value: 'Note' },
  { label: 'Card', value: 'Card' },
  { label: 'SSH Key', value: 'SSH Key' },
]

const categoryOptions = computed(() => {
  const opts = [{ label: 'None', value: '' }]
  for (const cat of categories.data || []) {
    opts.push({
      label: cat.category_name,
      value: cat.name,
    })
  }
  return opts
})

async function generatePassword() {
  const result = await passwordGenerator.submit({
    length: 20,
    use_uppercase: true,
    use_lowercase: true,
    use_digits: true,
    use_special: true,
  })
  if (result?.password) {
    form.password = result.password
    showPassword.value = true
  }
}

async function handleSubmit() {
  const result = await createSecret.submit({
    title: form.title,
    secret_type: form.secret_type,
    category: form.category || null,
    url: form.url || null,
    username: form.username || null,
    password: form.password || null,
    notes: form.notes || null,
    is_favorite: form.is_favorite,
  })

  if (result?.name) {
    // Reset form
    Object.assign(form, {
      title: '',
      secret_type: 'Password',
      category: '',
      url: '',
      username: '',
      password: '',
      notes: '',
      is_favorite: false,
    })
    emit('created', result)
  }
}
</script>
