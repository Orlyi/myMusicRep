import client from "./client.js";

export const searchSongName = (params) => client.get("/search/song-name", {params})

export const searchArtistName = (params) => client.get("/search/artist-name", {params})

export const searchAlbumName = (params) => client.get("/search/album-name", {params})

export const searchPlainLyric = (params) => client.get("/search/plain-lyric", {params})

// 网络搜索
export const networkSearch = (params) => client.get("/network/search", {params})

// 播放地址
export const networkPlayUrl = (params) => client.get("/network/play-url", {params})