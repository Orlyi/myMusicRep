from fastapi import APIRouter

from app.api.v1 import health, users, songs, auth, artists, albums, lyric, favorites, comments, playlists, search, follow, message, network_search, ranking, recommend

router = APIRouter(prefix="/api/v1")
router.include_router(health.router, tags=["Health"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(songs.router, prefix="/songs", tags=["Songs"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(artists.router, prefix="/artists", tags=["Artists"])
router.include_router(albums.router, prefix="/albums", tags=["Albums"])
router.include_router(lyric.router, prefix="/lyric", tags=["Lyric"])
router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
router.include_router(comments.router, tags=["Comments"])
router.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
router.include_router(search.router, prefix="/search", tags=["Search"])
router.include_router(follow.router, prefix="/follow", tags=["Follow"])
router.include_router(message.router, prefix="/message", tags=["Message"])
router.include_router(network_search.router, prefix="/network", tags=["Network Search"])
router.include_router(ranking.router, prefix="/ranking", tags=["Ranking"])
router.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])