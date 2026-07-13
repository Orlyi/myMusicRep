import client from "./client.js";

export const getLyrics = (id) => client.get(`/lyric/${id}`)