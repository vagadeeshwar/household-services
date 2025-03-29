<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Payment Gateway</h1>
        <p class="text-muted">Complete your service request payment</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="row g-4">
      <!-- Payment Form -->
      <div class="col-lg-8">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <!-- Payment Method Selection -->
            <div class="mb-4">
              <h5 class="mb-3">Select Payment Method</h5>
              <div class="row g-3">
                <div class="col-md-3">
                  <div
                    class="payment-method-card"
                    :class="{ selected: paymentMethod === 'credit' }"
                    @click="paymentMethod = 'credit'"
                  >
                    <div class="payment-method-icon">
                      <i class="bi bi-credit-card"></i>
                    </div>
                    <div class="payment-method-name">Credit Card</div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div
                    class="payment-method-card"
                    :class="{ selected: paymentMethod === 'debit' }"
                    @click="paymentMethod = 'debit'"
                  >
                    <div class="payment-method-icon">
                      <i class="bi bi-credit-card-2-front"></i>
                    </div>
                    <div class="payment-method-name">Debit Card</div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div
                    class="payment-method-card"
                    :class="{ selected: paymentMethod === 'upi' }"
                    @click="paymentMethod = 'upi'"
                  >
                    <div class="payment-method-icon">
                      <i class="bi bi-phone"></i>
                    </div>
                    <div class="payment-method-name">UPI</div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div
                    class="payment-method-card"
                    :class="{ selected: paymentMethod === 'wallet' }"
                    @click="paymentMethod = 'wallet'"
                  >
                    <div class="payment-method-icon">
                      <i class="bi bi-wallet2"></i>
                    </div>
                    <div class="payment-method-name">e-Wallet</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Card Information (for credit/debit card) -->
            <div v-if="paymentMethod === 'credit' || paymentMethod === 'debit'">
              <h5 class="mb-3">Card Information</h5>
              <form @submit.prevent="processPayment">
                <!-- Card Number -->
                <div class="mb-3">
                  <label for="cardNumber" class="form-label">
                    Card Number <span class="text-danger">*</span>
                  </label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-credit-card"></i>
                    </span>
                    <input
                      type="text"
                      id="cardNumber"
                      class="form-control"
                      v-model="formData.cardNumber"
                      placeholder="4111 1111 1111 1111"
                      :class="{ 'is-invalid': v$.cardNumber.$errors.length }"
                      @input="formatCardNumber"
                      @blur="v$.cardNumber.$touch()"
                      maxlength="19"
                    />
                    <div class="invalid-feedback">
                      {{ v$.cardNumber.$errors[0]?.$message }}
                    </div>
                  </div>
                  <div class="mt-1 text-end">
                    <i class="bi bi-credit-card text-primary mx-1"></i>
                    <i class="bi bi-credit-card text-danger mx-1"></i>
                    <i class="bi bi-credit-card text-warning mx-1"></i>
                    <i class="bi bi-credit-card text-success mx-1"></i>
                  </div>
                </div>

                <!-- Card Details Row -->
                <div class="row g-3 mb-3">
                  <!-- Expiry Date -->
                  <div class="col-md-6">
                    <label for="expiryDate" class="form-label">
                      Expiry Date <span class="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      id="expiryDate"
                      class="form-control"
                      v-model="formData.expiryDate"
                      placeholder="MM/YY"
                      :class="{ 'is-invalid': v$.expiryDate.$errors.length }"
                      @input="formatExpiryDate"
                      @blur="v$.expiryDate.$touch()"
                      maxlength="5"
                    />
                    <div class="invalid-feedback">
                      {{ v$.expiryDate.$errors[0]?.$message }}
                    </div>
                  </div>
                  <!-- CVV -->
                  <div class="col-md-6">
                    <label for="cvv" class="form-label">
                      CVV <span class="text-danger">*</span>
                    </label>
                    <div class="input-group">
                      <input
                        type="text"
                        id="cvv"
                        class="form-control"
                        v-model="formData.cvv"
                        placeholder="123"
                        :class="{ 'is-invalid': v$.cvv.$errors.length }"
                        @blur="v$.cvv.$touch()"
                        maxlength="3"
                      />
                      <span class="input-group-text bg-light">
                        <i
                          class="bi bi-question-circle"
                          data-bs-toggle="tooltip"
                          title="3-digit security code on the back of your card"
                        ></i>
                      </span>
                      <div class="invalid-feedback">
                        {{ v$.cvv.$errors[0]?.$message }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Cardholder Name -->
                <div class="mb-4">
                  <label for="cardholderName" class="form-label">
                    Cardholder Name <span class="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    id="cardholderName"
                    class="form-control"
                    v-model="formData.name"
                    placeholder="John Smith"
                    :class="{ 'is-invalid': v$.name.$errors.length }"
                    @blur="v$.name.$touch()"
                  />
                  <div class="invalid-feedback">
                    {{ v$.name.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Billing Address (toggled by checkbox) -->
                <div class="mb-3 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="showBillingAddress"
                    v-model="showBillingAddress"
                  />
                  <label class="form-check-label" for="showBillingAddress"
                    >Add billing address</label
                  >
                </div>

                <div v-if="showBillingAddress" class="billing-address-section mb-4">
                  <h6 class="mb-3">Billing Address</h6>
                  <div class="mb-3">
                    <label for="addressLine1" class="form-label">Address Line 1</label>
                    <input
                      type="text"
                      class="form-control"
                      id="addressLine1"
                      v-model="formData.addressLine1"
                    />
                  </div>
                  <div class="mb-3">
                    <label for="addressLine2" class="form-label">Address Line 2 (Optional)</label>
                    <input
                      type="text"
                      class="form-control"
                      id="addressLine2"
                      v-model="formData.addressLine2"
                    />
                  </div>
                  <div class="row g-3">
                    <div class="col-md-6 mb-3">
                      <label for="city" class="form-label">City</label>
                      <input type="text" class="form-control" id="city" v-model="formData.city" />
                    </div>
                    <div class="col-md-6 mb-3">
                      <label for="zipCode" class="form-label">ZIP / Postal Code</label>
                      <input
                        type="text"
                        class="form-control"
                        id="zipCode"
                        v-model="formData.zipCode"
                      />
                    </div>
                  </div>
                </div>

                <!-- Save Card Toggle -->
                <div class="mb-4 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="saveCard"
                    v-model="formData.saveCard"
                  />
                  <label class="form-check-label" for="saveCard"
                    >Save card for future payments</label
                  >
                </div>

                <!-- Action Buttons -->
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="isProcessing">
                    <i v-if="isProcessing" class="bi bi-hourglass-split me-2"></i>
                    <i v-else class="bi bi-lock-fill me-2"></i>
                    {{ isProcessing ? 'Processing Payment...' : 'Pay Now ₹' + amount.toFixed(2) }}
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="cancelPayment">
                    <i class="bi bi-x-circle me-2"></i>Cancel
                  </button>
                </div>
              </form>
            </div>

            <!-- UPI Section -->
            <div v-else-if="paymentMethod === 'upi'">
              <h5 class="mb-3">UPI Payment</h5>
              <form @submit.prevent="processPayment">
                <div class="mb-4">
                  <label for="upiId" class="form-label"
                    >UPI ID <span class="text-danger">*</span></label
                  >
                  <div class="input-group">
                    <input
                      type="text"
                      id="upiId"
                      class="form-control"
                      v-model="formData.upiId"
                      placeholder="name@upi"
                      :class="{ 'is-invalid': v$.upiId.$errors.length }"
                      @blur="v$.upiId.$touch()"
                    />
                    <span class="input-group-text bg-light">
                      <i class="bi bi-phone"></i>
                    </span>
                    <div class="invalid-feedback">
                      {{ v$.upiId.$errors[0]?.$message }}
                    </div>
                  </div>
                  <small class="form-text text-muted">Enter your UPI ID (e.g., name@okicici)</small>
                </div>

                <!-- UPI Payment Providers -->
                <div class="mb-4">
                  <label class="form-label d-block">Select UPI App</label>
                  <div class="upi-providers">
                    <div
                      v-for="provider in upiProviders"
                      :key="provider.id"
                      class="upi-provider"
                      :class="{ selected: selectedUpiProvider === provider.id }"
                      @click="selectedUpiProvider = provider.id"
                    >
                      <i :class="provider.icon"></i>
                      <span>{{ provider.name }}</span>
                    </div>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="isProcessing">
                    <i v-if="isProcessing" class="bi bi-hourglass-split me-2"></i>
                    <i v-else class="bi bi-phone me-2"></i>
                    {{ isProcessing ? 'Processing...' : 'Pay with UPI ₹' + amount.toFixed(2) }}
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="cancelPayment">
                    <i class="bi bi-x-circle me-2"></i>Cancel
                  </button>
                </div>
              </form>
            </div>

            <!-- E-Wallet Section -->
            <div v-else-if="paymentMethod === 'wallet'">
              <h5 class="mb-3">e-Wallet Payment</h5>
              <form @submit.prevent="processPayment">
                <!-- Wallet Selection -->
                <div class="mb-4">
                  <label class="form-label d-block">Select Wallet</label>
                  <div class="wallet-providers">
                    <div
                      v-for="wallet in walletProviders"
                      :key="wallet.id"
                      class="wallet-provider"
                      :class="{ selected: selectedWallet === wallet.id }"
                      @click="selectedWallet = wallet.id"
                    >
                      <i :class="wallet.icon"></i>
                      <span>{{ wallet.name }}</span>
                    </div>
                  </div>
                </div>

                <div class="mb-4">
                  <label for="walletMobile" class="form-label">
                    Mobile Number <span class="text-danger">*</span>
                  </label>
                  <div class="input-group">
                    <span class="input-group-text">+91</span>
                    <input
                      type="text"
                      id="walletMobile"
                      class="form-control"
                      v-model="formData.mobile"
                      placeholder="9876543210"
                      :class="{ 'is-invalid': v$.mobile.$errors.length }"
                      @blur="v$.mobile.$touch()"
                      maxlength="10"
                    />
                    <div class="invalid-feedback">
                      {{ v$.mobile.$errors[0]?.$message }}
                    </div>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="isProcessing">
                    <i v-if="isProcessing" class="bi bi-hourglass-split me-2"></i>
                    <i v-else class="bi bi-wallet2 me-2"></i>
                    {{ isProcessing ? 'Processing...' : 'Pay with e-Wallet ₹' + amount.toFixed(2) }}
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="cancelPayment">
                    <i class="bi bi-x-circle me-2"></i>Cancel
                  </button>
                </div>
              </form>
            </div>

            <!-- Security Info -->
            <div class="text-center mt-4">
              <div class="d-flex justify-content-center align-items-center gap-3 mb-2">
                <i class="bi bi-shield-lock text-success fs-4"></i>
                <i class="bi bi-patch-check text-primary fs-4"></i>
                <i class="bi bi-shield-check text-info fs-4"></i>
              </div>
              <p class="text-muted small mb-0">
                Your payment information is secure. We use industry-standard encryption to protect
                your data.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="col-lg-4">
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-light">
            <h5 class="card-title mb-0">Order Summary</h5>
          </div>
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="service-icon me-3">
                <i class="bi bi-tools"></i>
              </div>
              <div>
                <h6 class="mb-0">{{ service.name }}</h6>
                <p class="text-muted small mb-0">Service ID: #{{ service.id }}</p>
              </div>
            </div>

            <hr />

            <ul class="list-group list-group-flush mb-3">
              <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>Base Price</span>
                <span>₹{{ service.base_price.toFixed(2) }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>Convenience Fee</span>
                <span>₹{{ convenienceFee.toFixed(2) }}</span>
              </li>
              <li
                v-if="discount > 0"
                class="list-group-item d-flex justify-content-between align-items-center px-0 text-success"
              >
                <span>
                  <i class="bi bi-tag-fill me-1"></i>
                  Discount
                </span>
                <span>-₹{{ discount.toFixed(2) }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>Taxes (18% GST)</span>
                <span>₹{{ taxes.toFixed(2) }}</span>
              </li>
            </ul>

            <div class="d-flex justify-content-between align-items-center fw-bold fs-5 mb-3">
              <span>Total</span>
              <span>₹{{ amount.toFixed(2) }}</span>
            </div>

            <!-- Apply Coupon -->
            <div class="coupon-section mb-3">
              <div class="input-group">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Enter coupon code"
                  v-model="couponCode"
                />
                <button
                  class="btn btn-outline-primary"
                  type="button"
                  @click="applyCoupon"
                  :disabled="couponCode.trim() === ''"
                >
                  Apply
                </button>
              </div>
              <div v-if="couponMessage" class="mt-2" :class="couponMessageClass">
                <small>{{ couponMessage }}</small>
              </div>
            </div>

            <!-- Service Details -->
            <hr />
            <h6 class="mb-2">Service Details</h6>
            <p class="text-muted small">{{ service.description }}</p>
            <div class="d-flex align-items-center mb-2">
              <i class="bi bi-calendar text-muted me-2"></i>
              <span class="small">{{ formatScheduledTime }}</span>
            </div>
            <div class="d-flex align-items-center">
              <i class="bi bi-geo-alt text-muted me-2"></i>
              <span class="small">{{ service.location }}</span>
            </div>
          </div>
        </div>

        <!-- Payment Support -->
        <div class="card shadow-sm">
          <div class="card-body">
            <h6>Need Help?</h6>
            <p class="text-muted small">
              If you have any questions about your payment, contact our support team.
            </p>
            <div class="d-flex align-items-center mb-2">
              <i class="bi bi-envelope text-muted me-2"></i>
              <span class="small">support@householdservices.com</span>
            </div>
            <div class="d-flex align-items-center">
              <i class="bi bi-telephone text-muted me-2"></i>
              <span class="small">+91 9876543210</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Success Modal -->
    <div class="modal fade" id="paymentSuccessModal" tabindex="-1" ref="successModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-body text-center p-5">
            <div class="mb-4">
              <div class="success-icon">
                <i class="bi bi-check-lg"></i>
              </div>
            </div>
            <h4 class="mb-3">
              {{ isCompletedRequest ? 'Service Payment Completed!' : 'Payment Successful!' }}
            </h4>
            <p>
              Your payment of <strong>₹{{ amount.toFixed(2) }}</strong> for
              {{ isCompletedRequest ? 'the completed service' : 'your service request' }}
              has been processed successfully.
            </p>
            <p class="text-muted mb-4">A confirmation has been sent to your email address.</p>
            <div class="receipt-details bg-light p-3 rounded mb-4 text-start">
              <div class="mb-2 d-flex justify-content-between">
                <span>Payment ID:</span>
                <span>PAY{{ Math.floor(Math.random() * 10000000) }}</span>
              </div>
              <div class="mb-2 d-flex justify-content-between">
                <span>Date:</span>
                <span>{{ new Date().toLocaleDateString() }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span>Status:</span>
                <span class="text-success">Completed</span>
              </div>
            </div>
            <div class="d-grid gap-2">
              <button type="button" class="btn btn-primary" @click="redirectToRequestsPage">
                <i class="bi bi-list-check me-2"></i>View My Requests
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as bootstrap from 'bootstrap'
import useVuelidate from '@vuelidate/core'
import { required, minLength, helpers } from '@vuelidate/validators'

export default {
  name: 'PaymentView',
  setup() {
    const router = useRouter()
    const successModal = ref(null)
    let bsSuccessModal = null

    // Payment method state
    const paymentMethod = ref('credit')
    const showBillingAddress = ref(false)
    const isProcessing = ref(false)

    // UPI and E-Wallet providers
    const selectedUpiProvider = ref('gpay')
    const selectedWallet = ref('paytm')

    const upiProviders = [
      { id: 'gpay', name: 'Google Pay', icon: 'bi bi-google' },
      { id: 'phonepe', name: 'PhonePe', icon: 'bi bi-phone' },
      { id: 'paytm', name: 'Paytm', icon: 'bi bi-wallet2' },
      { id: 'bhim', name: 'BHIM', icon: 'bi bi-bank' },
    ]

    const walletProviders = [
      { id: 'paytm', name: 'Paytm', icon: 'bi bi-wallet2' },
      { id: 'phonepe', name: 'PhonePe', icon: 'bi bi-phone' },
      { id: 'amazonpay', name: 'Amazon Pay', icon: 'bi bi-amazon' },
      { id: 'mobikwik', name: 'MobiKwik', icon: 'bi bi-wallet' },
    ]

    // Form data
    const formData = reactive({
      cardNumber: '',
      expiryDate: '',
      cvv: '',
      name: '',
      addressLine1: '',
      addressLine2: '',
      city: '',
      zipCode: '',
      saveCard: false,
      upiId: '',
      mobile: '',
    })

    const route = useRoute()

    const requestId = route.query.request_id
    const isCompletedRequest = !!requestId

    const service = ref({
      id: route.query.request_id ? parseInt(route.query.request_id) : 12345,
      name: route.query.service_name || 'Premium AC Servicing',
      description: isCompletedRequest
        ? `Payment for completed service by ${route.query.professional_name || 'professional'}`
        : 'Complete air conditioner servicing including cleaning, gas refill, and performance check.',
      base_price: parseFloat(route.query.service_price || '1499.0'),
      location: '123 Main Street, Mumbai, 400001',
      scheduled_time:
        isCompletedRequest && route.query.date_completed
          ? new Date(route.query.date_completed)
          : new Date(new Date().getTime() + 2 * 24 * 60 * 60 * 1000),
    })

    // Custom validators
    const cardNumberValidator = helpers.withMessage(
      'Please enter a valid 16-digit card number',
      (value) => {
        const digits = value.replace(/\s/g, '')
        return /^\d{16}$/.test(digits)
      },
    )

    const expiryValidator = helpers.withMessage(
      'Please enter a valid expiry date (MM/YY)',
      (value) => {
        if (!value) return false
        const [month, year] = value.split('/')
        if (!month || !year) return false

        const numMonth = parseInt(month, 10)
        const numYear = parseInt(year, 10)
        const currentYear = new Date().getFullYear() % 100
        const currentMonth = new Date().getMonth() + 1

        if (numMonth < 1 || numMonth > 12) return false
        if (numYear < currentYear) return false
        if (numYear === currentYear && numMonth < currentMonth) return false

        return true
      },
    )

    const cvvValidator = helpers.withMessage('CVV must be 3 digits', (value) =>
      /^\d{3}$/.test(value),
    )

    const mobileValidator = helpers.withMessage(
      'Please enter a valid 10-digit mobile number',
      (value) => /^[6-9]\d{9}$/.test(value),
    )

    const upiValidator = helpers.withMessage(
      'Please enter a valid UPI ID (e.g., name@upi)',
      (value) => /^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$/.test(value),
    )

    // Validation rules
    const rules = computed(() => {
      // Common rules
      const baseRules = {}

      // Payment method specific rules
      if (paymentMethod.value === 'credit' || paymentMethod.value === 'debit') {
        return {
          ...baseRules,
          cardNumber: {
            required: helpers.withMessage('Card number is required', required),
            cardNumberValidator,
          },
          expiryDate: {
            required: helpers.withMessage('Expiry date is required', required),
            expiryValidator,
          },
          cvv: {
            required: helpers.withMessage('CVV is required', required),
            cvvValidator,
          },
          name: {
            required: helpers.withMessage('Cardholder name is required', required),
            minLength: helpers.withMessage('Name must be at least 3 characters', minLength(3)),
          },
        }
      } else if (paymentMethod.value === 'upi') {
        return {
          ...baseRules,
          upiId: {
            required: helpers.withMessage('UPI ID is required', required),
            upiValidator,
          },
        }
      } else if (paymentMethod.value === 'wallet') {
        return {
          ...baseRules,
          mobile: {
            required: helpers.withMessage('Mobile number is required', required),
            mobileValidator,
          },
        }
      }

      return baseRules
    })

    // Initialize Vuelidate
    const v$ = useVuelidate(rules, formData)

    // Coupon state
    const couponCode = ref('')
    const couponMessage = ref('')
    const couponMessageClass = ref('')
    const discount = ref(0)

    // Computed values
    const taxes = computed(() => service.value.base_price * 0.18)
    const convenienceFee = computed(() => 49.0)
    const amount = computed(
      () => service.value.base_price + taxes.value + convenienceFee.value - discount.value,
    )

    const formatScheduledTime = computed(() => {
      const date = service.value.scheduled_time
      return `${date.toLocaleDateString()} at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    })

    // Methods for card formatting
    const formatCardNumber = () => {
      let value = formData.value.cardNumber.replace(/\D/g, '')
      let formattedValue = ''

      for (let i = 0; i < value.length; i++) {
        if (i > 0 && i % 4 === 0) {
          formattedValue += ' '
        }
        formattedValue += value[i]
      }

      formData.value.cardNumber = formattedValue
    }

    const formatExpiryDate = () => {
      let value = formData.value.expiryDate.replace(/\D/g, '')

      if (value.length > 2) {
        formData.value.expiryDate = value.substring(0, 2) + '/' + value.substring(2)
      } else {
        formData.value.expiryDate = value
      }
    }

    // Watch for payment method changes to reset validation
    watch(paymentMethod, () => {
      // Reset validation when payment method changes
      v$.value.$reset()
    })

    // Apply coupon method
    const applyCoupon = () => {
      // Simulate coupon validation
      if (couponCode.value.toUpperCase() === 'WELCOME10') {
        discount.value = service.value.base_price * 0.1 // 10% discount
        couponMessage.value = 'Coupon applied successfully! You saved ₹' + discount.value.toFixed(2)
        couponMessageClass.value = 'text-success'
      } else if (couponCode.value.toUpperCase() === 'SAVE100') {
        discount.value = 100 // Flat ₹100 off
        couponMessage.value = 'Coupon applied successfully! You saved ₹100'
        couponMessageClass.value = 'text-success'
      } else {
        discount.value = 0
        couponMessage.value = 'Invalid coupon code'
        couponMessageClass.value = 'text-danger'
      }
    }
    const processPayment = async () => {
      // Validate all fields
      const isFormValid = await v$.value.$validate()
      if (!isFormValid) {
        // Show toast notification for validation errors
        window.showToast({
          type: 'warning',
          title: 'Some required information is missing or incorrect',
        })
        return
      }
      isProcessing.value = true
      try {
        // Simulate payment processing delay
        await new Promise((resolve) => setTimeout(resolve, 2000))

        // Different success message based on flow
        window.showToast({
          type: 'success',
          title: isCompletedRequest
            ? `Payment of ₹${amount.value.toFixed(2)} for your completed service has been processed`
            : `Payment of ₹${amount.value.toFixed(2)} has been processed`,
        })

        router.push('/customer/requests')
        // Show success modal
        bsSuccessModal.show()
      } catch (error) {
        // Handle payment errors
        window.showToast({
          type: 'danger',
          title: error.message || 'An error occurred during payment processing',
        })
      } finally {
        isProcessing.value = false
      }
    }

    // Cancel payment
    const cancelPayment = () => {
      // Confirm cancellation
      if (
        confirm(
          'Are you sure you want to cancel this payment? Your service request will not be processed.',
        )
      ) {
        router.push('/customer/requests')
      }
    }

    // Redirect after payment
    const redirectToRequestsPage = () => {
      bsSuccessModal.hide()
      router.push('/customer/requests')
    }

    // Initialize tooltips and modals
    onMounted(() => {
      // Initialize tooltips
      const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]'),
      )
      tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
      })

      // Initialize success modal
      if (successModal.value) {
        bsSuccessModal = new bootstrap.Modal(successModal.value)
      }
    })

    return {
      paymentMethod,
      showBillingAddress,
      formData,
      isProcessing,
      service,
      taxes,
      convenienceFee,
      amount,
      formatScheduledTime,
      upiProviders,
      walletProviders,
      selectedUpiProvider,
      selectedWallet,
      couponCode,
      couponMessage,
      couponMessageClass,
      discount,
      successModal,
      formatCardNumber,
      formatExpiryDate,
      processPayment,
      cancelPayment,
      applyCoupon,
      redirectToRequestsPage,
      v$,
    }
  },
}
</script>

<style scoped>
/* Payment method selection */
.payment-method-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.payment-method-card:hover {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.payment-method-card.selected {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  box-shadow: 0 0 0 3px rgba(var(--bs-primary-rgb), 0.25);
}

.payment-method-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--bs-primary);
}

.payment-method-name {
  font-size: 0.875rem;
  font-weight: 500;
}

/* UPI and Wallet providers */
.upi-providers,
.wallet-providers {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.upi-provider,
.wallet-provider {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upi-provider:hover,
.wallet-provider:hover {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.upi-provider.selected,
.wallet-provider.selected {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  box-shadow: 0 0 0 2px rgba(var(--bs-primary-rgb), 0.25);
}

.upi-provider i,
.wallet-provider i {
  font-size: 1.25rem;
  color: var(--bs-primary);
}

/* Service icon */
.service-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--bs-primary);
}

/* Form styling */
.form-label {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

/* Success modal styling */
.success-icon {
  width: 80px;
  height: 80px;
  background-color: #d1e7dd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.success-icon i {
  font-size: 2.5rem;
  color: #198754;
}

.receipt-details {
  font-size: 0.9rem;
}

/* Card hover effect */
.card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1) !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .payment-method-card {
    padding: 0.75rem 0.5rem;
  }

  .payment-method-icon {
    font-size: 1.25rem;
  }

  .payment-method-name {
    font-size: 0.75rem;
  }

  .upi-providers,
  .wallet-providers {
    gap: 0.5rem;
  }

  .upi-provider,
  .wallet-provider {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
  }
}
</style>
