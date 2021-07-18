from library import get_gambar_list
import datetime
from multiprocessing import Process
import logging
import socket

TARGET_IP = '255.255.255.255'
TARGET_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def kirim_gambar(namafile=None):
    waktu_awal = datetime.datetime.now()

    if (namafile is None):
        return False

    fp = open(namafile, 'rb')
    k = fp.read()

    terkirim=0

    for x in k:
       k_bytes = bytes([x])
       sock.sendto(k_bytes, (TARGET_IP, TARGET_PORT))
       terkirim = terkirim + 1

    print("terkirim ", namafile)
    fp.close()

    waktu_process = datetime.datetime.now() - waktu_awal
    waktu_akhir = datetime.datetime.now()
    logging.warning(f"sending {namafile} dalam waktu {waktu_process} {waktu_awal} s/d {waktu_akhir}")

    return waktu_process

def kirim_semua():
    texec = dict()
    gambar = get_gambar_list()
    catat_awal = datetime.datetime.now()

    for k in gambar:
        print(f"mengirim {gambar[k]}")

        # bagian ini merupakan bagian yang mengistruksikan eksekusi fungsi download gambar secara multiprocess
        texec[k] = Process(target=kirim_gambar, args=(gambar[k],))
        texec[k].start()

    # setelah menyelesaikan tugasnya, dikembalikan ke main process dengan join
    for k in gambar:
        texec[k].join()

    catat_akhir = datetime.datetime.now()
    selesai = catat_akhir - catat_awal
    print(f"Waktu TOTAL yang dibutuhkan {selesai} detik {catat_awal} s/d {catat_akhir}")

# fungsi kirim_gambar akan dijalankan secara multi process
if __name__=='__main__':
    # download_semua()
    kirim_semua()
