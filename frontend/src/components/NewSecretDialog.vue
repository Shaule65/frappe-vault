<template>
  <Dialog v-model="show" :options="{ title: 'Add Secret', size: 'lg' }">
    <template #body-content>
      <div class="space-y-4">
        <FormControl label="Title" v-model="form.title" :required="true" placeholder="e.g. Gmail, AWS Console" />

        <FormControl label="Secret Type" type="select" v-model="form.secret_type"
          :options="['Password', 'API Key', 'Note', 'SSH Key', 'Certificate', 'Credit Card', 'Database', 'Other']" />

        <div class="grid grid-cols-2 gap-4">
          <FormControl label="Folder" type="select" v-model="form.folder" :options="folderOptions" />
          <FormControl label="URL" v-model="form.url" placeholder="https://..." />
        </div>

        <!-- Password fields -->
        <template v-if="form.secret_type === 'Password'">
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Username" v-model="form.username" />
            <FormControl label="Email" v-model="form.email" type="email" />
          </div>
          <FormControl label="Password" v-model="form.password" type="password" />
        </template>

        <!-- API Key fields -->
        <template v-if="form.secret_type === 'API Key'">
          <FormControl label="API Key" v-model="form.api_key" />
          <FormControl label="API Secret" v-model="form.api_secret" type="password" />
        </template>

        <!-- Credit Card fields -->
        <template v-if="form.secret_type === 'Credit Card'">
          <FormControl label="Card Holder" v-model="form.card_holder" />
          <div class="grid grid-cols-3 gap-4">
            <FormControl label="Card Number" v-model="form.card_number" type="password" class="col-span-2" />
            <FormControl label="CVV" v-model="form.card_cvv" type="password" />
          </div>
          <FormControl label="Expiry (MM/YY)" v-model="form.card_expiry" placeholder="12/28" />
        </template>

        <!-- Database fields -->
        <template v-if="form.secret_type === 'Database'">
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Host" v-model="form.db_host" />
            <FormControl label="Port" v-model="form.db_port" type="number" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Database Name" v-model="form.db_name" />
            <FormControl label="Username" v-model="form.username" />
          </div>
          <FormControl label="Password" v-model="form.db_password" type="password" />
        </template>

        <FormControl label="Notes" type="textarea" v-model="form.notes" :rows="3" />
      </div>
    </template>

    <template #actions>
      <Button variant="solid" @click="handleCreate" :loading="createResource.loading">Create</Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button, Dialog, FormControl } from 'frappe-ui'
import { useCreateSecret, useFolders } from '../composables/vault'

const props = defineProps({
  modelValue: Boolean,
  initialFolder: String,
})
const emit = defineEmits(['update:modelValue', 'created'])

const show = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const createResource = useCreateSecret()
const foldersResource = useFolders()

const folderOptions = computed(() => {
  const opts = [{ label: 'None', value: '' }]
  for (const f of foldersResource.data || []) {
    opts.push({ label: f.folder_name, value: f.name })
  }
  return opts
})

const defaultForm = () => ({
  title: '', secret_type: 'Password', folder: props.initialFolder || '', url: '', username: '', email: '',
  password: '', api_key: '', api_secret: '', notes: '', card_holder: '', card_number: '',
  card_expiry: '', card_cvv: '', db_host: '', db_port: '', db_name: '', db_password: '',
})

const form = ref(defaultForm())

watch(show, (v) => { if (v) form.value = defaultForm() })

async function handleCreate() {
  const result = await createResource.submit(form.value)
  emit('created', result)
}
</script>
