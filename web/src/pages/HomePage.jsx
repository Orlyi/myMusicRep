import {useEffect} from "react";
import {useNavigate, useOutletContext} from "react-router-dom";
import client from "../api/client.js";
import "./HomePage.css"
import TopBar from "../components/TopBar.jsx";
import {Search} from "lucide-react"


export default function HomePage(){
    const navigate = useNavigate()
    const {setHeaderContent} = useOutletContext()

    useEffect(() => {
        setHeaderContent(
            <TopBar from="/" path="/">
                <div className="S" onClick={()=>navigate("/search")}>
                    <Search></Search>
                    <div className="search-for"></div>
                </div>

            </TopBar>
        )
        return () => setHeaderContent(null)
    }, [setHeaderContent])

    return (
        <div className="page">
        </div>
    )
}