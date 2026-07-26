import client from "./client.js";

export const recommend = (params) => client.get("/recommend/recommend", {params})
export const recommendPlaylists = (params) => client.get("/recommend/playlists", {params})
