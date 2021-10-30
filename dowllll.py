import os
import requests
import threading
import time

path = "E:/f/"

threadsRestriction = 50
renderThreadsRestriction = 6


def concatenate(chunksPath):
    global path
    if save_index(path+chunksPath):
        os.system('ffmpeg -y -f concat -i "{}/chunks.txt" -c copy "{}concatenated/{}.mp4"'.format(path+chunksPath, path, chunksPath))


def save_index(path):
    files = []
    for i in os.listdir(path):
        files += [i.split(".")[0]]
    if len(files[0])<10:
        q = sorted(files, key=int)
    else:
        q = sorted(files)
    if "chunks" in q:
        q.remove("chunks")
        with open(path + "/chunks.txt", "r") as f:
            if len(q) == len(f.readlines()):
                return False
    with open(path + "/chunks.txt", "w") as file:
        file.writelines(["file "+ i + ".ts\n" for i in q])
    return True


def download(link, save_path):                                          # download content function
    global checkAllSize
    name = link.split("/")[-1].split("?")[0]
    if os.path.exists(save_path+name):
        if checkAllSize:
            fileSize = os.path.getsize(save_path+name)
            realSize = int(requests.head(link).headers['Content-Length'])
            if fileSize == realSize:
                return                                                  # skip if the file has already been downloaded
        else:
            return
    r = requests.get(link)                                              # request content
    if r.status_code != 200:
        raise Exception("lol kek " + str(r.status_code))                # check for errors in the committed request
    else:
        with open(save_path+name, "wb") as f:
            f.write(r.content)


def handle_file(filename, filepath):  
    global threadsRestriction                                           # function to handle desired file with links
    print("handling "+filename)
    with open(filepath+filename, "r") as file:
        data = file.readlines()
        save_path = filepath+filename[:-5]+"/"                          # constructing path to save video chunks
        if not os.path.exists(save_path):                               # check for the directory
            os.mkdir(save_path)
        for line in data:
            if "http" in line:
                while threading.active_count() > threadsRestriction:
                    time.sleep(0.2)
                threading.Thread(target=download, args=(line, save_path)).start()


if __name__ == "__main__":
    checkAllSize = not(bool(input("check all files? empty - yes")))
    for file in os.listdir(path):
        if os.path.isfile(path+file):
            handle_file(file, path)
    for folder in os.listdir(path):
        if os.path.isdir(path+folder) and folder!="concatenated":
            while threading.active_count() > renderThreadsRestriction:
                    time.sleep(0.2)
            threading.Thread(target=concatenate, args=(folder,)).start()
            #concatenate(folder)