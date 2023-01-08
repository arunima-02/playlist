from typing import Optional
from fastapi import FastAPI,Response, status , HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Playlist(BaseModel):
    name : str
    

class Songs(BaseModel):
    title : str
    artist : str
    album : str


class add_remove_to_playlist(BaseModel):
    pid : int
    sid : int


while(1):
    try :
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='123',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break; 

    except Exception as error :
        print("Connecting to database failed")
        print("Error : ",error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Yoo"}


@app.get("/playlists")
def get_playlists():
    cursor.execute("""select * from playlists """)
    playlists = cursor.fetchall()
    arr=[]
    dict ={}
    for row in playlists :
        cursor.execute("""select count("songId") from songs where "playlistId"={}""".format(row['playlistId']))
        no_of_songs=cursor.fetchone()
        dict = {"id":row['playlistId'] , "name" : row['name'] ,"songs" : no_of_songs["count"]}
        arr.append(dict)
    return arr


@app.get("/playlists/{id}")
def get_one_playlists(id : int):
    cursor.execute("""select * from playlists where "playlistId"={}""".format(id))
    rec = cursor.fetchone()   
    cursor.execute("""select * from songs where "playlistId"={}""".format(id))
    rec_song= cursor.fetchall()
    dict = {"id":rec['playlistId'] , "name" : rec['name'] ,"songs" : rec_song}    
    return dict


@app.get("/songs")
def get_songs():
    cursor.execute("""select * from songs """)
    songs = cursor.fetchall()
    return songs


@app.get("/songs/{id}")
def get_one_songs(id : int):
    cursor.execute("""select * from songs where "songId"={}""".format(id))
    song = cursor.fetchall()
    return song


@app.post("/playlists",status_code=status.HTTP_201_CREATED)
def create_playlists(playlist: Playlist):
    print(playlist.name)
    cursor.execute("""insert into playlists (name) values ('{}') returning * """.format(playlist.name))
    new_playlists = cursor.fetchone()
    conn.commit()
    return new_playlists
   

@app.post("/songs",status_code=status.HTTP_201_CREATED)
def create_songs(song: Songs):
    cursor.execute("""insert into songs (title,artist,album) values ('{}','{}','{}') returning * """.format(song.title,song.artist,song.album))
    new_songs = cursor.fetchone()
    conn.commit()
    return new_songs

@app.post("/add-to-playlist",status_code=status.HTTP_201_CREATED)
def addtoplaylist(atp : add_remove_to_playlist):
    cursor.execute("""update songs set "playlistId" = {} where "songId" = {} returning * """.format(atp.pid , atp.sid))
    added = cursor.fetchone()
    conn.commit()
    if added == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message" : "song added to playlist"}


@app.post("/remove-from-playlist")
def removefromplaylist(atp : add_remove_to_playlist):
    cursor.execute("""update songs set "playlistId" = {} where "songId" = {} returning * """.format(0 , atp.sid))
    added = cursor.fetchone()
    conn.commit()
    if added == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message" : "song removed from playlist"}


@app.delete("/playlists/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletefromplaylist(id :int):
    cursor.execute("""delete from playlists where "playlistId" = {} returning * """.format(id))
    deleted = cursor.fetchone()
    conn.commit()
    if deleted == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"playlist with id :{id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/songs/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletefromsong(id :int):
    cursor.execute("""delete from songs where "songId" = {} returning * """.format(id))
    deleted = cursor.fetchone()
    conn.commit()
    if deleted == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"song with id :{id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/playlists/{id}")
def update_playlist(id :int , playlist: Playlist):
    cursor.execute("""update playlists set "name"='{}' where "playlistId" = {} returning * """.format(playlist.name , id))
    updated = cursor.fetchone()
    conn.commit()
    if updated == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"playlist with id :{id} does not exist")
    return {"data" : updated}


@app.put("/songs/{id}")
def update_song(id :int , song: Songs):
    cursor.execute("""update songs set "title"='{}' ,"artist"='{}' , "album"='{}' where "songId" = {} returning * """.format(song.title ,song.artist , song.album, id))
    updated = cursor.fetchone()
    print(updated)
    conn.commit()
    if updated == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"playlist with id :{id} does not exist")
    return {"data" : updated}

