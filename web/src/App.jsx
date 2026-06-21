import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import {HomePage, AlbumDetailPage, ArtistDetailPage, LibraryPage, LoginPage, MessagesPage, PlaylistDetailPage, ProfilePage, RegisterPage, SearchPage, SongDetailPage} from './pages'

export default function APP(){
    return(
        <Routes>
            <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/song/:id" element={<SongDetailPage />} />
                <Route path="/artist/:id" element={<ArtistDetailPage />} />
                <Route path="/album/:id" element={<AlbumDetailPage />} />
                <Route path="/playlist/:id" element={<PlaylistDetailPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/library" element={<LibraryPage />} />
                <Route path="/messages" element={<MessagesPage />} />
                <Route path="/profile" element={<ProfilePage />} />
            </Route>
        </Routes>
    )
}