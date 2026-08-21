<template>
  <Dialog v-model="show" :options="{ title: 'Add Secret', size: 'lg' }">
    <template #body-content>
      <div class="space-y-4">
        <FormControl label="Title" v-model="form.title" :required="true" placeholder="e.g. Gmail, AWS Console, Passport Scan" />

        <FormControl label="Secret Type" type="select" v-model="form.secret_type" :options="SECRET_TYPES" />

        <FormControl label="Folder" type="select" v-model="form.folder" :options="folderOptions" />

        <!-- Guided Database flow: server -> admin -> test -> stored credential.
             Every other secret type keeps the plain generic field grid below. -->
        <template v-if="form.secret_type === 'Database'">
          <div class="space-y-4">
            <!-- 1. Where the database lives -->
            <div class="space-y-3">
              <p class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider">Server</p>
              <div class="grid grid-cols-2 gap-4">
                <FormControl label="Database Type" type="select" v-model="form.database_type" :options="DATABASE_TYPES" class="col-span-2" />
                <FormControl label="Host" v-model="form.db_host" placeholder="localhost or IP" />
                <FormControl label="Port" v-model="form.db_port" placeholder="Engine default" />
                <FormControl label="Database Name" v-model="form.db_name" />
                <FormControl v-if="form.database_type === 'MongoDB'" label="Auth Source" v-model="form.db_auth_source" placeholder="admin" />
                <FormControl label="URL (optional)" v-model="form.url" class="col-span-2" />
                <div class="col-span-2">
                  <FormControl type="checkbox" label="Use TLS / SSL" v-model="form.db_use_ssl" />
                </div>
              </div>
            </div>

            <!-- 2. Should Vault reset this password on the server? -->
            <div class="pt-2 border-t border-outline-gray-1 space-y-2">
              <FormControl
                type="checkbox"
                label="Let Vault reset this password on the database"
                v-model="form.apply_rotation_to_target"
              />
              <p class="text-xs text-ink-gray-5 leading-relaxed">
                Rotates the password on a schedule and changes it on the live server too, so Vault and the
                database stay in sync, and the new value stays readable here. Leave this off to simply store
                the credential without touching the server.
              </p>
            </div>

            <!-- 3. Admin credential + connection test -->
            <template v-if="form.apply_rotation_to_target">
              <div class="space-y-3">
                <p class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider">Admin Credential</p>
                <p class="text-xs text-ink-gray-5 leading-relaxed">
                  The privileged account Vault authenticates as to reset the password. Stored encrypted, and
                  never rotated by Vault.
                </p>
                <div class="grid grid-cols-2 gap-4">
                  <FormControl label="Account to Rotate" v-model="form.username" placeholder="the DB user Vault will reset" class="col-span-2" />
                  <FormControl label="Admin Username" v-model="form.rotation_admin_username" placeholder="postgres / root" />
                  <FormControl label="Admin Password" v-model="form.rotation_admin_password" :type="showSecrets ? 'text' : 'password'" />
                </div>

                <div class="flex items-center gap-3">
                  <Button
                    variant="subtle"
                    icon-left="lucide-plug"
                    label="Test Connection"
                    :loading="testResource.loading"
                    @click="handleTestConnection"
                  />
                  <span v-if="testState === 'passed'" class="text-xs font-medium text-ink-green-3">
                    <FeatherIcon name="check-circle" class="w-3.5 h-3.5 inline -mt-0.5 mr-1" />Connection confirmed
                  </span>
                  <span v-else-if="testState === 'failed'" class="text-xs font-medium text-ink-red-3">
                    <FeatherIcon name="x-circle" class="w-3.5 h-3.5 inline -mt-0.5 mr-1" />Not connected
                  </span>
                </div>

                <p v-if="testMessage" class="text-xs leading-relaxed" :class="testState === 'passed' ? 'text-ink-gray-6' : 'text-ink-red-3'">
                  {{ testMessage }}
                </p>
              </div>

              <!-- 4. Rotation schedule -->
              <div class="grid grid-cols-2 gap-4">
                <FormControl label="Rotate Every" type="number" min="1" v-model="form.rotation_interval" />
                <FormControl label="Interval Unit" type="select" v-model="form.rotation_unit" :options="ROTATION_UNITS" />
              </div>
            </template>

            <!-- 5. The credential that gets stored and rotated -->
            <div class="pt-2 border-t border-outline-gray-1 space-y-3">
              <p class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider">Stored Credential</p>
              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-if="!form.apply_rotation_to_target"
                  label="Username"
                  v-model="form.username"
                  class="col-span-2"
                />
                <FormControl
                  label="Password"
                  v-model="form.db_password"
                  :type="showSecrets ? 'text' : 'password'"
                  :disabled="credentialLocked"
                  class="col-span-2"
                >
                  <template #suffix>
                    <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
                  </template>
                </FormControl>
              </div>
              <p v-if="credentialLocked" class="text-xs text-ink-gray-5 leading-relaxed">
                <FeatherIcon name="lock" class="w-3.5 h-3.5 inline -mt-0.5 mr-1" />
                Confirm the connection above first — that way the password you store is one Vault has proven
                it can actually reset.
              </p>
            </div>
          </div>
        </template>

        <div v-else class="grid grid-cols-2 gap-4">
          <template v-for="field in visibleFieldsFor(form.secret_type, form)" :key="field.name">
            <!-- Media Attachment Custom UI -->
            <div v-if="field.type === 'file'" class="col-span-2 space-y-2 pt-1">
              <label class="block text-sm font-medium text-ink-gray-7">Document / Media Attachments</label>

              <!-- List of Uploaded Files -->
              <div v-if="attachmentList.length > 0" class="space-y-2">
                <div
                  v-for="(fileUrl, idx) in attachmentList"
                  :key="fileUrl + idx"
                  class="p-2.5 rounded-xl border border-outline-gray-1 bg-surface-gray-2 flex items-center justify-between shadow-2xs"
                >
                  <div class="flex items-center gap-3 overflow-hidden min-w-0">
                    <img
                      v-if="isImageUrl(fileUrl)"
                      :src="fileUrl"
                      class="w-10 h-10 object-cover rounded-lg shrink-0 border border-outline-gray-1 bg-surface-base"
                    />
                    <div v-else class="w-10 h-10 rounded-lg bg-surface-gray-3 border border-outline-gray-1 flex items-center justify-center shrink-0">
                      <FeatherIcon name="paperclip" class="w-5 h-5 text-ink-gray-7" />
                    </div>
                    <div class="min-w-0">
                      <p class="text-xs font-semibold text-ink-gray-9 truncate">{{ getFileName(fileUrl) }}</p>
                      <a :href="fileUrl" target="_blank" class="text-[11px] font-mono text-ink-gray-5 hover:text-blue-600 dark:hover:text-blue-400 hover:underline truncate block">{{ fileUrl }}</a>
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="xs"
                    icon="x"
                    class="!p-1 h-auto text-ink-gray-5 hover:text-ink-red-3 hover:bg-surface-gray-3 focus:outline-none"
                    title="Remove File"
                    @click.stop.prevent="removeAttachment(idx)"
                  />
                </div>
              </div>

              <!-- Multi-File Upload Dropzone Trigger -->
              <div
                class="relative border-2 border-dashed border-outline-gray-2 rounded-xl p-4 text-center hover:border-ink-gray-6 transition-colors cursor-pointer bg-surface-gray-1"
                @click="triggerFileInput('attachment')"
              >
                <FormControl
                  type="file"
                  id="file_input_attachment"
                  class="hidden"
                  multiple
                  accept="*/*"
                  @change="handleFileUpload($event)"
                />
                <div class="flex flex-col items-center gap-1">
                  <FeatherIcon name="paperclip" class="w-6 h-6 text-ink-gray-5" />
                  <span class="text-xs font-semibold text-ink-gray-8">
                    {{ uploadingFiles ? 'Uploading files...' : (attachmentList.length > 0 ? '+ Add More Files' : 'Click or drag files here to upload') }}
                  </span>
                  <span class="text-[10px] text-ink-gray-5">Supports Images, PDFs, Zip, Documents (Select multiple files)</span>
                </div>
              </div>
            </div>

            <!-- Engine / option picker -->
            <FormControl
              v-else-if="field.type === 'select'"
              :label="field.label"
              type="select"
              v-model="form[field.name]"
              :options="field.options"
              :class="(field.colSpan === 2) ? 'col-span-2' : 'col-span-1'"
            />

            <!-- Toggle -->
            <div v-else-if="field.type === 'checkbox'" :class="[(field.colSpan === 2) ? 'col-span-2' : 'col-span-1', 'flex items-end pb-2']">
              <FormControl type="checkbox" :label="field.label" v-model="form[field.name]" />
            </div>

            <!-- Standard Form Control -->
            <FormControl
              v-else
              :label="field.label"
              v-model="form[field.name]"
              :type="field.type === 'password' && showSecrets ? 'text' : field.type"
              :class="(field.colSpan === 2) ? 'col-span-2' : 'col-span-1'"
              :placeholder="field.placeholder"
            >
              <template #suffix v-if="field.type === 'password'">
                <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
              </template>
            </FormControl>
          </template>
        </div>

        <!-- Automatic rotation. Database secrets configure theirs inside the guided
             flow above; the full model (vault-only rotation, custom archive
             passphrase) stays available for them in the edit panel. -->
        <div v-if="form.secret_type === 'Password'" class="pt-1 space-y-2">
          <FormControl type="checkbox" label="Enable Automatic Rotation" v-model="form.enable_rotation" />
          <p class="text-xs text-ink-gray-5 leading-relaxed">
            Generate a new password on a schedule. Everyone with access is notified and can read the new
            value here. Updates the stored value only &mdash; you must apply it to the target system yourself.
          </p>
          <div v-if="form.enable_rotation" class="grid grid-cols-2 gap-4 pt-1">
            <FormControl label="Rotate Every" type="number" min="1" v-model="form.rotation_interval" />
            <FormControl label="Interval Unit" type="select" v-model="form.rotation_unit" :options="ROTATION_UNITS" />
          </div>

          <FormControl
            v-if="form.enable_rotation"
            label="Custom Rotation Passphrase (optional)"
            v-model="form.zip_passphrase"
            :type="showSecrets ? 'text' : 'password'"
            placeholder="Leave blank to use the shared site passphrase"
          />
          <p v-if="form.enable_rotation" class="text-xs text-ink-gray-5 leading-relaxed">
            Stored encrypted, the same way as this secret's own password. Used automatically when this
            secret rotates, so its archive opens with your passphrase instead of the shared site one.
          </p>

        </div>

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
import { Dialog, FormControl, Button, FeatherIcon, toast } from 'frappe-ui'
import { SECRET_TYPES, ROTATION_UNITS, DATABASE_TYPES, DATABASE_DEFAULT_PORTS } from '../composables/constants'
import { visibleFieldsFor } from '../composables/secretFields'
import { useFolders, useCreateSecret, useTestDbConnectionParams } from '../composables/vault'
import { cleanUrl, parseAttachments, isImageUrl, getFileName } from '../utils/attachments'
import { validateTotpSecret } from '../utils/secretForm'

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
    if (f.can_write) {
      opts.push({ label: f.folder_name, value: f.name })
    }
  }
  return opts
})

