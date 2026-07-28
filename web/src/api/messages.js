import client from "./client.js";

export const sendMessage = (data) => client.post("/message", data)

export const receivedMessage = (params) => client.get("/message/received", {params})

export const listMessages = (params) => client.get("/message/list", {params})

export const deleteMessageSoft = (id) => client.delete(`/message/${id}`)

export const deleteMessageHard = (id) => client.delete(`/message/${id}`)