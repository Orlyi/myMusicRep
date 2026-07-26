import axios from 'axios'

// 前端内存缓存（key → { data, time }）
const cache = new Map()
const CACHE_TTL = 300_000 // 5 分钟

function cacheKey(config) {
    return `${config.method}:${config.url}:${JSON.stringify(config.params || {})}`
}

const client = axios.create({
    baseURL: 'http://serverIP:8000/api/v1',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
})

const requestQueue = new Map() // 请求去重，同 url+params 只发一个

client.interceptors.request.use((config) => {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`

    // GET 命中缓存 → 跳过
    if (config.method === 'get') {
        const key = cacheKey(config)
        const hit = cache.get(key)
        if (hit && Date.now() - hit.time < CACHE_TTL) {
            // 用 cancelToken 取消请求，直接 resolve
            const source = axios.CancelToken.source()
            config.cancelToken = source.token
            source.cancel(JSON.stringify(hit.data))
        }
    }
    return config
}, (err) => Promise.reject(err))

client.interceptors.response.use(
    (res) => {
        // GET 成功 → 写缓存
        if (res.config.method === 'get' && res.data?.code === 0) {
            cache.set(cacheKey(res.config), { data: res.data, time: Date.now() })
        }
        // POST/PUT/DELETE → 删模块缓存
        const m = res.config.method?.toLowerCase()
        if (m && !['get'].includes(m)) {
            const module = (res.config.url || '').split('/')[0] || ''
            for (const key of cache.keys()) {
                if (key.includes(`:${module}/`) || key.includes(`/${module}`) || key.endsWith(`:${module}`)) {
                    cache.delete(key)
                }
            }
        }
        return res.data
    },
    (err) => {
        if (err.response?.status === 401) {
            localStorage.removeItem('token')
            sessionStorage.removeItem('token')
            window.location.href = '/login'
        }
        // 缓存命中导致请求被取消 → 返回缓存数据
        if (axios.isCancel(err)) {
            try {
                return Promise.resolve(JSON.parse(err.message))
            } catch {
                return Promise.reject(err)
            }
        }
        return Promise.reject(err)
    }
)

export default client
