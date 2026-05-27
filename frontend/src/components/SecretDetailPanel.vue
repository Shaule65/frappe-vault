<template>
  <aside class="w-[500px] border-l border-gray-200 bg-white flex flex-col fixed right-0 top-0 h-full z-20 shadow-2xl transition-all duration-300">
    
    <!-- Premium Header -->
    <div class="flex items-center justify-between p-5 border-b border-gray-100 bg-gray-50/50 backdrop-blur shrink-0">
      <div class="flex items-center gap-3.5 min-w-0 flex-1">
        <!-- Circular Avatar/Icon based on type -->
        <div :class="`w-10 h-10 rounded-full border flex items-center justify-center shrink-0 shadow-sm transition-all ${typeMeta[secretData?.secret_type || 'Other']?.bg}`">
          <FeatherIcon :name="typeMeta[secretData?.secret_type || 'Other']?.icon" class="w-5 h-5" />
        </div>
        <div class="min-w-0 flex-1">
          <h2 class="font-bold text-lg text-gray-900 leading-tight truncate" :title="secretData?.title">
            {{ secretData?.title || 'Loading...' }}
          </h2>
          <div class="flex items-center gap-2 mt-1">
            <!-- Copyable ID/Name Badge -->
            <button
              v-if="secretData?.name"
              @click="copyField(secretData.name, 'name')"
              class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors group cursor-pointer"
            >
              <span>{{ secretData.name }}</span>
              <FeatherIcon :name="copiedField === 'name' ? 'check' : 'copy'" class="w-3 h-3 text-gray-400 group-hover:text-gray-600" :class="{'text-green-600': copiedField === 'name'}" />
            </button>
            <Badge v-if="secretData?.is_favorite" theme="yellow" size="sm" variant="subtle" class="gap-1">
              <FeatherIcon name="star" class="w-3 h-3 fill-yellow-500 text-yellow-500" />
              <span>Favorite</span>
            </Badge>
          </div>
        </div>
      </div>
      
      <!-- Actions Group -->
      <div class="flex items-center gap-2 shrink-0 ml-4">
        <!-- Edit Mode Toggle -->
        <Button
          variant="outline"
          size="sm"
          @click="toggleEditMode"
          :class="isEditing ? 'bg-gray-100 text-gray-900 font-semibold border-gray-300' : 'text-gray-700 hover:bg-gray-50'"
        >
          <template #prefix>
            <FeatherIcon :name="isEditing ? 'eye' : 'edit-2'" class="w-3.5 h-3.5" />
          </template>
          <span>{{ isEditing ? 'View' : 'Edit' }}</span>
        </Button>
        
        <!-- Delete Button -->
        <Button
          v-if="!isEditing"
          variant="ghost"
          size="sm"
          theme="red"
          @click="handleDelete"
          class="text-gray-400 hover:text-red-600 hover:bg-red-50"
        >
          <FeatherIcon name="trash-2" class="w-4 h-4" />
        </Button>
        
        <!-- Separator -->
        <div class="w-[1px] h-5 bg-gray-200 mx-1" />
        
        <!-- Close Button -->
        <Button
          variant="ghost"
          size="sm"
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <FeatherIcon name="x" class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Borderless Navigation Tabs (CRM Lead layout style) -->
    <div v-if="!isEditing" class="flex items-center gap-6 px-6 border-b border-gray-100 bg-white shrink-0">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        class="py-3.5 text-sm font-medium relative transition-all focus:outline-none"
        :class="activeTab === tab.name ? 'text-gray-900 font-bold' : 'text-gray-400 hover:text-gray-900'"
        @click="activeTab = tab.name"
      >
        <span>{{ tab.label }}</span>
        <span
          v-if="activeTab === tab.name"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900 rounded-full"
        />
      </button>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-y-auto p-6 bg-white min-h-0">
      
      <!-- EDIT MODE LAYOUT (CRM SidePanel Split Style) -->
      <div v-if="isEditing" class="space-y-6">
        
        <!-- Basic Info Box -->
        <div class="p-4 bg-gray-50/50 border border-gray-100 rounded-xl space-y-3.5 shadow-sm">
          <h3 class="text-[11px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100 pb-1.5 mb-2">Basic Info</h3>
          
          <!-- Title -->
          <div class="flex items-center justify-between min-h-[38px]">
            <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">
              Title <span class="text-red-500">*</span>
            </label>
            <div class="w-[65%]">
              <TextInput
                v-model="editForm.title"
                placeholder="Enter secret title"
                class="w-full text-sm"
              />
            </div>
          </div>

          <!-- Secret Type -->
          <div class="flex items-center justify-between min-h-[38px]">
            <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Secret Type</label>
            <div class="w-[65%]">
              <FormControl
                v-model="editForm.secret_type"
                type="select"
                :options="secretTypeOptions"
                class="w-full text-sm cursor-pointer"
              />
            </div>
          </div>

          <!-- Folder -->
          <div class="flex items-center justify-between min-h-[38px]">
            <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Folder</label>
            <div class="w-[65%]">
              <FormControl
                v-model="editForm.folder"
                type="select"
                :options="folderOptions"
                class="w-full text-sm cursor-pointer"
              />
            </div>
          </div>
        </div>

        <!-- Type-Specific Fields Box -->
        <div class="p-4 bg-gray-50/50 border border-gray-100 rounded-xl space-y-3.5 shadow-sm">
          <h3 class="text-[11px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100 pb-1.5 mb-2">Credentials & Secret Fields</h3>

          <!-- PASSWORD TYPE -->
          <div v-if="editForm.secret_type === 'Password'" class="space-y-3.5">
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Username</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Password</label>
              <div class="w-[65%] relative">
                <TextInput :type="showEditPassword ? 'text' : 'password'" v-model="editForm.password" placeholder="Password" class="w-full text-sm pr-10" />
                <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-600" @click="showEditPassword = !showEditPassword">
                  <FeatherIcon :name="showEditPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">URL</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.url" placeholder="https://example.com" class="w-full text-sm" />
              </div>
            </div>
          </div>

          <!-- API KEY TYPE -->
          <div v-else-if="editForm.secret_type === 'API Key'" class="space-y-3.5">
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">API Key</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.api_key" placeholder="API Key" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">API Secret</label>
              <div class="w-[65%] relative">
                <TextInput :type="showEditAPISecret ? 'text' : 'password'" v-model="editForm.api_secret" placeholder="API Secret" class="w-full text-sm pr-10" />
                <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-600" @click="showEditAPISecret = !showEditAPISecret">
                  <FeatherIcon :name="showEditAPISecret ? 'eye-off' : 'eye'" class="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">URL</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.url" placeholder="https://api.example.com" class="w-full text-sm" />
              </div>
            </div>
          </div>

          <!-- CREDIT CARD TYPE -->
          <div v-else-if="editForm.secret_type === 'Credit Card'" class="space-y-3.5">
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Card Holder</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.card_holder" placeholder="Card Holder Name" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Card Number</label>
              <div class="w-[65%] relative">
                <TextInput :type="showEditCardNumber ? 'text' : 'password'" v-model="editForm.card_number" placeholder="Card Number" class="w-full text-sm pr-10" />
                <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-600" @click="showEditCardNumber = !showEditCardNumber">
                  <FeatherIcon :name="showEditCardNumber ? 'eye-off' : 'eye'" class="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Card Expiry</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.card_expiry" placeholder="MM/YY" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">CVV</label>
              <div class="w-[65%] relative">
                <TextInput :type="showEditCardCVV ? 'text' : 'password'" v-model="editForm.card_cvv" placeholder="CVV" class="w-full text-sm pr-10" />
                <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-600" @click="showEditCardCVV = !showEditCardCVV">
                  <FeatherIcon :name="showEditCardCVV ? 'eye-off' : 'eye'" class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <!-- DATABASE TYPE -->
          <div v-else-if="editForm.secret_type === 'Database'" class="space-y-3.5">
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Host</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.db_host" placeholder="localhost" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Port</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.db_port" placeholder="3306" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">DB Name</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.db_name" placeholder="my_database" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Username</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
              </div>
            </div>
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Password</label>
              <div class="w-[65%] relative">
                <TextInput :type="showEditDBPassword ? 'text' : 'password'" v-model="editForm.db_password" placeholder="Password" class="w-full text-sm pr-10" />
                <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-600" @click="showEditDBPassword = !showEditDBPassword">
                  <FeatherIcon :name="showEditDBPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <!-- SSH KEY TYPE -->
          <div v-else-if="editForm.secret_type === 'SSH Key'" class="space-y-3.5">
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-sm text-gray-600 font-semibold truncate pr-2">Username</label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.username" placeholder="e.g. root" class="w-full text-sm" />
              </div>
            </div>
            <div class="space-y-1.5 pt-1.5">
              <label class="block text-xs font-semibold text-gray-605">Private Key</label>
              <textarea
                v-model="editForm.ssh_private_key"
                rows="5"
                placeholder="-----BEGIN OPENSSH PRIVATE KEY-----"
                class="w-full rounded border border-gray-200 bg-white p-3 text-xs font-mono text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner"
              />
            </div>
          </div>

          <!-- CERTIFICATE TYPE -->
          <div v-else-if="editForm.secret_type === 'Certificate'" class="space-y-1.5 pt-1.5">
            <label class="block text-xs font-semibold text-gray-605">Certificate Content</label>
            <textarea
              v-model="editForm.certificate"
              rows="5"
              placeholder="-----BEGIN CERTIFICATE-----"
              class="w-full rounded border border-gray-200 bg-white p-3 text-xs font-mono text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner"
            />
          </div>

          <!-- OTHER / NOTE -->
          <div v-else class="text-xs text-gray-400 italic py-1">
            No special custom fields required for {{ editForm.secret_type }}. Use the Notes block below.
          </div>
        </div>

        <!-- Notes Box -->
        <div class="p-4 bg-gray-50/50 border border-gray-100 rounded-xl space-y-2 shadow-sm">
          <label class="block text-xs font-semibold text-gray-600">Notes</label>
          <textarea
            v-model="editForm.notes"
            rows="4"
            placeholder="Add private notes or description..."
            class="w-full rounded border border-gray-200 bg-white p-3 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner"
          />
        </div>
      </div>
      
      <!-- READ MODE LAYOUT (CRM SidePanel Split Style) -->
      <div v-else class="h-full">
        
        <!-- Details Tab -->
        <div v-if="activeTab === 'details'" class="space-y-4">
          
          <!-- Secret Type -->
          <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
            <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">
              Secret Type
            </div>
            <div class="w-[65%] flex items-center justify-start min-w-0">
              <Badge size="md" variant="subtle" :theme="secretData?.secret_type === 'Password' ? 'green' : 'gray'">
                {{ secretData?.secret_type }}
              </Badge>
            </div>
          </div>

          <!-- Folder -->
          <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
            <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">
              Folder
            </div>
            <div class="w-[65%] flex items-center justify-start min-w-0 text-sm font-semibold text-gray-900 truncate">
              {{ getFolderName(secretData?.folder) || '—' }}
            </div>
          </div>

          <!-- Clipboard auto-clear visual indicator -->
          <div v-if="clipboard.copied.value" class="flex items-center gap-2.5 p-3 bg-amber-50/70 text-amber-800 rounded-xl text-xs font-medium border border-amber-100/40 shadow-sm transition-all duration-300">
            <FeatherIcon name="shield" class="w-4 h-4 text-amber-600 animate-pulse shrink-0" />
            <span class="flex-1">Clipboard contains credentials. Wiping in <strong>{{ clipboard.countdown.value }}s</strong>.</span>
          </div>

          <!-- TYPE-SPECIFIC HORIZONTAL FIELDS -->
          <!-- PASSWORD TYPE -->
          <div v-if="secretData?.secret_type === 'Password'" class="space-y-1">
            <!-- URL -->
            <div v-if="secretData?.url" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">URL</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <a :href="secretData.url" target="_blank" class="text-sm font-semibold text-indigo-650 hover:text-indigo-800 hover:underline truncate mr-2 inline-flex items-center gap-1">
                  <span>{{ secretData.url }}</span>
                  <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
                </a>
                <Button variant="ghost" size="sm" @click="copyField(secretData.url, 'url')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'url' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'url'}" />
                </Button>
              </div>
            </div>
            <!-- Username -->
            <div v-if="secretData?.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Username</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.username }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.username, 'username')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'username' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'username'}" />
                </Button>
              </div>
            </div>
            <!-- Password with reveal -->
            <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Password</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono tracking-wider truncate mr-2">
                  {{ showPassword ? decryptedData?.password : '••••••••••••' }}
                </span>
                <div class="flex items-center gap-0.5 shrink-0">
                  <Button variant="ghost" size="sm" @click="togglePassword" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="copyPassword" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="copiedField === 'password' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'password'}" />
                  </Button>
                </div>
              </div>
            </div>
            <!-- Strength -->
            <div v-if="secretData?.password_strength" class="py-2.5 border-b border-gray-100/50">
              <span class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Password Strength</span>
              <PasswordStrength :level="secretData.password_strength" />
            </div>
          </div>

          <!-- API KEY TYPE -->
          <div v-else-if="secretData?.secret_type === 'API Key'" class="space-y-1">
            <!-- URL -->
            <div v-if="secretData?.url" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Endpoint</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <a :href="secretData.url" target="_blank" class="text-sm font-semibold text-indigo-650 hover:text-indigo-800 hover:underline truncate mr-2 inline-flex items-center gap-1">
                  <span>{{ secretData.url }}</span>
                  <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
                </a>
                <Button variant="ghost" size="sm" @click="copyField(secretData.url, 'url')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'url' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'url'}" />
                </Button>
              </div>
            </div>
            <!-- API Key -->
            <div v-if="secretData?.api_key" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">API Key</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.api_key }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.api_key, 'api_key')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'api_key' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'api_key'}" />
                </Button>
              </div>
            </div>
            <!-- API Secret -->
            <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">API Secret</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono tracking-wider truncate mr-2">
                  {{ showAPISecret ? decryptedData?.api_secret : '••••••••••••' }}
                </span>
                <div class="flex items-center gap-0.5 shrink-0">
                  <Button variant="ghost" size="sm" @click="toggleAPISecret" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="showAPISecret ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="copyAPISecret" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="copiedField === 'api_secret' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'api_secret'}" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <!-- CREDIT CARD TYPE -->
          <div v-else-if="secretData?.secret_type === 'Credit Card'" class="space-y-1">
            <!-- Card Holder -->
            <div v-if="secretData?.card_holder" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Card Holder</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 truncate mr-2">{{ secretData.card_holder }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.card_holder, 'card_holder')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'card_holder' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_holder'}" />
                </Button>
              </div>
            </div>
            <!-- Card Number -->
            <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Card Number</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono tracking-wider truncate mr-2">
                  {{ showCardNumber ? decryptedData?.card_number : '•••• •••• •••• ••••' }}
                </span>
                <div class="flex items-center gap-0.5 shrink-0">
                  <Button variant="ghost" size="sm" @click="toggleCardNumber" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="showCardNumber ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="copyCardNumber" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="copiedField === 'card_number' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_number'}" />
                  </Button>
                </div>
              </div>
            </div>
            <!-- Card Expiry -->
            <div v-if="secretData?.card_expiry" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Expiry</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.card_expiry }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.card_expiry, 'card_expiry')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'card_expiry' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_expiry'}" />
                </Button>
              </div>
            </div>
            <!-- Card CVV -->
            <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">CVV</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono tracking-wider truncate mr-2">
                  {{ showCardCVV ? decryptedData?.card_cvv : '•••' }}
                </span>
                <div class="flex items-center gap-0.5 shrink-0">
                  <Button variant="ghost" size="sm" @click="toggleCardCVV" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="showCardCVV ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="copyCardCVV" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="copiedField === 'card_cvv' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_cvv'}" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <!-- DATABASE TYPE -->
          <div v-else-if="secretData?.secret_type === 'Database'" class="space-y-1">
            <!-- Host -->
            <div v-if="secretData?.db_host" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Host</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.db_host }}{{ secretData.db_port ? ':' + secretData.db_port : '' }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.db_host + (secretData.db_port ? ':' + secretData.db_port : ''), 'db_host')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'db_host' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'db_host'}" />
                </Button>
              </div>
            </div>
            <!-- DB Name -->
            <div v-if="secretData?.db_name" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">DB Name</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 truncate mr-2">{{ secretData.db_name }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.db_name, 'db_name')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'db_name' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'db_name'}" />
                </Button>
              </div>
            </div>
            <!-- Username -->
            <div v-if="secretData?.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Username</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.username }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.username, 'username')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'username' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'username'}" />
                </Button>
              </div>
            </div>
            <!-- DB Password -->
            <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Password</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono tracking-wider truncate mr-2">
                  {{ showDBPassword ? decryptedData?.db_password : '••••••••••••' }}
                </span>
                <div class="flex items-center gap-0.5 shrink-0">
                  <Button variant="ghost" size="sm" @click="toggleDBPassword" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="showDBPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="copyDBPassword" class="text-gray-400 hover:text-gray-600">
                    <FeatherIcon :name="copiedField === 'db_password' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'db_password'}" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <!-- SSH KEY TYPE -->
          <div v-else-if="secretData?.secret_type === 'SSH Key'" class="space-y-1">
            <!-- Username -->
            <div v-if="secretData?.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[38px]">
              <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Username</div>
              <div class="w-[65%] flex items-center justify-between min-w-0">
                <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.username }}</span>
                <Button variant="ghost" size="sm" @click="copyField(secretData.username, 'username')" class="text-gray-400 hover:text-gray-600 shrink-0">
                  <FeatherIcon :name="copiedField === 'username' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'username'}" />
                </Button>
              </div>
            </div>
            <!-- SSH Private Key -->
            <div v-if="secretData?.ssh_private_key" class="py-2">
              <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">SSH Private Key</span>
              <div class="relative bg-gray-50 border border-gray-100 rounded-xl p-3.5 group shadow-inner">
                <pre class="text-xs font-mono text-gray-800 overflow-x-auto max-h-40 whitespace-pre select-all leading-normal">{{ secretData.ssh_private_key }}</pre>
                <Button variant="outline" size="sm" @click="copyField(secretData.ssh_private_key, 'ssh_private_key')" class="absolute top-2 right-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border-gray-200">
                  <template #prefix>
                    <FeatherIcon :name="copiedField === 'ssh_private_key' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'ssh_private_key'}" />
                  </template>
                  <span>Copy Key</span>
                </Button>
              </div>
            </div>
          </div>

          <!-- CERTIFICATE TYPE -->
          <div v-else-if="secretData?.secret_type === 'Certificate'" class="space-y-1">
            <!-- Certificate Content -->
            <div v-if="secretData?.certificate" class="py-2">
              <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Certificate</span>
              <div class="relative bg-gray-50 border border-gray-100 rounded-xl p-3.5 group shadow-inner">
                <pre class="text-xs font-mono text-gray-800 overflow-x-auto max-h-40 whitespace-pre select-all leading-normal">{{ secretData.certificate }}</pre>
                <Button variant="outline" size="sm" @click="copyField(secretData.certificate, 'certificate')" class="absolute top-2 right-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border-gray-200">
                  <template #prefix>
                    <FeatherIcon :name="copiedField === 'certificate' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'certificate'}" />
                  </template>
                  <span>Copy Certificate</span>
                </Button>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="secretData?.notes" class="py-2">
            <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Notes</span>
            <div class="p-3.5 bg-gray-50/50 rounded-xl text-sm text-gray-700 prose prose-sm max-w-none border border-gray-100 leading-relaxed shadow-sm" v-html="secretData.notes" />
          </div>
        </div>

        <!-- Activity Tab -->
        <div v-else-if="activeTab === 'activity'" class="space-y-4">
          <div v-if="activity.loading" class="space-y-3">
            <div v-for="i in 3" :key="i" class="h-14 bg-gray-50 border border-gray-100 rounded-xl animate-pulse" />
          </div>
          <div v-else-if="activityList.length" class="relative border-l border-gray-100 ml-4 pl-6 space-y-6 py-2">
            <div v-for="item in activityList" :key="item.name" class="relative flex items-start gap-3">
              <!-- Dot marker -->
              <span class="absolute -left-[31px] top-1.5 w-2.5 h-2.5 rounded-full border-2 border-white bg-gray-400 ring-4 ring-white" />
              <div class="w-8 h-8 rounded-full border border-gray-100 bg-gray-50 flex items-center justify-center shrink-0 shadow-sm">
                <FeatherIcon :name="actionIcons[item.action] || 'activity'" class="w-4 h-4 text-gray-500" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm text-gray-800 leading-snug">
                  <span class="font-semibold text-gray-900">{{ item.user }}</span>
                  {{ item.action.toLowerCase() }} this secret
                </p>
                <p class="text-xs text-gray-400 mt-1 font-medium">{{ formatTime(item.timestamp) }}</p>
              </div>
            </div>
          </div>
          <EmptyState v-else icon="activity" title="No activity yet" />
        </div>

        <!-- Sharing Tab -->
        <div v-else-if="activeTab === 'sharing'" class="space-y-4">
          <Button variant="outline" class="w-full justify-center shadow-sm" @click="showShareDialog = true">
            <template #prefix><FeatherIcon name="user-plus" class="w-4 h-4" /></template>
            <span>Share Secret</span>
          </Button>
          <div class="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center text-xs text-gray-500 font-medium">
            Sharing functionality coming soon.
          </div>
        </div>
      </div>

    </div>

    <!-- Sticky Footer for Save/Cancel Buttons in Edit Mode -->
    <div v-if="isEditing" class="p-4 border-t border-gray-100 bg-gray-50/50 flex items-center justify-end gap-3 shrink-0">
      <Button
        variant="outline"
        @click="isEditing = false"
        class="text-gray-700 hover:bg-gray-100"
      >
        Cancel
      </Button>
      <Button
        variant="solid"
        theme="green"
        @click="handleSave"
        :loading="updateResource.loading"
        class="font-semibold px-4 shadow-sm"
      >
        Save Changes
      </Button>
    </div>

  </aside>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { Button, Badge, FeatherIcon, TextInput, FormControl } from 'frappe-ui'
import { useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret, useUpdateSecret, useFolders } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from './EmptyState.vue'
import PasswordStrength from './PasswordStrength.vue'

const props = defineProps({ name: { type: String, required: true } })
const emit = defineEmits(['close', 'updated', 'deleted'])

const activeTab = ref('details')
const isEditing = ref(false)

// Sensitive fields reveal flags (Read-only view)
const showPassword = ref(false)
const showAPISecret = ref(false)
const showCardNumber = ref(false)
const showCardCVV = ref(false)
const showDBPassword = ref(false)

// Password/Sensitive fields type toggle flags (Edit view)
const showEditPassword = ref(false)
const showEditAPISecret = ref(false)
const showEditCardNumber = ref(false)
const showEditCardCVV = ref(false)
const showEditDBPassword = ref(false)

const showShareDialog = ref(false)

const secret = useSecret(props.name)
const decryptResource = useDecryptSecret()
const activity = useSecretActivity(props.name)
const deleteResource = useDeleteSecret()
const updateResource = useUpdateSecret()
const folders = useFolders()
const clipboard = useClipboard()

const secretData = computed(() => secret.data)
const decryptedData = computed(() => decryptResource.data?.decrypted)
const activityList = computed(() => activity.data || [])

const tabs = [
  { name: 'details', label: 'Details' },
  { name: 'activity', label: 'Activity' },
  { name: 'sharing', label: 'Sharing' },
]