const defaultForm = () => ({
  title: '', secret_type: 'Password', folder: props.initialFolder || '', url: '', username: '', email: '',
  password: '', totp_secret: '', api_key: '', api_secret: '', ssh_private_key: '', attachment: '', notes: '', card_holder: '', card_number: '',
  card_expiry: '', card_cvv: '', database_type: '', db_host: '', db_port: '', db_name: '',
  db_auth_source: '', db_use_ssl: 0, db_password: '',
  enable_rotation: 0, rotation_interval: 90, rotation_unit: 'Days', zip_passphrase: '',
  apply_rotation_to_target: 0, rotation_admin_username: '', rotation_admin_password: '',
})

const form = ref(defaultForm())
const attachmentList = ref([])
const showSecrets = ref(false)
const uploadingFiles = ref(false)

const testResource = useTestDbConnectionParams()
const testState = ref('untested')   // 'untested' | 'passed' | 'failed'
const testMessage = ref('')

// The stored password stays locked until Vault has proven it can reach the
// server and reset the account — otherwise you would be storing a credential
// for a rotation that was never going to work.
const credentialLocked = computed(
  () => form.value.secret_type === 'Database'
    && !!form.value.apply_rotation_to_target
    && testState.value !== 'passed'
)

// Any change to what the test proved invalidates the result.
watch(
  () => [
    form.value.database_type, form.value.db_host, form.value.db_port, form.value.db_name,
    form.value.db_auth_source, form.value.db_use_ssl, form.value.username,
    form.value.rotation_admin_username, form.value.rotation_admin_password,
  ],
  () => {
    testState.value = 'untested'
    testMessage.value = ''
  }
)

