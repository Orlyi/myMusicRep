import {useNavigate} from "react-router-dom";



export const useNav = () =>{
    const navigate = useNavigate()

    const goHome = () =>{
        navigate("/")
    }
    const goLogin = () =>{
        navigate("/login")
    }
    const goBack = () =>{
        navigate(-1)
    }
    const goForward = () =>{
        navigate(1)
    }
    const refresh = () =>{
        navigate(0)
    }

    return {goHome, goLogin, goBack, goForward, refresh}
}
