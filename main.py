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

    return songs

def gather_files_data(path):

    collected = []
    for (dirpath, dirnames, filenames) in walk(path):
        for filename in filenames:
            collected.append(dirpath + '/' + filename)

    return collected

def move_songs(songs, current, dest, depth, clear):

    total_size = len(songs)
    transfer_count = 0

    #Iterate songs that will be copied
    while len(songs) != 0:
        src_file = songs.pop().rstrip()
        src_items = src_file.split('/')

        dest_path = dest

        for pos in range(0, depth):
            dest_path = dest_path + '/' + src_items[-depth-1+pos]

        dest_file = dest_path + '/' + src_items[-1]

        # If file already exists, doesnt copy
        if dest_file in current:
            current.remove(dest_file)
        else:
            # Create directory if necessary
            if not os.path.exists(dest_path):
                os.makedirs(dest_path, exist_ok=True)

            shutil.copyfile(src=src_file, dst=dest_file, follow_symlinks=True)

            transfer_count = transfer_count + 1

            print("New music added ({}/{}): {}".format(transfer_count, total_size, dest_file))

    # Remove old files if requested
    if clear:

        total_size = len(current)
        transfer_count = 0

        for left_file in current:
            os.remove(left_file)
            transfer_count = transfer_count + 1
            print("File Removed ({}/{}): {}".format(transfer_count, total_size, left_file))

def main():

    parser = argparse.ArgumentParser(description='Copy musics based on input playlist data.')

    parser.add_argument('--playlist', type=str, help='Playlists path', action='append', required=True)
    parser.add_argument('--dest', type=str, help='Path to where the musics will be copied', required=True)
    parser.add_argument('--depth', type=int, default=0,
                        help='Folder depth that will be kept when moving files - '
                             'Default = 0, files are copied drectly to the root of the destination', )
    parser.add_argument('--clear', action='store_true', default=False,
                        help="Remove any other non-matched file")

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

    print("Gathering destination files information")
    # Look for the list of current files on the destination
    current_songs = gather_files_data(args.dest)

    print("Copying music to destination folder")
    # Move music files to the destination folder
    move_songs(all_songs, current_songs, args.dest, args.depth, args.clear)

if __name__ == "__main__":
    main()