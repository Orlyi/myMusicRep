import {Outlet, Link } from 'react-router-dom'
import {House, MessageCircle, List, UserRound, TextAlignJustify} from "lucide-react"
import {useState} from "react";
import Sidebar from "../components/Sidebar.jsx"

export default function MainLayout() {
const [open, setOpen] = useState(false)
const [headerContent, setHeaderContent]= useState(null)

return (
    <div className="app-layout" style={{width:'100%'}}>
        <nav className="top-nav">
            {headerContent}
            <button onClick= {()=> setOpen(true)}>
                <TextAlignJustify></TextAlignJustify>
            </button>
        </nav>

        <Sidebar open= {open} onClose= {()=> setOpen(false)}></Sidebar>

        <nav className="nav">
            <Link to="/">
                <House></House>
                <span>首页</span>
            </Link>
            <Link to="/messages">
                <MessageCircle></MessageCircle>
                <span>消息</span>
            </Link>
            <Link to="/library">
                <List></List>
                <span>列表</span>
            </Link>
            <Link to="/profile">
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