const actionIcons = { Viewed: 'eye', Created: 'plus', Updated: 'edit', Deleted: 'trash', Shared: 'share', Copied: 'copy' }

const typeMeta = {
  Password: { icon: 'key', bg: 'bg-emerald-50 text-emerald-600 border-emerald-100', color: 'text-emerald-600' },
  'API Key': { icon: 'code', bg: 'bg-purple-50 text-purple-600 border-purple-100', color: 'text-purple-600' },
  Note: { icon: 'file-text', bg: 'bg-amber-50 text-amber-600 border-amber-100', color: 'text-amber-600' },
  'SSH Key': { icon: 'terminal', bg: 'bg-slate-50 text-slate-600 border-slate-100', color: 'text-slate-600' },
  Certificate: { icon: 'shield', bg: 'bg-indigo-50 text-indigo-600 border-indigo-100', color: 'text-indigo-600' },
  'Credit Card': { icon: 'credit-card', bg: 'bg-blue-50 text-blue-600 border-blue-100', color: 'text-blue-600' },
  Database: { icon: 'database', bg: 'bg-cyan-50 text-cyan-600 border-cyan-100', color: 'text-cyan-600' },
  Other: { icon: 'lock', bg: 'bg-pink-50 text-pink-600 border-pink-100', color: 'text-pink-600' },
}

