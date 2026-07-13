import {useEffect,useState} from "react";
import { login} from "../api/auth.js";
import {useNavigate, useLocation, Link} from "react-router-dom";
import "./LoginPage.css"
import TopBar from "../components/TopBar.jsx";
import {X} from "lucide-react"

export default function LoginPage(){
    const saved = JSON.parse(localStorage.getItem("remembered") || null)

    const [autoLogin, setAutoLogin] = useState(false)
    const [userName, setUserName] = useState(saved?.userName || "")
    const [password, setPassword] = useState(saved?.password || "")
    const [remember, setRemember] = useState(!!saved)
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const location = useLocation()
    const navigate = useNavigate()
    const from = location.state?.from
    const path = location.pathname

    useEffect(()=>{
        if(error){
            console.log(error)
        }
    }, [error])


    const handleSubmit = async (e) =>{
        e.preventDefault()
        setError("")

        if(!userName.trim()){
            setError("UserName cannot be empty")
            return
        }

        if(!password.trim()){
            setError("Password cannot be empty")
            return
        }

        setLoading(true)
        try{
            const result = await login({
                "user_name": userName,
                "password": password
            })

            const storage = autoLogin ? localStorage : sessionStorage
            storage.setItem("token", result.data.token)
            storage.setItem("user", JSON.stringify(result.data))

            if(remember){
                localStorage.setItem("remembered", JSON.stringify({userName, password}))
            }else{
                localStorage.removeItem("remembered")
            }
            navigate("/")
        } catch (err){
            setError(err.response?.data?.detail || "登陆失败")
        } finally{
            setLoading(false)
        }

    }

    return (
        <>
            <header className="loginpage">
                <TopBar from={from} path={path} title="账号密码登录"></TopBar>
            </header>

            <main className="loginpage">
                <form onSubmit={handleSubmit}>
                    <div className="username">
                        <label>
                            {/*<span>用户</span>*/}
                            <input className="user-input" type="text" value={userName} onChange={(e)=>{setUserName(e.target.value)}} placeholder="用户名" />
                        </label>
                        <X style={{color:"rgb(114,114,114)",width:"5%",opacity:userName ? 1: 0,transition:"all 0.3s ease"}} onClick={()=>{setUserName("")}}></X>

                    </div>

                    <div className="password">
                        <label>
                            {/*<span>密码</span>*/}
                            <input className="pas-input" type="password" value={password} onChange={(e)=>{setPassword(e.target.value)}} placeholder="密码" />
                        </label>
                        <X style={{color:"rgb(114,114,114)",width:"5%",opacity:password ? 1: 0,transition:"all 0.3s ease"}} onClick={()=>{setPassword("")}}></X>
                    </div>
                    <div>
                        <button type="submit"><h2>登录</h2></button>
                    </div>

                </form>
                <div className="remember">
                    <label>
                        <input className="newChecked" type="checkbox" checked={remember} onChange={(e)=> {setRemember(e.target.checked)}}></input>
                        <span className="rem-font">记住密码</span>
                    </label>
                    <label>
                        <input className="newChecked" type="checkbox" checked={autoLogin} onChange={(e)=> {setAutoLogin(e.target.checked)}}></input>
                        <span className="rem-font">自动登录</span>
                    </label>
                </div>



                <div>
                    <Link to="/register">注册</Link>
                </div>
                <div>
                    {error && <span className="error-font">{error}</span>}
                </div>

            </main>

            <footer className="loginpage">

            </footer>
        </>
    )
}