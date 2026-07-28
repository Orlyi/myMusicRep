import {useEffect} from "react";
import {useLocation, useNavigate} from "react-router-dom";

const publicPaths=[ "/", "/register"]

export default function  useAuth(){
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        const token = localStorage.getItem("token") || sessionStorage.getItem("token")

        if (!token && !publicPaths.includes(location.pathname)){
            navigate("/login", {state:{from:location.pathname}})
        }
        if (token && publicPaths.includes(location.pathname)) {
          navigate("/")
      }
    }, [location.pathname]);

    const logout = () => {
          localStorage.removeItem("token")
          localStorage.removeItem("user")
          sessionStorage.removeItem("token")
          sessionStorage.removeItem("user")
          navigate("/login")
      }
    return {logout}

}