const secretTypeOptions = [
  { label: 'Password', value: 'Password' },
  { label: 'API Key', value: 'API Key' },
  { label: 'Note', value: 'Note' },
  { label: 'SSH Key', value: 'SSH Key' },
  { label: 'Certificate', value: 'Certificate' },
  { label: 'Credit Card', value: 'Credit Card' },
  { label: 'Database', value: 'Database' },
  { label: 'Other', value: 'Other' },
]

const folderOptions = computed(() => {
  const options = [{ label: 'No Folder', value: '' }]
  if (folders.data) {
    folders.data.forEach(f => {
      options.push({ label: f.folder_name, value: f.name })
    })
  }
  return options
})

const copiedField = ref(null)

const editForm = reactive({
  title: '',
  secret_type: 'Password',
  folder: '',
  url: '',
  username: '',
  email: '',
  notes: '',
  password: '',
  api_key: '',
  api_secret: '',
  card_holder: '',
  card_number: '',
  card_expiry: '',
  card_cvv: '',
  db_host: '',
  db_port: '',
  db_name: '',
  db_password: '',
  ssh_private_key: '',
  certificate: '',
})

watch(() => props.name, (n) => {
  if (n) {
    secret.submit({ name: n })
    activity.submit({ secret_name: n })
    showPassword.value = false
    showAPISecret.value = false
    showCardNumber.value = false
    showCardCVV.value = false
    showDBPassword.value = false
    isEditing.value = false
  }
})

