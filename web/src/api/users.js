import client from "./client.js";

export const getMyInfo = () => {
    console.log('[users.js] getMyInfo called')
    return client.get("/users/me/info")
}

export const getMyHistory = (params) => client.get("/users/me/history", {params})

export const registerDuration = () => client.get("/users/me/register-duration")

export const writeMyInfo = (data) => client.put("/users/me", data)

