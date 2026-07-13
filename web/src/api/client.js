import axios from 'axios'

const client = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
})

client.interceptors.request.use((config)=>{
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
}, (err) => Promise.reject(err))

client.interceptors.response.use(
    (res) => {
        console.log('[API]', res.config.method?.toUpperCase(), res.config.url, res.data)
        return res.data
    },
    (err) => {
        console.log('[API ERR]', err.config?.url, err.response?.status, err.response?.data)
        if (err.response?.status === 401) {
            localStorage.removeItem('token')
            window.location.href = '/login'
        }
        return Promise.reject(err)
    }
)

export default client