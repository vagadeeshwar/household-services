import moment from 'moment'

/**
 * Format a UTC date string to relative time (e.g., "5 minutes ago")
 * @param {string} dateString - UTC date string from the API
 * @returns {string} Formatted relative time
 */
export const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A'
  // Ensure we're treating the input date as UTC and converting to local time
  return moment.utc(dateString).local().fromNow()
}

/**
 * Format a UTC date string to a standard date format
 * @param {string} dateString - UTC date string from the API
 * @param {string} format - Optional moment format string (default: 'MMM DD, YYYY hh:mm A')
 * @returns {string} Formatted date string
 */
export const formatDateTime = (dateString, format = 'MMM DD, YYYY hh:mm A') => {
  return dateString ? moment.utc(dateString).local().format(format) : 'N/A'
}

/**
 * Format a UTC date string to date only (no time)
 * @param {string} dateString - UTC date string from the API
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString) => {
  return dateString ? moment.utc(dateString).local().format('MMM DD, YYYY') : 'N/A'
}

/**
 * Format a UTC date string to time only (no date)
 * @param {string} dateString - UTC date string from the API
 * @returns {string} Formatted time string
 */
export const formatTime = (dateString) => {
  return dateString ? moment.utc(dateString).local().format('hh:mm A') : 'N/A'
}

/**
 * For client-side timestamps (not from the backend)
 * @param {Date|string} date - Local date object or string
 * @param {string} format - Optional moment format string
 * @returns {string} Formatted date string
 */
export const formatLocalDateTime = (date, format = 'MMM DD, YYYY hh:mm A') => {
  return date ? moment(date).format(format) : 'N/A'
}

/**
 * Format minutes to a human-readable duration
 * @param {number} minutes - Total minutes
 * @returns {string} Formatted duration string
 */
export const formatDuration = (minutes) => {
  if (!minutes) return 'N/A'

  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60

  if (hours > 0 && mins > 0) {
    return `${hours}h ${mins}m`
  } else if (hours > 0) {
    return `${hours}h`
  } else {
    return `${mins}m`
  }
}