// Initialize folder resource
folders.submit()

function getFolderName(folderId) {
  if (!folderId) return ''
  const found = folders.data?.find(f => f.name === folderId)
  return found ? found.folder_name : folderId
}

function copyField(value, fieldName) {
  if (!value) return
  clipboard.copy(value)
  copiedField.value = fieldName
  setTimeout(() => {
    if (copiedField.value === fieldName) {
      copiedField.value = null
    }
  }, 3000)
}

async function togglePassword() {
  if (!showPassword.value && !decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }
  showPassword.value = !showPassword.value
}

async function copyPassword() {
  if (!decryptedData.value) await decryptResource.submit({ name: props.name })
  if (decryptedData.value?.password) {
    copyField(decryptedData.value.password, 'password')
  }
}

async function toggleAPISecret() {
  if (!showAPISecret.value && !decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }
  showAPISecret.value = !showAPISecret.value
}

async function copyAPISecret() {
  if (!decryptedData.value) await decryptResource.submit({ name: props.name })
  if (decryptedData.value?.api_secret) {
    copyField(decryptedData.value.api_secret, 'api_secret')
  }
}

async function toggleCardNumber() {
  if (!showCardNumber.value && !decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }
  showCardNumber.value = !showCardNumber.value
}

async function copyCardNumber() {
  if (!decryptedData.value) await decryptResource.submit({ name: props.name })
  if (decryptedData.value?.card_number) {
    copyField(decryptedData.value.card_number, 'card_number')
  }
}

