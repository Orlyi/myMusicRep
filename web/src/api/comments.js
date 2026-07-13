import client from "./client.js";

export const createComment = (id, data) => client.post(`/comments/songs/${id}/comments`, data)

export const listComments = (id, params) => client.get(`/comments/songs/${id}/comments`, {params})

export const deleteComment = (id) => client.delete(`/comments/comments/${id}`)