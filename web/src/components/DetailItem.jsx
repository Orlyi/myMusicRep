import {useNavigate} from "react-router-dom";
import {ChevronRight} from "lucide-react";

export function DetailItem({path, from, title, children}){
    const navigate= useNavigate()

    return(
        <div style={{boxSizing:"border-box",position:"relative",height:"10vh",width:"100vw",textAlign:"left",display:"flex",alignItems:"center",paddingLeft:"10vw",paddingRight:"10vw",justifyContent:"space-between"}} onClick={()=>navigate(path, {state:{from:from}})}>

            <span>{title}</span>
            {children}
            <ChevronRight style={{position:"absolute",right:0}}></ChevronRight>
        </div>
    )
}