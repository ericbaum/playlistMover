import argparse
import shutil
import os
from os import walk

def parse_playlist(playlist):

    songs = []

    file = open(playlist, 'r')
    for line in file.readlines():
        if line[0] != '#':
            songs.append(line)

    file.close()

    return songs

def generate_playlists(playlists, dest, depth, real_path=None):

    if not real_path:
        real_path = dest

    for play in playlists:

        out_play = dest + '/' + play.split('/')[-1].split('.')[0] + '.m3u8'

        with open(play, 'r') as in_file:
            with open(out_play, 'w') as  out_file:
                for line in in_file.readlines():
                    # found a music
                    if line[0] != '#':
                        src_file = line.rstrip()
                        src_items = src_file.split('/')

                        dest_file = real_path

                        for pos in range(0, depth):
                            dest_file = dest_file + '/' + src_items[-depth-1+pos]

                        dest_file = dest_file + '/' + src_items[-1] + '\n'

                        out_file.write(dest_file)

def gather_files_data(path):

    collected = []
    for (dirpath, _, filenames) in walk(path):
        for filename in filenames:
            collected.append(dirpath + '/' + filename)

    return collected

def move_songs(songs, current, dest, depth, clear):

    total_size = len(songs)
    transfer_count = 0

    result_files = []
    result_files = current.copy()

    #Iterate songs that will be copied
    while len(songs) != 0:
        src_file = songs.pop().rstrip()
        src_items = src_file.split('/')

        dest_path = dest

        for pos in range(0, depth):
            dest_path = dest_path + '/' + src_items[-depth-1+pos]

        dest_file = dest_path + '/' + src_items[-1]

        transfer_count = transfer_count + 1

        # If file already exists, doesnt copy
        if dest_file in current:
            current.remove(dest_file)
        else:
            # Create directory if necessary
            if not os.path.exists(dest_path):
                os.makedirs(dest_path, exist_ok=True)

            try:
                shutil.copyfile(src=src_file, dst=dest_file, follow_symlinks=True)
                result_files.append(dest_file)
            except FileNotFoundError:
                print("Playlist contains invalid file: {}".format(src_file))
                continue          
            except OSError:
                print("Failed to copy file {}, retrying.".format(src_file))
                shutil.copyfile(src=src_file, dst=dest_file, follow_symlinks=True)

            print("New music added ({}/{}): {}".format(transfer_count, total_size, dest_file))

    # Remove old files if requested
    if clear:

        total_size = len(current)
        transfer_count = 0

        for left_file in current:
            os.remove(left_file)
            transfer_count = transfer_count + 1
            print("File Removed ({}/{}): {}".format(transfer_count, total_size, left_file))
            result_files.remove(left_file)

    return result_files

def main():

    parser = argparse.ArgumentParser(description='Copy musics based on input playlist data.')

    parser.add_argument('--playlist', type=str, help='Playlists path', action='append', required=True)
    parser.add_argument('--dest', type=str, help='Path to where the musics will be copied', required=True)
    parser.add_argument('--depth', type=int, default=0,
                        help='Folder depth that will be kept when moving files - '
                             'Default = 0, files are copied drectly to the root of the destination', )
    parser.add_argument('--clear', action='store_true', default=False,
                        help="Remove any other non-matched file")
    parser.add_argument('--no-use-cache', dest="cache", action='store_false', default=True,
                        help="Don't use the cellphone cached information")
    parser.add_argument('--play-dest', dest='play_dest', type=str, default=None, required=False,
                        help='Path where the playlist files will be created, defaults to dest')
    parser.add_argument('--play-path', dest='play_path', type=str, default=None, required=False,
                        help='Path that will be used as base for the playlist files, defaults to dest')

    args = parser.parse_args()

    print("Loading data from playlists")

    # Parse each of the playlists separetly
    parsed_plays = []
    index = 0
    for play in args.playlist:
        parsed_plays.insert(index, parse_playlist(play))
        index = index + 1

    print("Building transfer list")
    # Aggregate songs on a single list
    all_songs = set()
    for play in parsed_plays:
        for item in play:
            all_songs.add(item)

    if args.cache and os.path.isfile("cache.txt"):
        print("Loading cached files information")
        with open("cache.txt", 'r') as cache_file:
            current_songs = []
            for line in cache_file.readlines():
                current_songs.append(line.rstrip())
    else:
        print("Gathering destination files information")
        # Look for the list of current files on the destination
        current_songs = gather_files_data(args.dest)

    print("Copying music to destination folder")
    # Move music files to the destination folder
    result = move_songs(all_songs, current_songs, args.dest, args.depth, args.clear)

    print("Caching resulting files information")
    with open("cache.txt", 'w') as cache_file:
        for song in result:
            cache_file.write(song + '\n')

    print("Generating remote playlists")

    if args.play_dest:
        play_dest = args.play_dest
    else:
        play_dest = args.dest

    generate_playlists(args.playlist, play_dest, args.depth, args.play_path)  

if __name__ == "__main__":
    main()