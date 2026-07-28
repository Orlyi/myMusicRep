import client from "./client.js"

export const login= (data)=> client.post('/auth/login', data)

export const register= (data)=> client.post('/auth/register', data)

export const getMe= ()=> client.get('/auth/me')

export const changePassword = (data) => client.post('/auth/change-password', data)

export const uploadAvatar = (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/auth/upload-avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}