import socket
import json
import base64
import logging
import datetime
import threading
import concurrent.futures
from multiprocessing import Process, Pool

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename="", counter=0):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes

        namafile= hasil['data_namafile']

        split = namafile.split(".")
        nama = split[0].strip()
        ekstensi = split[1].strip()

        namafile = "files" + "\\" + nama + "_" + str(counter) + "." + ekstensi

        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_get_100(filename=""):
    texec = dict()
    status_task = dict()

    task_pool = Pool(processes=10) #2 task yang dapat dikerjakan secara simultan, dapat diset sesuai jumlah core
    task = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    catat_awal = datetime.datetime.now()

    # multiprocess
    # for k in range(0, 100):
    #     print(f"mendownload {filename} {k+1}")
    #
    #     #bagian ini merupakan bagian yang mengistruksikan eksekusi fungsi download gambar secara multiprocess
    #     texec[k] = Process(target=remote_get, args=(filename, k+1))
    #     texec[k].start()
    # #setelah menyelesaikan tugasnya, dikembalikan ke main process dengan join
    # for k in range(0, 100):
    #     texec[k].join()

    # multithread async
    # for k in range(1, 11):
    #     print(f"mendownload {filename} {k}")
    #
    #     #bagian ini merupakan bagian yang mengistruksikan eksekusi fungsi download gambar secara multithread
    #     texec[k] = task.submit(remote_get, filename, k)
    #
    #
    # #setelah menyelesaikan tugasnya, dikembalikan ke main thread dengan memanggil result
    # for k in range(0, 10):
    #     status_task[k]=texec[k].result()
    #

    # multithread
    # for k in range(0, 100):
    #     print(f"mendownload {filename} {k+1}")
    #
    #     #bagian ini merupakan bagian yang mengistruksikan eksekusi fungsi download gambar secara multithread
    #     texec[k] = threading.Thread(target=remote_get, args=(filename, k+1))
    #     texec[k].start()
    #
    # #setelah menyelesaikan tugasnya, dikembalikan ke main thread dengan join
    # for k in range(0, 100):
    #     texec[k].join()

    # multiprocess async
    for k in range(0, 100):
        print(f"mendownload {filename} {k+1}")

        #bagian ini merupakan bagian yang mengistruksikan eksekusi fungsi download gambar secara multiprocess
        texec[k] = task_pool.apply_async(func=remote_get, args=(filename, k+1))

    #setelah menyelesaikan tugasnya, dikembalikan ke main process dengan mengambil hasilnya dengan get
    for k in range(0, 100):
        status_task[k]=texec[k].get(timeout=10)

    catat_akhir = datetime.datetime.now()
    selesai = catat_akhir - catat_awal
    print(f"Waktu TOTAL yang dibutuhkan {selesai} detik {catat_awal} s/d {catat_akhir}")
    # print("status TASK")
    # print(status_task)

    return

if __name__=='__main__':
    server_address=('127.0.0.1',7777)
    remote_list()
    # remote_get('donalbebek.jpg', 1)
    remote_get_100('pokijan.jpg')