async function toggleCardCVV() {
  if (!showCardCVV.value && !decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }
  showCardCVV.value = !showCardCVV.value
}

async function copyCardCVV() {
  if (!decryptedData.value) await decryptResource.submit({ name: props.name })
  if (decryptedData.value?.card_cvv) {
    copyField(decryptedData.value.card_cvv, 'card_cvv')
  }
}

async function toggleDBPassword() {
  if (!showDBPassword.value && !decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }
  showDBPassword.value = !showDBPassword.value
}

async function copyDBPassword() {
  if (!decryptedData.value) await decryptResource.submit({ name: props.name })
  if (decryptedData.value?.db_password) {
    copyField(decryptedData.value.db_password, 'db_password')
  }
}

async function toggleEditMode() {
  if (isEditing.value) {
    isEditing.value = false
    return
  }

  // Decrypt everything before entering edit mode to pre-fill raw inputs instead of masks
  if (!decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }

  showEditPassword.value = false
  showEditAPISecret.value = false
  showEditCardNumber.value = false
  showEditCardCVV.value = false
  showEditDBPassword.value = false

  const sd = secretData.value || {}
  const dd = decryptedData.value || {}

  editForm.title = sd.title || ''
  editForm.secret_type = sd.secret_type || 'Password'
  editForm.folder = sd.folder || ''
  editForm.url = sd.url || ''
  editForm.username = sd.username || ''
  editForm.email = sd.email || ''
  editForm.notes = sd.notes || ''

  editForm.password = dd.password || ''
  editForm.api_key = sd.api_key || ''
  editForm.api_secret = dd.api_secret || ''
  editForm.card_holder = sd.card_holder || ''
  editForm.card_number = dd.card_number || ''
  editForm.card_expiry = sd.card_expiry || ''
  editForm.card_cvv = dd.card_cvv || ''
  editForm.db_host = sd.db_host || ''
  editForm.db_port = sd.db_port || ''
  editForm.db_name = sd.db_name || ''
  editForm.db_password = dd.db_password || ''
  editForm.ssh_private_key = sd.ssh_private_key || ''
  editForm.certificate = sd.certificate || ''

  isEditing.value = true
}

