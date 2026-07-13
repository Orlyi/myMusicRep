import client from "./client.js";

export const listSongs = (params)=> client.get('/songs',{params})

export const getSong = (id) => client.get(`/songs/${id}`)

export const playSong = (id , data) => client.post(`/songs/${id}/play`, data)

export const downloadSong = (id) => client.post(`/songs/${id}/download`)

export const playCount = (id) => client.get(`/songs/${id}/play-count`)

export const downloadCount = (id) => client.get(`/songs/${id}/download-count`)
