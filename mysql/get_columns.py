import pymysql
import pandas as pd

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sql2008',
    database='myMusic'
)

tables = [
    'users', 'songs', 'artists', 'albums', 'playlists',
    'comments', 'lyrics', 'messages', 'play_history',
    'user_save_song', 'user_save_album', 'user_save_playlist',
    'user_follow_artist', 'user_follow_user', 'user_like_comment',
    'artist_sing_song', 'album_save_song', 'playlist_save_song',
    'search_history', 'user_details'
]

for table in tables:
    cursor = conn.cursor()
    cursor.execute(f"DESC {table}")
    columns = cursor.fetchall()
    print(f"\n {table}")
    for col in columns:
        print(f"  {col[0]} | {col[1]} | {col[2]} | {col[3]}")
    cursor.close()

conn.close()