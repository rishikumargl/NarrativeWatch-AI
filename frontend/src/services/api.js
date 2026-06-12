import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
})

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    // Add request preprocessing if needed
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // Handle errors globally
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    console.error('API Error:', message)
    return Promise.reject({
      status: error.response?.status,
      message: message,
      error: error.response?.data?.error,
    })
  }
)

// API methods
export const analyzeInstagram = async (url, options = {}) => {
  return apiClient.post('/v1/analyze', {
    instagram_url: url,
    analysis_type: options.analysisType || 'page',
    include_historical: options.includeHistorical !== false,
    include_bot_analysis: options.includeBotAnalysis !== false,
    include_bias_detection: options.includeBiasDetection !== false,
    include_campaign_detection: options.includeCampaignDetection !== false,
  })
}

export const getAnalysisResult = async (requestId) => {
  return apiClient.get(`/v1/results/${requestId}`)
}

export const healthCheck = async () => {
  return apiClient.get('/health')
}

export default apiClient
