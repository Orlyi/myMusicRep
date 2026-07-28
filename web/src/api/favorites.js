import client from "./client.js";

export const saveSong= (id) => client.post(`/favorites/songs/${id}`)

export const savePlaylist = (id) => client.post(`/favorites/playlists/${id}`)

export const saveAlbum = (id) => client.post(`/favorites/albums/${id}`)

export const listFavorites = (params) => client.get("/favorites/list", {params})

export const unsaveSong = (id) => client.delete(`/favorites/songs/${id}`)

export const unsavePlaylist = (id) => client.delete(`/favorites/playlists/${id}`)

export const unsaveAlbums = (id) => client.delete(`/favorites/albums/${id}`)