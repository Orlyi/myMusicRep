import client from "./client.js";

export const followArtist = (id) => client.post(`/follow/artist/${id}`)

export const followUser = (id) => client.post(`/follow/user/${id}`)

export const unfollowArtist = (id) => client.delete(`/follow/artist/${id}`)

export const unfollowUser = (id) => client.delete(`/follow/user/${id}`)

