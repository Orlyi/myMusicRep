import client from "./client.js";

export const topSongs = (params) => client.get("/ranking/top-songs", {params})
export const topAlbums = (params) => client.get("/ranking/top-albums", {params})
export const topArtists = (params) => client.get("/ranking/top-artists", {params})
