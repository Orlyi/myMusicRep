import {Outlet, Link } from 'react-router-dom'
import {House, MessageCircle, List, UserRound, TextAlignJustify, ArrowLeftRight, Settings,NotepadText
,CircleAlert, ShieldCheck, LogOut} from "lucide-react"
import {useState} from "react";
import Sidebar from "../components/Sidebar.jsx"
import {SideItem, SideLabel} from "../components/SidebarItem.jsx";
import {PlayerBar} from "../components/PlayerBar.jsx";
import {QueueDrawer} from "../components/QueueDrawer.jsx";
import PlayerPage from "../pages/PlayerPage.jsx";
import {SongDetail} from "../components/SongDetail.jsx";

export default function MainLayout() {
	const [open, setOpen] = useState(false)
	const [headerContent, setHeaderContent]= useState(null)
	const [acting, setActing] = useState(1)
	const [queueOpen, setQueueOpen] = useState(false)
	const is_act=(n)=>{
		    setActing(n)
		    }

	return (
		    <div className="app-layout" style={{width:'100%'}}>
		        <nav className="top-nav">
		            {headerContent}
		            <button onClick= {()=> setOpen(true)}>
		                <TextAlignJustify></TextAlignJustify>
		            </button>
		        </nav>

		        <Sidebar open= {open} onClose= {()=> setOpen(false)}>

		            <div style={{display:"flex",flexDirection:"column",justifyContent:"space-between",height:"100%"}}>
		                <div>
		                    <div style={{height:"2em",display:"flex", justifyContent:"right",alignItems:"center",margin:"0.5em"}}>
		                        <SideItem path={"/profile/detail"} from={"/"} content={<><NotepadText></NotepadText><span>个人信息</span></>} onClose={()=> setOpen(false)}>
		                        </SideItem>
		                    </div>

		                    <div style={{height:"2em",display:"flex", justifyContent:"right",alignItems:"center",margin:"0.5em"}}>
		                        <SideItem path={"/security"} from={"/"} content={<><ShieldCheck></ShieldCheck><span>安全中心</span></>} onClose={()=> setOpen(false)}>
		                        </SideItem>
		                    </div>
		                </div>

		                <div>
		                    <div style={{height:"2em",display:"flex", justifyContent:"right",alignItems:"center",margin:"0.5em"}}>
		                        <SideItem path={"/about"} from={"/"} content={<><CircleAlert></CircleAlert><span>关于我们</span></>} onClose={()=> setOpen(false)}>
		                        </SideItem>
		                    </div>

		                    <div style={{height:"2em",display:"flex", justifyContent:"right",alignItems:"center",margin:"0.5em"}}>
		                        <SideItem path={"/login"} from={"/"} content={<><LogOut></LogOut><span>退出登录</span></>} onClose={()=> setOpen(false)}>
		                        </SideItem>
		                    </div>
		                </div>
		            </div>

		        </Sidebar>

		        <div className="queue" >
		            <QueueDrawer open={queueOpen} onClose={()=>setQueueOpen(false)}></QueueDrawer>
		        </div>

		        <PlayerPage onOpenQueue={()=>setQueueOpen(true)} />
	        <SongDetail />

		        <div className="Player">
		            <PlayerBar onOpenQueue={()=>setQueueOpen(true)}></PlayerBar>
		        </div>


		        <nav className="nav">
		            <Link to="/" onClick={()=>is_act(1)} className={acting===1 ?"isAct":""}>
		                <House></House>
		                <span>首页</span>
		            </Link>
		            <Link to="/messages" onClick={()=>is_act(2)} className={acting===2 ?"isAct":""}>
		                <MessageCircle></MessageCircle>
		                <span>消息</span>
		            </Link>
		            <Link to="/library" onClick={()=>is_act(3)} className={acting===3 ?"isAct":""}>
		                <List></List>
		                <span>列表</span>
		            </Link>
		            <Link to="/profile" onClick={()=>is_act(4)} className={acting===4 ?"isAct":""}>
		                <UserRound></UserRound>
		                <span>我的</span>
		            </Link>
		        </nav>
		    <main className="main-content">
		        <Outlet context={{ setHeaderContent }} />
		    </main>
		  </div>
		)
		}