async function handleTestConnection() {
  testState.value = 'untested'
  testMessage.value = ''
  try {
    const result = await testResource.submit({
      database_type: form.value.database_type,
      db_host: form.value.db_host,
      db_port: form.value.db_port,
      db_name: form.value.db_name,
      db_auth_source: form.value.db_auth_source,
      db_use_ssl: form.value.db_use_ssl ? 1 : 0,
      username: form.value.username,
      admin_username: form.value.rotation_admin_username,
      admin_password: form.value.rotation_admin_password,
    })
    testState.value = 'passed'
    testMessage.value = result.message || ''
  } catch (err) {
    testState.value = 'failed'
    testMessage.value = err.messages?.[0] || err.message || 'Could not reach the database'
  }
}

watch(show, (v) => {
  if (v) {
    form.value = defaultForm()
    attachmentList.value = []
    showSecrets.value = false
    testState.value = 'untested'
    testMessage.value = ''
  }
})

// Choosing an engine fills in its default port and Mongo's auth source, but
// never overwrites something already typed.
watch(() => form.value.database_type, (engine) => {
  if (!engine) return
  if (!form.value.db_port) form.value.db_port = DATABASE_DEFAULT_PORTS[engine] || ''
  if (engine === 'MongoDB' && !form.value.db_auth_source) form.value.db_auth_source = 'admin'
})

