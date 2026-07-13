import {ChevronLeft} from "lucide-react";
import {useNavigate} from "react-router-dom";

export default function GoBack({from, path}){
    const navigate = useNavigate()

    return (
        <ChevronLeft
            onClick={()=> from&&path ? navigate(from, {state:{from: path}}) : navigate(-1)}
        />
    )
}
