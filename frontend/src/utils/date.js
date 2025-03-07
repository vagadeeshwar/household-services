import moment from 'moment'

/**
 * Format a UTC date string to relative time (e.g., "5 minutes ago")
 * @param {string} dateString - UTC date string from the API
 * @returns {string} Formatted relative time
 */
export const formatRelativeTime = (dateString) => {
  return dateString ? moment.utc(dateString).local().fromNow() : 'N/A'
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
