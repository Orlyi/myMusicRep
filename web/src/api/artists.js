import client from "./client.js";

export const listArtists = (params) => client.get('/artists', {params})

export const artistSongs = (id, params) =>client.get(`/artists/${id}/songs`, {params})

export const artistAlbums = (id, params) => client.get(`/artists/${id}/albums`, {params})

export const getArtist = (id) => client.get(`/artists/${id}`)