async function handleSave() {
  if (!editForm.title || !editForm.title.trim()) {
    alert('Please enter a secret title')
    return
  }

  try {
    const payload = {
      title: editForm.title,
      secret_type: editForm.secret_type,
      folder: editForm.folder,
      notes: editForm.notes,
    }

    if (editForm.secret_type === 'Password') {
      payload.username = editForm.username
      payload.password = editForm.password
      payload.url = editForm.url
    } else if (editForm.secret_type === 'API Key') {
      payload.api_key = editForm.api_key
      payload.api_secret = editForm.api_secret
      payload.url = editForm.url
    } else if (editForm.secret_type === 'Credit Card') {
      payload.card_holder = editForm.card_holder
      payload.card_number = editForm.card_number
      payload.card_expiry = editForm.card_expiry
      payload.card_cvv = editForm.card_cvv
    } else if (editForm.secret_type === 'Database') {
      payload.db_host = editForm.db_host
      payload.db_port = editForm.db_port
      payload.db_name = editForm.db_name
      payload.username = editForm.username
      payload.db_password = editForm.db_password
    } else if (editForm.secret_type === 'SSH Key') {
      payload.username = editForm.username
      payload.ssh_private_key = editForm.ssh_private_key
    } else if (editForm.secret_type === 'Certificate') {
      payload.certificate = editForm.certificate
    }

    await updateResource.submit({
      name: props.name,
      ...payload,
    })

    isEditing.value = false
    
    // Refresh local components and data
    await secret.submit({ name: props.name })
    await activity.submit({ secret_name: props.name })
    decryptResource.submit({ name: props.name })

    emit('updated')
  } catch (e) {
    console.error('Save failed:', e)
  }
}

async function handleDelete() {
  if (confirm('Are you sure you want to permanently delete this secret? This action cannot be undone.')) {
    try {
      await deleteResource.submit({ name: props.name })
      emit('deleted')
    } catch (e) {
      console.error('Delete failed:', e)
    }
  }
}

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
