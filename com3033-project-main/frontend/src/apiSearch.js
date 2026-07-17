import axios from "axios";
import { ACCESS_TOKEN } from "./constants";

//routing through to backend2 from included URLS within django
const scheme = window.location.protocol === "https:" ? "https" : "http";
const BASE_URL = `${scheme}://${window.location.host}/backend2`; 

const apiSearch = axios.create({
    baseURL: BASE_URL
})

apiSearch.interceptors.request.use(
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

export default apiSearch