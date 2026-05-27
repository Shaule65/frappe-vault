<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/20">
    
    <!-- Page Header (Identical to CRM splitscreen headers) -->
    <header class="flex h-14 items-center justify-between border-b bg-white px-5 py-3 shrink-0">
      <!-- Breadcrumbs -->
      <div class="flex items-center gap-2 text-sm">
        <router-link to="/secrets" class="text-gray-500 hover:text-gray-950 font-medium transition-colors">Secrets</router-link>
        <FeatherIcon name="chevron-right" class="w-3.5 h-3.5 text-gray-300" />
        <span class="font-semibold text-gray-900">{{ secretData?.title || 'Loading...' }}</span>
      </div>
      
      <!-- Right actions -->
      <div class="flex items-center gap-2">
      </div>
    </header>

    <!-- Splitscreen Main Content Body (Exact CRM split match) -->
    <div v-if="secretData" class="flex-1 flex overflow-hidden min-h-0">
      
      <!-- LEFT PANE: Tab navigation & Activity timeline feed -->
      <div class="flex-1 flex flex-col overflow-hidden bg-white border-r border-gray-100">
        <!-- Borderless navigation tabs (matching CRM layout) -->
        <div class="flex items-center gap-7.5 px-6 border-b border-gray-100 bg-white shrink-0 min-h-[45px]">
          <button
            v-for="t in tabs"
            :key="t.name"
            class="py-3.5 text-sm font-medium relative focus:outline-none transition-colors"
            :class="activeTab === t.name ? 'text-gray-950 font-bold' : 'text-gray-400 hover:text-gray-950'"
            @click="activeTab = t.name"
          >
            <span>{{ t.label }}</span>
            <span
              v-if="activeTab === t.name"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-950 rounded-full"
            />
          </button>
        </div>

        <!-- Tab Panel content container -->
        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          
          <!-- Activity feed timeline panel -->
          <div v-if="activeTab === 'activity'" class="space-y-6">
            <div class="flex items-center justify-between border-b border-gray-100 pb-3 mb-5">
              <h3 class="text-base font-semibold text-gray-900">Activity Timeline</h3>
            </div>
            
            <div v-if="activity.loading" class="space-y-4">
              <div v-for="i in 3" :key="i" class="h-16 bg-gray-50/50 border border-gray-100 rounded-xl animate-pulse" />
            </div>
            
            <div v-else-if="activityList.length" class="relative border-l border-gray-100 ml-4 pl-6 space-y-6 py-2">
              <div v-for="item in activityList" :key="item.name" class="relative flex items-start gap-4">
                <!-- Dot marker -->
                <span class="absolute -left-[31px] top-2 w-2.5 h-2.5 rounded-full border-2 border-white bg-gray-450 ring-4 ring-white" />
                
                <div class="w-8.5 h-8.5 rounded-full border border-gray-100 bg-gray-50 flex items-center justify-center shrink-0 shadow-sm">
                  <FeatherIcon :name="actionIcons[item.action] || 'activity'" class="w-4 h-4 text-gray-500" />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-800 leading-snug mt-0.5">
                    <span class="font-bold text-gray-950">{{ item.user }}</span>
                    {{ item.action.toLowerCase() }} this secret
                  </p>
                  <p class="text-xs text-gray-400 mt-1 font-medium">{{ formatTime(item.timestamp) }}</p>
                </div>
              </div>
            </div>
            
            <EmptyState v-else icon="activity" title="No activity recorded" />
          </div>

          <!-- Sharing config panel -->
          <div v-else-if="activeTab === 'sharing'" class="space-y-4 max-w-lg">
            <h3 class="text-base font-semibold text-gray-900 border-b border-gray-100 pb-3">Sharing Settings</h3>
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

      <!-- RIGHT PANE: Resizable Side Panel Drawer (off-white bg, bordered) -->
      <div class="w-[380px] shrink-0 flex flex-col bg-gray-50/30 overflow-y-auto border-l border-gray-100 flex-1 lg:flex-none">
        
        <!-- Sidebar Top Header details (Avatar, Title, and ID Copy badge) -->
        <div class="flex items-center gap-4 p-5 border-b border-gray-100 shrink-0">
          <!-- Circular type avatar icon -->
          <div :class="`w-12 h-12 rounded-full border flex items-center justify-center shrink-0 shadow-sm ${typeMeta[secretData.secret_type || 'Other']?.bg}`">
            <FeatherIcon :name="typeMeta[secretData.secret_type || 'Other']?.icon" class="w-5.5 h-5.5" />
          </div>
          
          <div class="min-w-0 flex-1">
            <h2 class="font-bold text-lg text-gray-950 leading-tight truncate" :title="secretData.title">
              {{ secretData.title }}
            </h2>
            <div class="flex items-center gap-2 mt-1.5">
              <button
                @click="copyField(secretData.name, 'name')"
                class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors group cursor-pointer"
              >
                <span>{{ secretData.name }}</span>
                <FeatherIcon :name="copiedField === 'name' ? 'check' : 'copy'" class="w-3 h-3 text-gray-400 group-hover:text-gray-650" :class="{'text-green-600': copiedField === 'name'}" />
              </button>
              
              <Badge v-if="secretData.is_favorite" theme="yellow" size="sm" variant="subtle" class="gap-0.5">
                <FeatherIcon name="star" class="w-2.5 h-2.5 fill-yellow-500 text-yellow-500" />
                <span>Fav</span>
              </Badge>
            </div>
          </div>
        </div>

        <!-- Sidebar Top Quick Action Button Row (Copy fields, edit mode toggle, delete) -->
        <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between shrink-0 bg-white/40">
          <div class="flex items-center gap-1.5">
            <!-- Copy Username action -->
            <Button
              v-if="secretData.username"
              variant="ghost"
              size="sm"
              :tooltip="'Copy Username'"
              @click="copyField(secretData.username, 'username')"
              class="text-gray-450 hover:text-gray-800"
            >
              <template #icon>
                <FeatherIcon :name="copiedField === 'username' ? 'check' : 'user'" class="w-4 h-4" :class="{'text-green-600': copiedField === 'username'}" />
              </template>
            </Button>
            
            <!-- Reveal / Copy Password action -->
            <Button
              v-if="secretData.secret_type === 'Password'"
              variant="ghost"
              size="sm"
              :tooltip="'Copy Password'"
              @click="copyPassword"
              class="text-gray-450 hover:text-gray-800"
            >
              <template #icon>
                <FeatherIcon :name="copiedField === 'password' ? 'check' : 'key'" class="w-4 h-4" :class="{'text-green-600': copiedField === 'password'}" />
              </template>
            </Button>

            <!-- Copy API Key/Secret action -->
            <Button
              v-if="secretData.secret_type === 'API Key'"
              variant="ghost"
              size="sm"
              :tooltip="'Copy API Secret'"
              @click="copyAPISecret"
              class="text-gray-450 hover:text-gray-800"
            >
              <template #icon>
                <FeatherIcon :name="copiedField === 'api_secret' ? 'check' : 'code'" class="w-4 h-4" :class="{'text-green-600': copiedField === 'api_secret'}" />
              </template>
            </Button>

            <!-- Link click action -->
            <Button
              v-if="secretData.url"
              variant="ghost"
              size="sm"
              :tooltip="'Open URL'"
              @click="window.open(secretData.url, '_blank')"
              class="text-gray-450 hover:text-gray-800"
            >
              <template #icon><FeatherIcon name="external-link" class="w-4 h-4" /></template>
            </Button>

            <!-- Delete action -->
            <Button
              variant="ghost"
              size="sm"
              theme="red"
              :tooltip="'Delete'"
              @click="showDeleteDialog = true"
              class="text-gray-450 hover:text-red-600 hover:bg-red-50"
            >
              <template #icon><FeatherIcon name="trash-2" class="w-4 h-4" /></template>
            </Button>
          </div>

          <!-- Edit mode trigger -->
          <Button
            variant="outline"
            size="sm"
            @click="toggleEditMode"
            :class="isEditing ? 'bg-gray-100 text-gray-950 font-bold border-gray-300' : 'text-gray-700 hover:bg-gray-50'"
          >
            <template #prefix>
              <FeatherIcon :name="isEditing ? 'eye' : 'edit-2'" class="w-3.5 h-3.5" />
            </template>
            <span>{{ isEditing ? 'View' : 'Edit' }}</span>
          </Button>
        </div>

        <!-- Sidebar Content block list -->
        <div class="flex-1 p-5 space-y-6">
          
          <!-- Clipboard clear warning indicator -->
          <div v-if="clipboard.copied.value" class="flex items-center gap-2.5 p-3 bg-amber-50/70 text-amber-800 rounded-xl text-xs font-semibold border border-amber-100/40 shadow-sm transition-all duration-300">
            <FeatherIcon name="shield" class="w-4 h-4 text-amber-600 animate-pulse shrink-0" />
            <span class="flex-1">Clipboard copied. Auto-clearing in <strong>{{ clipboard.countdown.value }}s</strong>.</span>
          </div>

          <!-- EDIT VIEW FORM (CRM SIDEBAR SPLIT) -->
          <div v-if="isEditing" class="space-y-5">
            <!-- Title -->
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Title <span class="text-red-550">*</span></label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.title" placeholder="Secret Title" class="w-full text-sm" />
              </div>
            </div>

            <!-- Type select -->
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Type</label>
              <div class="w-[65%]">
                <FormControl v-model="editForm.secret_type" type="select" :options="secretTypeOptions" class="w-full text-sm cursor-pointer" />
              </div>
            </div>

            <!-- Folder select -->
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Folder</label>
              <div class="w-[65%]">
                <FormControl v-model="editForm.folder" type="select" :options="folderOptions" class="w-full text-sm cursor-pointer" />
              </div>
            </div>

            <div class="w-full border-t border-gray-100 my-4" />

            <!-- Dynamic type inputs -->
            <!-- PASSWORD TYPE -->
            <div v-if="editForm.secret_type === 'Password'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Username</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Password</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditPassword ? 'text' : 'password'" v-model="editForm.password" placeholder="Password" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-650" @click="showEditPassword = !showEditPassword">
                    <FeatherIcon :name="showEditPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">URL</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.url" placeholder="https://example.com" class="w-full text-sm" />
                </div>
              </div>
            </div>

            <!-- API KEY TYPE -->
            <div v-else-if="editForm.secret_type === 'API Key'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">API Key</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.api_key" placeholder="API Key" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">API Secret</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditAPISecret ? 'text' : 'password'" v-model="editForm.api_secret" placeholder="API Secret" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-650" @click="showEditAPISecret = !showEditAPISecret">
                    <FeatherIcon :name="showEditAPISecret ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">URL</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.url" placeholder="https://api.example.com" class="w-full text-sm" />
                </div>
              </div>
            </div>

            <!-- CREDIT CARD TYPE -->
            <div v-else-if="editForm.secret_type === 'Credit Card'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Card Holder</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.card_holder" placeholder="Holder Name" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Card Number</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditCardNumber ? 'text' : 'password'" v-model="editForm.card_number" placeholder="Card Number" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-655" @click="showEditCardNumber = !showEditCardNumber">
                    <FeatherIcon :name="showEditCardNumber ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Expiry</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.card_expiry" placeholder="MM/YY" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">CVV</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditCardCVV ? 'text' : 'password'" v-model="editForm.card_cvv" placeholder="CVV" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-655" @click="showEditCardCVV = !showEditCardCVV">
                    <FeatherIcon :name="showEditCardCVV ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- DATABASE TYPE -->
            <div v-else-if="editForm.secret_type === 'Database'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Host</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.db_host" placeholder="localhost" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Port</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.db_port" placeholder="3306" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">DB Name</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.db_name" placeholder="my_database" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Username</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Password</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditDBPassword ? 'text' : 'password'" v-model="editForm.db_password" placeholder="Password" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-655" @click="showEditDBPassword = !showEditDBPassword">
                    <FeatherIcon :name="showEditDBPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- SSH KEY TYPE -->
            <div v-else-if="editForm.secret_type === 'SSH Key'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] shrink-0 text-xs font-bold text-gray-500 uppercase tracking-wider pr-2">Username</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.username" placeholder="e.g. root" class="w-full text-sm" />
                </div>
              </div>
              <div class="space-y-1.5 pt-1.5">
                <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider">Private Key</label>
                <textarea v-model="editForm.ssh_private_key" rows="6" placeholder="-----BEGIN OPENSSH KEY-----" class="w-full rounded border border-gray-200 bg-white p-3 text-xs font-mono text-gray-800 placeholder-gray-450 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner" />
              </div>
            </div>

            <!-- CERTIFICATE TYPE -->
            <div v-else-if="editForm.secret_type === 'Certificate'" class="space-y-1.5 pt-1.5">
              <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider">Certificate Content</label>
              <textarea v-model="editForm.certificate" rows="6" placeholder="-----BEGIN CERTIFICATE-----" class="w-full rounded border border-gray-200 bg-white p-3 text-xs font-mono text-gray-800 placeholder-gray-455 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner" />
            </div>

            <!-- Stacked Notes Box -->
            <div class="space-y-1.5 pt-1.5">
              <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider">Notes</label>
              <textarea v-model="editForm.notes" rows="4" placeholder="Enter notes..." class="w-full rounded border border-gray-200 bg-white p-3 text-sm text-gray-850 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner" />
            </div>

            <!-- Edit Sticky Buttons -->
            <div class="flex items-center justify-end gap-3 pt-3 border-t border-gray-100">
              <Button variant="outline" @click="isEditing = false" class="text-gray-700 hover:bg-gray-100">Cancel</Button>
              <Button variant="solid" theme="green" @click="handleSave" :loading="updateResource.loading" class="font-semibold shadow-sm px-4">Save Changes</Button>
            </div>
          </div>

          <!-- READ ONLY VIEW COLLAPSIBLES (CRM STYLE DETAILS DRAWER) -->
          <template v-else>
            
            <!-- Collapsible DETAILS Accordion -->
            <div class="border-b border-gray-100 pb-4">
              <button @click="detailsOpen = !detailsOpen" class="w-full flex items-center justify-between text-xs font-bold text-gray-500 uppercase tracking-wider focus:outline-none mb-4 py-1 select-none text-left">
                <span>Details</span>
                <FeatherIcon :name="detailsOpen ? 'chevron-down' : 'chevron-right'" class="w-4 h-4 text-gray-400" />
              </button>

              <div v-if="detailsOpen" class="space-y-1">
                <!-- Secret Type -->
                <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                  <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Secret Type</div>
                  <div class="w-[65%] flex items-center justify-start min-w-0">
                    <Badge size="md" variant="subtle" :theme="secretData.secret_type === 'Password' ? 'green' : 'gray'">
                      {{ secretData.secret_type }}
                    </Badge>
                  </div>
                </div>

                <!-- Folder -->
                <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                  <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Folder</div>
                  <div class="w-[65%] flex items-center justify-start min-w-0 text-sm font-semibold text-gray-900 truncate">
                    {{ getFolderName(secretData.folder) || '—' }}
                  </div>
                </div>

                <!-- Password Type specific fields -->
                <div v-if="secretData.secret_type === 'Password'" class="space-y-1">
                  <div v-if="secretData.url" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">URL</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <a :href="secretData.url" target="_blank" class="text-sm font-semibold text-indigo-650 hover:text-indigo-800 hover:underline truncate mr-2 inline-flex items-center gap-1">
                        <span>{{ secretData.url }}</span>
                        <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                  <div v-if="secretData.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Username</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.username }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Password</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-805 font-mono tracking-wider truncate mr-2">
                        {{ showPassword ? decryptedData?.password : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="togglePassword" class="text-gray-400 hover:text-gray-650">
                          <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- API Key specific fields -->
                <div v-else-if="secretData.secret_type === 'API Key'" class="space-y-1">
                  <div v-if="secretData.url" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Endpoint</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <a :href="secretData.url" target="_blank" class="text-sm font-semibold text-indigo-650 hover:text-indigo-800 hover:underline truncate mr-2 inline-flex items-center gap-1">
                        <span>{{ secretData.url }}</span>
                        <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                  <div v-if="secretData.api_key" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">API Key</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 font-mono truncate mr-2">{{ secretData.api_key }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">API Secret</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 font-mono tracking-wider truncate mr-2">
                        {{ showAPISecret ? decryptedData?.api_secret : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleAPISecret" class="text-gray-400 hover:text-gray-650">
                          <FeatherIcon :name="showAPISecret ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Credit Card specific fields -->
                <div v-else-if="secretData.secret_type === 'Credit Card'" class="space-y-1">
                  <div v-if="secretData.card_holder" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Card Holder</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 truncate mr-2">{{ secretData.card_holder }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Card Number</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 font-mono tracking-wider truncate mr-2">
                        {{ showCardNumber ? decryptedData?.card_number : '•••• •••• •••• ••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleCardNumber" class="text-gray-400 hover:text-gray-650">
                          <FeatherIcon :name="showCardNumber ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div v-if="secretData.card_expiry" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Expiry</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 font-mono truncate mr-2">{{ secretData.card_expiry }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">CVV</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 font-mono tracking-wider truncate mr-2">
                        {{ showCardCVV ? decryptedData?.card_cvv : '•••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleCardCVV" class="text-gray-400 hover:text-gray-650">
                          <FeatherIcon :name="showCardCVV ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Database specific fields -->
                <div v-else-if="secretData.secret_type === 'Database'" class="space-y-1">
                  <div v-if="secretData.db_host" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Host</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 font-mono truncate mr-2">{{ secretData.db_host }}{{ secretData.db_port ? ':' + secretData.db_port : '' }}</span>
                    </div>
                  </div>
                  <div v-if="secretData.db_name" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">DB Name</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-850 truncate mr-2">{{ secretData.db_name }}</span>
                    </div>
                  </div>
                  <div v-if="secretData.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Username</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.username }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Password</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-800 font-mono tracking-wider truncate mr-2">
                        {{ showDBPassword ? decryptedData?.db_password : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleDBPassword" class="text-gray-400 hover:text-gray-650">
                          <FeatherIcon :name="showDBPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- SSH Key specific fields -->
                <div v-else-if="secretData.secret_type === 'SSH Key'" class="space-y-1">
                  <div v-if="secretData.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] shrink-0 text-sm text-gray-500 font-medium truncate pr-2">Username</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-sm font-semibold text-gray-800 font-mono truncate mr-2">{{ secretData.username }}</span>
                    </div>
                  </div>
                  <div v-if="secretData.ssh_private_key" class="py-2.5">
                    <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">SSH Private Key</span>
                    <div class="relative bg-gray-50 border border-gray-100 rounded-xl p-3.5 group shadow-inner">
                      <pre class="text-xs font-mono text-gray-800 overflow-x-auto max-h-40 whitespace-pre select-all leading-normal">{{ secretData.ssh_private_key }}</pre>
                      <Button variant="outline" size="sm" @click="copyField(secretData.ssh_private_key, 'ssh_private_key')" class="absolute top-2 right-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border-gray-200">
                        <template #prefix>
                          <FeatherIcon :name="copiedField === 'ssh_private_key' ? 'check' : 'copy'" class="w-3 h-3" :class="{'text-green-600': copiedField === 'ssh_private_key'}" />
                        </template>
                        <span>Copy</span>
                      </Button>
                    </div>
                  </div>
                </div>

                <!-- Certificate specific fields -->
                <div v-else-if="secretData.secret_type === 'Certificate'" class="space-y-1">
                  <div v-if="secretData.certificate" class="py-2.5">
                    <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Certificate</span>
                    <div class="relative bg-gray-50 border border-gray-100 rounded-xl p-3.5 group shadow-inner">
                      <pre class="text-xs font-mono text-gray-800 overflow-x-auto max-h-40 whitespace-pre select-all leading-normal">{{ secretData.certificate }}</pre>
                      <Button variant="outline" size="sm" @click="copyField(secretData.certificate, 'certificate')" class="absolute top-2 right-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border-gray-200">
                        <template #prefix>
                          <FeatherIcon :name="copiedField === 'certificate' ? 'check' : 'copy'" class="w-3 h-3" :class="{'text-green-600': copiedField === 'certificate'}" />
                        </template>
                        <span>Copy</span>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Collapsible NOTES Accordion -->
            <div v-if="secretData.notes" class="border-b border-gray-100 pb-4">
              <button @click="notesOpen = !notesOpen" class="w-full flex items-center justify-between text-xs font-bold text-gray-500 uppercase tracking-wider focus:outline-none mb-3 py-1 select-none text-left">
                <span>Notes</span>
                <FeatherIcon :name="notesOpen ? 'chevron-down' : 'chevron-right'" class="w-4 h-4 text-gray-400" />
              </button>
              
              <div v-if="notesOpen" class="p-3.5 bg-gray-50/50 rounded-xl text-sm text-gray-700 border border-gray-100 leading-relaxed shadow-sm whitespace-pre-wrap" v-html="secretData.notes" />
            </div>

            <!-- Collapsible METADATA Accordion -->
            <div class="border-b border-gray-100 pb-4">
              <button @click="metaOpen = !metaOpen" class="w-full flex items-center justify-between text-xs font-bold text-gray-500 uppercase tracking-wider focus:outline-none mb-4 py-1 select-none text-left">
                <span>Metadata</span>
                <FeatherIcon :name="metaOpen ? 'chevron-down' : 'chevron-right'" class="w-4 h-4 text-gray-400" />
              </button>

              <div v-if="metaOpen" class="space-y-2">
                <!-- Strength bar -->
                <div v-if="secretData.secret_type === 'Password' && secretData.password_strength" class="py-1 flex items-center justify-between">
                  <span class="text-sm text-gray-500 font-medium">Strength</span>
                  <Badge size="sm" :theme="secretData.password_strength === 'weak' ? 'red' : 'green'" variant="subtle">
                    {{ secretData.password_strength }}
                  </Badge>
                </div>
                
                <!-- Last accessed -->
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="text-gray-500 font-medium">Last Accessed</span>
                  <span class="text-gray-900 font-semibold">{{ formatDateOnly(secretData.last_accessed) }}</span>
                </div>
                
                <!-- Access count -->
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="text-gray-500 font-medium">Access Count</span>
                  <span class="text-gray-900 font-semibold">{{ secretData.access_count || 0 }} times</span>
                </div>

                <!-- Last changed -->
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="text-gray-500 font-medium">Last Changed</span>
                  <span class="text-gray-900 font-semibold">{{ formatDateOnly(secretData.password_last_changed) }}</span>
                </div>
              </div>
            </div>

          </template>
        </div>
      </div>
      
    </div>

    <!-- Delete Confirmation Dialog (matching CRM/Frappe UI styles) -->
    <Dialog
      v-model="showDeleteDialog"
      :options="{
        title: 'Delete Secret',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-3">
          <p class="text-sm text-gray-600 mt-1 leading-normal">
            Are you sure you want to permanently delete <strong>{{ secretData?.title }}</strong>? This action cannot be undone.
          </p>
          <ErrorMessage v-if="deleteError" :message="deleteError" />
        </div>
      </template>
      <template #actions>
        <div class="flex items-center justify-end gap-2 px-4 pb-4">
          <Button variant="outline" @click="showDeleteDialog = false" class="text-gray-700 hover:bg-gray-100">
            Cancel
          </Button>
          <Button variant="solid" theme="red" @click="confirmDelete" :loading="deleteResource.loading" class="font-semibold shadow-sm px-4">
            Delete
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, FeatherIcon, TextInput, FormControl, Dialog, ErrorMessage, toast } from 'frappe-ui'
import { useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret, useUpdateSecret, useFolders } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from '../components/EmptyState.vue'
import PasswordStrength from '../components/PasswordStrength.vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  }
})

const router = useRouter()

const activeTab = ref('activity')
const isEditing = ref(false)

// Collapsible blocks
const detailsOpen = ref(true)
const notesOpen = ref(true)
const metaOpen = ref(true)

// Sensitive fields reveal flags (Read-only view)
const showPassword = ref(false)
const showAPISecret = ref(false)
const showCardNumber = ref(false)
const showCardCVV = ref(false)
const showDBPassword = ref(false)

// Sensitive fields type toggle flags (Edit view)
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
}, { immediate: true })

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
    toast.error('Please enter a secret title')
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
    await secret.submit({ name: props.name })
    await activity.submit({ secret_name: props.name })
    decryptResource.submit({ name: props.name })
  } catch (e) {
    console.error('Save failed:', e)
    toast.error(e.messages?.[0] || e.message || 'Failed to save changes')
  }
}

const showDeleteDialog = ref(false)
const deleteError = ref('')

async function confirmDelete() {
  deleteError.value = ''
  try {
    await deleteResource.submit({ name: props.name })
    showDeleteDialog.value = false
    toast.success('Secret deleted successfully')
    router.push('/secrets')
  } catch (err) {
    console.error('Delete failed:', err)
    deleteError.value = err.messages?.[0] || err.message || 'Failed to delete secret'
    toast.error(deleteError.value)
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

function formatDateOnly(dt) {
  if (!dt) return 'Never'
  return new Date(dt).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>