function removeAttachment(index) {
  attachmentList.value.splice(index, 1)
  syncAttachmentForm()
}

function syncAttachmentForm() {
  if (attachmentList.value.length === 0) {
    form.value.attachment = ''
  } else if (attachmentList.value.length === 1) {
    form.value.attachment = attachmentList.value[0]
  } else {
    form.value.attachment = JSON.stringify(attachmentList.value)
  }
}

async function handleFileUpload(event) {
  const files = Array.from(event.target.files || [])
  if (!files.length) return

  uploadingFiles.value = true
  try {
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_private', 1)

      const response = await fetch('/api/method/frappe_vault.api.secrets.upload_file', {
        method: 'POST',
        headers: {
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: formData
      })
      const data = await response.json()
      if (response.ok && data.message && data.message.file_url) {
        attachmentList.value.push(data.message.file_url)
      } else {
        toast.error(data.message || 'File upload failed')
      }
    }
    syncAttachmentForm()
  } catch (err) {
    toast.error(err.message || 'File upload failed')
  } finally {
    uploadingFiles.value = false
  }
}

function triggerFileInput(fieldname) {
  const el = document.getElementById('file_input_' + fieldname)
  if (el) {
    if (el.tagName === 'INPUT') el.click()
    else {
      const input = el.querySelector('input[type="file"]')
      if (input) input.click()
    }
  }
}

async function handleCreate() {
  if (credentialLocked.value) {
    toast.error('Confirm the database connection before saving this secret')
    return
  }

  if (['Password', 'API Key'].includes(form.value.secret_type) && form.value.totp_secret) {
    const validation = validateTotpSecret(form.value.totp_secret)
    if (!validation.ok) {
      toast.error(validation.message)
      return
    }
  }

  const payload = { ...form.value }

  // For a Database secret, letting Vault reset the password on the server is
  // what turns rotation on — the two are one decision in this dialog.
  if (payload.secret_type === 'Database') {
    if (payload.apply_rotation_to_target) {
      payload.apply_rotation_to_target = 1
      payload.enable_rotation = 1
      payload.rotation_interval = Number(payload.rotation_interval) || 90
      payload.rotation_unit = payload.rotation_unit || 'Days'
    } else {
      payload.apply_rotation_to_target = 0
      payload.enable_rotation = 0
      delete payload.rotation_interval
      delete payload.rotation_unit
      delete payload.rotation_admin_username
      delete payload.rotation_admin_password
    }
    delete payload.zip_passphrase
  } else if (payload.secret_type === 'Password' && payload.enable_rotation) {
    payload.enable_rotation = 1
    payload.rotation_interval = Number(payload.rotation_interval) || 90
    if (!payload.zip_passphrase) delete payload.zip_passphrase
    payload.apply_rotation_to_target = 0
  } else {
    payload.enable_rotation = 0
    payload.apply_rotation_to_target = 0
    delete payload.rotation_interval
    delete payload.rotation_unit
    delete payload.zip_passphrase
    delete payload.rotation_admin_username
    delete payload.rotation_admin_password
  }

  try {
    const result = await createResource.submit(payload)
    window.dispatchEvent(new CustomEvent('vault-secret-updated', { detail: { name: result?.name } }))
    emit('created', result)
  } catch (err) {
    if (err.messages?.length) {
      err.messages.forEach(msg => toast.error(msg))
    } else {
      toast.error(err.message || 'Failed to create secret')
    }
  }
}
</script>
