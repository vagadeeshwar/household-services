import { helpers } from '@vuelidate/validators'

export const profileValidationRules = {
    email: {
        required: helpers.withMessage('Email is required', v => !!v),
        email: helpers.withMessage('Please enter a valid email address', v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))
    },
    full_name: {
        required: helpers.withMessage('Full name is required', v => !!v),
        minLength: helpers.withMessage('Full name must be at least 3 characters', v => v.length >= 3),
        validName: helpers.withMessage(
            'Name can only contain letters, spaces, and hyphens',
            v => /^[a-zA-Z\s-]+$/.test(v)
        )
    },
    phone: {
        required: helpers.withMessage('Phone number is required', v => !!v),
        validPhone: helpers.withMessage(
            'Please enter a valid 10-digit phone number',
            v => /^[1-9]\d{9}$/.test(v)
        )
    },
    pin_code: {
        required: helpers.withMessage('PIN code is required', v => !!v),
        validPin: helpers.withMessage(
            'Please enter a valid 6-digit PIN code',
            v => /^[1-9]\d{5}$/.test(v)
        )
    },
    address: {
        required: helpers.withMessage('Address is required', v => !!v),
        minLength: helpers.withMessage('Address must be at least 10 characters', v => v.length >= 10),
        maxLength: helpers.withMessage('Address cannot exceed 200 characters', v => v.length <= 200)
    },
    description: {
        required: helpers.withMessage('Professional description is required', v => !!v),
        minLength: helpers.withMessage('Description must be at least 50 characters', v => v.length >= 50),
        maxLength: helpers.withMessage('Description cannot exceed 1000 characters', v => v.length <= 1000)
    },
    service_type_id: {
        required: helpers.withMessage('Please select a service type', v => !!v)
    },
    experience_years: {
        required: helpers.withMessage('Years of experience is required', v => !!v),
        numeric: helpers.withMessage('Please enter a valid number', v => !isNaN(v)),
        min: helpers.withMessage('Experience must be at least 0 years', v => v >= 0),
        max: helpers.withMessage('Experience cannot exceed 50 years', v => v <= 50)
    }
}

export const passwordValidationRules = {
    old_password: {
        required: helpers.withMessage('Current password is required', v => !!v)
    },
    new_password: {
        required: helpers.withMessage('New password is required', v => !!v),
        minLength: helpers.withMessage('Password must be at least 8 characters', v => v.length >= 8),
        containsUppercase: helpers.withMessage(
            'Password must contain at least one uppercase letter',
            v => /[A-Z]/.test(v)
        ),
        containsLowercase: helpers.withMessage(
            'Password must contain at least one lowercase letter',
            v => /[a-z]/.test(v)
        ),
        containsNumber: helpers.withMessage(
            'Password must contain at least one number',
            v => /\d/.test(v)
        ),
        containsSpecial: helpers.withMessage(
            'Password must contain at least one special character',
            v => /[!@#$%^&*(),.?":{}|<>]/.test(v)
        )
    },
    confirm_password: {
        required: helpers.withMessage('Please confirm your password', v => !!v),
        sameAsPassword: helpers.withMessage(
            'Passwords must match',
            (v, form) => v === form.new_password
        )
    }
}

export const documentValidationRules = {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['application/pdf', 'image/jpeg', 'image/png'],
    validateFile: (file) => {
        if (!file) return { valid: false, error: 'Please select a file' }
        if (!documentValidationRules.allowedTypes.includes(file.type)) {
            return { valid: false, error: 'File must be PDF, JPG, or PNG' }
        }
        if (file.size > documentValidationRules.maxSize) {
            return { valid: false, error: 'File size must not exceed 5MB' }
        }
        return { valid: true }
    }
}