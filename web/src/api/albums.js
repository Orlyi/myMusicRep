import client from "./client.js";

export const listAlbums = (params) => client.get('/albums', {params})

export const getAlbum = (id) => client.get(`/albums/${id}`)

export const getSongs = (id,params) => client.get(`/albums/${id}/songs`, {params})

