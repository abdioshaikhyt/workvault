import axios from "axios"
import { ACCESS_TOKEN } from "./constants"

const scheme = window.location.protocol === "https:" ? "https" : "http";
export const BASE_URL = `${scheme}://${window.location.host}`; 

const apiAuth = axios.create({
    baseURL: BASE_URL
})

apiAuth.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem(ACCESS_TOKEN);
        if(token){
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default apiAuth