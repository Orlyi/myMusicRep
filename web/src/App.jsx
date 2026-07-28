import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import {HomePage, AlbumDetailPage, ArtistDetailPage, LibraryPage, LoginPage, MessagesPage, PlaylistDetailPage,
ProfilePage, RegisterPage, SearchPage, SongDetailPage, ProfileDetailPage} from './pages'
import SecurityPage from "./pages/SecurityPage.jsx";
import AboutPage from "./pages/AboutPage.jsx";
import useAuth from "./hooks/useAuth.js";
import {PlayerProvider} from "./layouts/PlayerContext.jsx";

export default function APP(){
    useAuth()

    return(
        <PlayerProvider>
        <Routes>
            <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/library" element={<LibraryPage />} />
                <Route path="/messages" element={<MessagesPage />} />
                <Route path="/profile" element={<ProfilePage />} />
            </Route>
            <Route path="/profile/detail" element={<ProfileDetailPage />} />
            <Route path="/security" element={<SecurityPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/song/:id" element={<SongDetailPage />} />
            <Route path="/artist/:id" element={<ArtistDetailPage />} />
            <Route path="/album/:id" element={<AlbumDetailPage />} />
            <Route path="/playlist/:id" element={<PlaylistDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
        </Routes>
        </PlayerProvider>
    )
}