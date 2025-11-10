<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Header Bar -->
    <div class="bg-white shadow-md border-b border-gray-200 mb-8">
      <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 py-6">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Invoice Dashboard</h1>
            <p class="text-gray-600">Manage and track all your invoices</p>
          </div>
          <div class="flex items-center gap-3">
            <!-- View Toggle Buttons -->
            <div class="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                @click="viewMode = 'grid'"
                :class="{
                  'bg-white text-blue-600 shadow-sm': viewMode === 'grid',
                  'text-gray-600 hover:text-gray-900': viewMode !== 'grid'
                }"
                class="p-2 rounded-md transition-all duration-200"
                title="Grid View"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                @click="viewMode = 'list'"
                :class="{
                  'bg-white text-blue-600 shadow-sm': viewMode === 'list',
                  'text-gray-600 hover:text-gray-900': viewMode !== 'list'
                }"
                class="p-2 rounded-md transition-all duration-200"
                title="List View"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </button>
            </div>
            <NuxtLink
              to="/invoices/new"
              class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl font-semibold flex items-center gap-2 whitespace-nowrap"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New Invoice
            </NuxtLink>
            <button
              @click="handleLogout"
              class="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-3 rounded-lg hover:from-red-700 hover:to-red-800 transition-all duration-200 shadow-lg hover:shadow-xl font-semibold flex items-center gap-2 whitespace-nowrap"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 pb-10">
      <!-- Statistics Cards -->
      <div v-if="!loading && !error" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 text-sm font-medium">Total Invoices</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ invoices.length }}</p>
            </div>
            <div class="bg-blue-100 rounded-full p-3">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 text-sm font-medium">Total Amount</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">RM {{ totalAmount.toLocaleString() }}</p>
            </div>
            <div class="bg-green-100 rounded-full p-3">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-emerald-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 text-sm font-medium">Paid</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ paidCount }}</p>
            </div>
            <div class="bg-emerald-100 rounded-full p-3">
              <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 text-sm font-medium">Unpaid</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ unpaidCount }}</p>
            </div>
            <div class="bg-red-100 rounded-full p-3">
              <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-20">
        <div class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
        <p class="mt-6 text-gray-600 text-lg font-medium">Loading invoices...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-500 text-red-700 p-6 rounded-lg shadow-lg mb-6">
        <div class="flex items-center">
          <svg class="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <p class="font-semibold">{{ error }}</p>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="invoices.length === 0" class="bg-white rounded-xl shadow-lg p-12 text-center">
        <div class="max-w-md mx-auto">
          <div class="bg-gray-100 rounded-full p-6 w-24 h-24 mx-auto mb-6 flex items-center justify-center">
            <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">No invoices yet</h3>
          <p class="text-gray-600 mb-6">Get started by creating your first invoice</p>
          <NuxtLink
            to="/invoices/new"
            class="inline-block bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl font-semibold"
          >
            Create Your First Invoice
          </NuxtLink>
        </div>
      </div>

      <!-- Invoices Grid View -->
      <div v-else-if="viewMode === 'grid'" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="invoice in invoices"
          :key="invoice.id"
          class="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-100 group"
        >
        <!-- Card Header -->
        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900 mb-1">{{ invoice.invoice_no }}</h3>
              <p class="text-sm text-gray-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {{ invoice.client_name }}
              </p>
            </div>
            <span
              :class="{
                'bg-green-100 text-green-800 border-green-200': invoice.status === 'Paid',
                'bg-red-100 text-red-800 border-red-200': invoice.status === 'Unpaid',
              }"
              class="px-3 py-1 rounded-full text-xs font-bold border-2 uppercase tracking-wide"
            >
              {{ invoice.status }}
            </span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="p-6">
          <div class="space-y-4 mb-6">
            <div class="flex justify-between items-center">
              <span class="text-gray-600 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Amount
              </span>
              <span class="text-2xl font-bold text-gray-900">RM {{ parseFloat(invoice.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
            </div>
            
            <div class="flex justify-between items-center">
              <span class="text-gray-600 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Date
              </span>
              <span class="font-medium text-gray-900">{{ formatDate(invoice.date) }}</span>
            </div>
            
            <div class="flex justify-between items-center">
              <span class="text-gray-600 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Expiration
              </span>
              <span :class="getExpirationColor(invoice.date)" class="font-semibold">
                {{ getExpirationStatus(invoice.date) }}
              </span>
            </div>
          </div>

          <!-- Expiration Indicator Bar -->
          <div class="mb-6">
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                :class="getExpirationBarColor(invoice.date)"
                :style="{ width: getExpirationPercentage(invoice.date) + '%' }"
                class="h-full transition-all duration-500 rounded-full"
              ></div>
            </div>
          </div>

          <!-- Card Footer -->
          <div class="pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between mb-3">
              <span
                :class="{
                  'text-green-600 bg-green-50': invoice.is_done,
                  'text-gray-500 bg-gray-50': !invoice.is_done,
                }"
                class="px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1"
              >
                <svg v-if="invoice.is_done" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
                {{ invoice.is_done ? 'Completed' : 'Pending' }}
              </span>
              <NuxtLink
                :to="`/invoices/${invoice.id}/edit`"
                class="text-blue-600 hover:text-blue-800 font-semibold text-sm flex items-center gap-1 transition-all"
              >
                Edit
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </NuxtLink>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex gap-2">
              <button
                @click="toggleDone(invoice)"
                :disabled="togglingId === invoice.id"
                :class="{
                  'bg-green-600 hover:bg-green-700': !invoice.is_done,
                  'bg-gray-400 hover:bg-gray-500': invoice.is_done,
                }"
                class="flex-1 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="togglingId === invoice.id" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <svg v-else-if="invoice.is_done" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ invoice.is_done ? 'Undo' : 'Mark Done' }}
              </button>
              
              <button
                @click="confirmDelete(invoice)"
                :disabled="deletingId === invoice.id"
                class="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="deletingId === invoice.id" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Invoices List View -->
      <div v-else-if="viewMode === 'list'" class="space-y-4">
        <div
          v-for="invoice in invoices"
          :key="invoice.id"
          class="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden"
        >
          <div class="p-6">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <!-- Left Section -->
              <div class="flex-1">
                <div class="flex items-start justify-between mb-3">
                  <div>
                    <h3 class="text-xl font-bold text-gray-900 mb-1">{{ invoice.invoice_no }}</h3>
                    <p class="text-sm text-gray-600 flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      {{ invoice.client_name }}
                    </p>
                  </div>
                  <span
                    :class="{
                      'bg-green-100 text-green-800 border-green-200': invoice.status === 'Paid',
                      'bg-red-100 text-red-800 border-red-200': invoice.status === 'Unpaid',
                    }"
                    class="px-3 py-1 rounded-full text-xs font-bold border-2 uppercase tracking-wide"
                  >
                    {{ invoice.status }}
                  </span>
                </div>

                <!-- Invoice Details -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Amount</p>
                    <p class="text-lg font-bold text-gray-900">RM {{ parseFloat(invoice.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Date</p>
                    <p class="text-sm font-medium text-gray-900">{{ formatDate(invoice.date) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Expiration</p>
                    <p :class="getExpirationColor(invoice.date)" class="text-sm font-semibold">
                      {{ getExpirationStatus(invoice.date) }}
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Status</p>
                    <span
                      :class="{
                        'text-green-600 bg-green-50': invoice.is_done,
                        'text-gray-500 bg-gray-50': !invoice.is_done,
                      }"
                      class="px-2 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-1"
                    >
                      <svg v-if="invoice.is_done" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      {{ invoice.is_done ? 'Done' : 'Pending' }}
                    </span>
                  </div>
                </div>

                <!-- Expiration Bar -->
                <div class="mb-4">
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      :class="getExpirationBarColor(invoice.date)"
                      :style="{ width: getExpirationPercentage(invoice.date) + '%' }"
                      class="h-full transition-all duration-500 rounded-full"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Right Section - Actions -->
              <div class="flex flex-col gap-2 lg:min-w-[200px]">
                <div class="flex gap-2">
                  <button
                    @click="toggleDone(invoice)"
                    :disabled="togglingId === invoice.id"
                    :class="{
                      'bg-green-600 hover:bg-green-700': !invoice.is_done,
                      'bg-gray-400 hover:bg-gray-500': invoice.is_done,
                    }"
                    class="flex-1 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg v-if="togglingId === invoice.id" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <svg v-else-if="invoice.is_done" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    {{ invoice.is_done ? 'Undo' : 'Done' }}
                  </button>
                  
                  <button
                    @click="confirmDelete(invoice)"
                    :disabled="deletingId === invoice.id"
                    class="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg v-if="deletingId === invoice.id" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete
                  </button>
                </div>
                <NuxtLink
                  :to="`/invoices/${invoice.id}/edit`"
                  class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit Invoice
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const api = useApi()
const invoices = ref([])
const loading = ref(true)
const error = ref('')
const togglingId = ref(null)
const deletingId = ref(null)
const viewMode = ref('grid') // 'grid' or 'list'
const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  authStore.logout()
  await router.push('/login')
}

const fetchInvoices = async () => {
  try {
    loading.value = true
    error.value = ''
    const config = useRuntimeConfig()
    const authStore = useAuthStore()
    
    invoices.value = await $fetch(`${config.public.apiBase}/invoices/`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
  } catch (err) {
    error.value = 'Failed to load invoices. Please try again.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const getExpirationDate = (invoiceDate) => {
  const date = new Date(invoiceDate)
  date.setDate(date.getDate() + 5)
  return date
}

const getDaysUntilExpiration = (invoiceDate) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const expiration = getExpirationDate(invoiceDate)
  expiration.setHours(0, 0, 0, 0)
  const diffTime = expiration - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

const getExpirationStatus = (invoiceDate) => {
  const days = getDaysUntilExpiration(invoiceDate)
  if (days >= 3) {
    return `${days} days remaining`
  } else if (days >= 1) {
    return `${days} day(s) remaining - Expiring soon`
  } else if (days === 0) {
    return 'Expires today'
  } else {
    return `Expired ${Math.abs(days)} day(s) ago`
  }
}

const getExpirationColor = (invoiceDate) => {
  const days = getDaysUntilExpiration(invoiceDate)
  if (days >= 3) {
    return 'text-green-600 font-medium'
  } else if (days >= 1) {
    return 'text-orange-600 font-medium'
  } else {
    return 'text-red-600 font-medium'
  }
}

const getExpirationBarColor = (invoiceDate) => {
  const days = getDaysUntilExpiration(invoiceDate)
  if (days >= 3) {
    return 'bg-green-500'
  } else if (days >= 1) {
    return 'bg-orange-500'
  } else {
    return 'bg-red-500'
  }
}

const getExpirationPercentage = (invoiceDate) => {
  const days = getDaysUntilExpiration(invoiceDate)
  // 5 days total, calculate percentage
  if (days >= 5) return 100
  if (days >= 0) return Math.max(0, (days / 5) * 100)
  return 0
}

// Computed properties for statistics
const totalAmount = computed(() => {
  return invoices.value.reduce((sum, invoice) => sum + parseFloat(invoice.amount || 0), 0)
})

const paidCount = computed(() => {
  return invoices.value.filter(invoice => invoice.status === 'Paid').length
})

const unpaidCount = computed(() => {
  return invoices.value.filter(invoice => invoice.status === 'Unpaid').length
})

const toggleDone = async (invoice) => {
  try {
    togglingId.value = invoice.id
    const config = useRuntimeConfig()
    const authStore = useAuthStore()
    
    const updatedInvoice = await $fetch(`${config.public.apiBase}/invoices/${invoice.id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${authStore.token}`
      },
      body: {
        ...invoice,
        is_done: !invoice.is_done,
        amount: parseFloat(invoice.amount)
      }
    })
    
    // Update the invoice in the list
    const index = invoices.value.findIndex(inv => inv.id === invoice.id)
    if (index !== -1) {
      invoices.value[index] = updatedInvoice
    }
  } catch (err) {
    error.value = 'Failed to update invoice status. Please try again.'
    console.error(err)
  } finally {
    togglingId.value = null
  }
}

const confirmDelete = (invoice) => {
  if (confirm(`Are you sure you want to delete invoice ${invoice.invoice_no}? This action cannot be undone.`)) {
    deleteInvoice(invoice)
  }
}

const deleteInvoice = async (invoice) => {
  try {
    deletingId.value = invoice.id
    const config = useRuntimeConfig()
    const authStore = useAuthStore()
    
    await $fetch(`${config.public.apiBase}/invoices/${invoice.id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    // Remove the invoice from the list
    invoices.value = invoices.value.filter(inv => inv.id !== invoice.id)
  } catch (err) {
    error.value = 'Failed to delete invoice. Please try again.'
    console.error(err)
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  fetchInvoices()
})
</script>

