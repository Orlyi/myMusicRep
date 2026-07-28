import {useState} from "react";
import {register, uploadAvatar} from "../api/auth.js";
import {useNavigate, useLocation, Link} from "react-router-dom";
import "./RegisterPage.css"
import TopBar from "../components/TopBar.jsx";
import {X, ImagePlus} from "lucide-react"

export default function RegisterPage(){
    const [userName, setUserName] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [email, setEmail] = useState("")
    const [avatarFile, setAvatarFile] = useState(null)
    const [avatarPreview, setAvatarPreview] = useState(null)
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const location = useLocation()
    const navigate = useNavigate()
    const from = location.state?.from
    const path = location.pathname

    const handleAvatarChange = (e) =>{
        const file = e.target.files[0]
        if(!file) return
        if(!file.type.startsWith("image/")){
            setError("请选择图片文件")
            return
        }
        setAvatarFile(file)
        setAvatarPreview(URL.createObjectURL(file))
    }

    const handleSubmit = async (e) =>{
        e.preventDefault()
        setError("")

        if(!userName.trim()){
            setError("用户名不能为空")
            return
        }

        if(!password.trim()){
            setError("密码不能为空")
            return
        }

        if(password.length < 6){
            setError("密码不能少于6位")
            return
        }

        if(password !== confirmPassword){
            setError("两次密码不一致")
            return
        }

        setLoading(true)
        try{
            // 先上传头像
            let avatar_url = null
            if(avatarFile){
                const uploadRes = await uploadAvatar(avatarFile)
                avatar_url = uploadRes.data?.avatar_url
            }

            // 注册
            await register({
                "user_name": userName,
                "password": password,
                "email": email || null,
                "avatar_url": avatar_url
            })

            navigate("/login", {state:{from}})
        } catch (err){
            setError(err.response?.data?.detail || "注册失败")
        } finally{
            setLoading(false)
        }

    }

    return (
        <>
            <header className="registerpage">
                <TopBar from={from} path={path} title="创建账号"></TopBar>
            </header>

            <main className="registerpage">
                <form onSubmit={handleSubmit}>
                    {/* 头像上传 */}
                    <div className="avatar-upload">
                        <label htmlFor="avatar-input" style={{display:"flex",flexDirection:"column",justifyContent:"center",alignItems:"center"}}>
                            {avatarPreview ? (
                                <img src={avatarPreview} alt="头像预览" className="avatar-preview" />
                            ) : (
                                <>
                                <ImagePlus></ImagePlus>
                                <span >上传头像</span>
                                </>
                            )}
                        </label>
                        <input id="avatar-input" type="file" accept="image/*" onChange={handleAvatarChange} style={{display:"none"}} />
                        {avatarPreview && (
                            <X style={{color:"rgb(114,114,114)",width:"1em",cursor:"pointer"}} onClick={()=>{setAvatarFile(null); setAvatarPreview(null)}}></X>
                        )}
                    </div>

                    <div className="username">
                        <label>
                            <input className="user-input" type="text" value={userName} onChange={(e)=>{setUserName(e.target.value)}} placeholder="用户名" />
                        </label>
                        <X style={{color:"rgb(114,114,114)",width:"5%",opacity:userName ? 1: 0,transition:"all 0.3s ease"}} onClick={()=>{setUserName("")}}></X>
                    </div>

                    <div className="password">
                        <label>
                            <input className="pas-input" type="password" value={password} onChange={(e)=>{setPassword(e.target.value)}} placeholder="密码" />
                        </label>
                        <X style={{color:"rgb(114,114,114)",width:"5%",opacity:password ? 1: 0,transition:"all 0.3s ease"}} onClick={()=>{setPassword("")}}></X>
                    </div>

                    <div className="password">
                        <label>
                            <input className="pas-input" type="password" value={confirmPassword} onChange={(e)=>{setConfirmPassword(e.target.value)}} placeholder="确认密码" />
                        </label>
                        <X style={{color:"rgb(114,114,114)",width:"5%",opacity:confirmPassword ? 1: 0,transition:"all 0.3s ease"}} onClick={()=>{setConfirmPassword("")}}></X>
                    </div>

                    <div className="email">
                        <label>
                            <input className="email-input" type="email" value={email} onChange={(e)=>{setEmail(e.target.value)}} placeholder="邮箱（可选）" />
                        </label>
                        <X style={{color:"rgb(114,114,114)",width:"5%",opacity:email ? 1: 0,transition:"all 0.3s ease"}} onClick={()=>{setEmail("")}}></X>
                    </div>

                    <div>
                        <button type="submit" disabled={loading}><h2>{loading? "注册中..." : "注册"}</h2></button>
                    </div>

                </form>

                <div>
                    <Link to="/login">已有账号？登录</Link>
                </div>

                <div>
                    {error && <span className="error-font">{error}</span>}
                </div>

            </main>

            <footer className="registerpage">

            </footer>
        </>
    )
}