import TopBar from "../components/TopBar.jsx";
import {useLocation} from "react-router-dom";
import {useNavigate} from "react-router-dom";
import {SideItem} from "../components/SidebarItem.jsx";
import {DetailItem} from "../components/DetailItem.jsx";
import {getMyInfo} from "../api/users.js";
import {useEffect, useState} from "react";

export default function ProfileDetailPage(){
    const location = useLocation()
    const from = location.pathname
    const path = location.state?.from
    const [userInfo,setUserInfo]=useState(null)
    const [loading, setLoading]= useState(true)
    const fetchInfo = async () => {
        try{
            const res = await getMyInfo()
            console.log('[ProfilePage] getMyInfo result:', res)
            setUserInfo(res.data)
        } catch(err){
            console.log("获取用户信息失败", err)
        }
        finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchInfo()
    }, []);

    if(loading){
        return <div>加载中</div>
    }

    return (
        <div className="page">
            <header style={{height:'10vh'}}>
                <TopBar from={from} path={path} title="个人信息"></TopBar>
            </header>
            <main>
                <div className="detail-item" style={{display:"flex",flexDirection:"column",width:"100%"}}>
                    <DetailItem title="头像">
                        <img src={`http://localhost:8000${userInfo.user.avatar_url}` }style={{height:"100%",objectFit: "cover",borderRadius: "50%",aspectRatio:"1/1"}} ></img>

                    </DetailItem>
                </div>

                <div className="detail-item" style={{display:"flex",flexDirection:"column",width:"100%"}}>
                    <DetailItem title="昵称">
                        {userInfo?.details?.nickName ||"前往填写"}
                    </DetailItem>
                </div>

                <div className="detail-item" style={{display:"flex",flexDirection:"column",width:"100%"}}>
                    <DetailItem title="性别">
                        {userInfo?.details?.gender }
                    </DetailItem>
                </div>

                <div className="detail-item" style={{display:"flex",flexDirection:"column",width:"100%"}}>
                    <DetailItem title="生日">
                        {userInfo?.details?.birthdate ||"前往填写"}
                    </DetailItem>
                </div>

                <div className="detail-item" style={{display:"flex",flexDirection:"column",width:"100%"}}>
                    <DetailItem title="手机">
                        {userInfo?.details?.phoneNumber||"前往填写"}
                    </DetailItem>
                </div>

                <div className="detail-item" style={{display:"flex",flexDirection:"column",width:"100%"}}>
                    <DetailItem title="城市">
                        {userInfo?.details?.city||"前往填写"}
                    </DetailItem>
                </div>
            </main>

        </div>
    )
}