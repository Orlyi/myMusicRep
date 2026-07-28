import client from "./client.js";

export const searchSongName = (params) => client.get("/search/song-name", {params})

export const searchArtistName = (params) => client.get("/search/artist-name", {params})

export const searchAlbumName = (params) => client.get("/search/album-name", {params})

export const searchPlainLyric = (params) => client.get("/search/plain-lyric", {params})

// 网络搜索
export const networkSearch = (params) => client.get("/network/search", {params})

// 播放地址
export const networkPlayUrl = (params) => client.get("/network/play-url", {params})

// 拉取专辑并存库 → 返回本地 album_id
export const fetchAlbumDetail = (params) => client.get("/network/album-detail", {params: {...params, save: true}})