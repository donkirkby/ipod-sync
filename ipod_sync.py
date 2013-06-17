from gpod.ipod import Database, Track
import os

""" After a reset, the iPod has 484KB used, or 895MB free.
"""

def copy_file(db, filename):
    podcasts = db.get_podcasts()
    master = db.get_master()
    track = Track(filename, 
        podcast=True)
    track.copy_to_ipod()
    db.add(track)
    master.add(track)
    podcasts.add(track)
    
def copy_track(db, track):
    podcasts = db.get_podcasts()
    master = db.get_master()
    track.copy_to_ipod()
    db.add(track)
    master.add(track)
    podcasts.add(track)
    
def copy_tracks(db, folders):
    for folder, tracks in folders.items():
        for filename, track in tracks.items():
            copy_track(db, track)

def remove_all(db):
#    print 'Podcasts:'
#    podcasts = db.get_podcasts()
#    for p in podcasts:
#        print p
#    
#    db.remove(podcasts)
    print 'Other:'
    master = db.get_master()
    tracks = list(db)
    for track in tracks:
        print track['title']
        db.remove(track)

def remove_deleted(db, folders):
    master = db.get_master()
    tracks = list(db)
    for track in tracks:
        album = track['album']
        title = track['title']
        folder = folders.get(album)
        library_track = folder and folder.pop(title, None)
        if library_track is None:
            print 'removing %s/%s.' % (album, title)
            db.remove(track)

def list_all(db):
    print 'Podcasts:'
    podcasts = db.get_podcasts()
    for p in podcasts:
        print p
    
    print 'Other:'
    master = db.get_master()
    for track in master:
        print track['title']
    
    print 'Unattached?'
    for track in db:
        print track['title']
        
def switch_to_podcast(db):
    podcasts = db.get_podcasts()
    for track in db:
        if track['title'].startswith('1207'):
            print track['album']
            track['album'] = 'Planet Money'
            if track not in podcasts:
                podcasts.add(track)
                
def list_files(rootpath):
    folders = {}
    for dirpath, dirname, filenames in os.walk(rootpath):
        parent, folder = os.path.split(dirpath)
        if parent == rootpath:
            tracks = {}
            folders[folder] = tracks
            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                filesize = os.stat(fullpath).st_size
                try:
                    track = Track(fullpath,
                                  podcast=True)
                    track['album'] = folder
                    track.filesize = filesize
                    tracks[track['title']] = track
                except Exception, e:
                    print "Could not load '%s': %s" % (folder + '/' + filename, 
                                                       e)
    return folders
    
    
def get_fs_freespace(pathname):
    "Get the free space of the filesystem containing pathname"
    stat= os.statvfs(pathname)
    # use f_bfree for superuser, or f_bavail if filesystem
    # has reserved space for superuser
    return stat.f_bfree*stat.f_bsize / (1024*1024)

def main():
    mount_point = '/media/IPOD'
    db = Database(mount_point)
    try:
#         db.__repr__()
        folders = list_files('/home/don/Music')
        remove_deleted(db, folders)
        copy_tracks(db, folders)
#         switch_to_podcast(db)
#         list_all(db)
#         remove_all(db)
        filename = '/home/don/Music/NPR: Planet Money Podcast/npr_157681373.mp3'
#         copy_file(db, filename)
        
        db.copy_delayed_files()
        print "%sMB free space remaining." % get_fs_freespace(mount_point)
        print 'Success.'
    finally:
        db.close()
    print 'Done.'

if __name__ == '__main__':
    main()