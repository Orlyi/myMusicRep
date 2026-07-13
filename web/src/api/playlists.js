import client from "./client.js";

export const createPlaylist= (data) => client.post("/playlists", data)

export const listPlaylist = (params) => client.get("/playlists", {params})

export const myPlaylists = (params) => client.get("/playlists/my", {params})

export const getPlaylist = (id) => client.get(`/playlists/${id}`)

export const updatePlaylist = (id, data) => client.put(`/playlists/${id}`, data)

export const deletePlaylist = (id) => client.delete(`/playlists/${id}`)