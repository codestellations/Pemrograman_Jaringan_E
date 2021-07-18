import logging
import requests
import os
import datetime

counter = 1

def get_url_list():
    urls = dict()
    urls['kucing']='https://loremflickr.com/320/240/kitten'
    urls['anjing']='https://loremflickr.com/320/240/puppy'
    urls['burung']='https://loremflickr.com/320/240/bird'
    urls['bebek']='https://loremflickr.com/320/240/duckling'

    return urls

def get_gambar_list():
    gambar = dict()
    gambar['kucing'] = 'files/kucing_1.jpg'
    gambar['anjing'] = 'files/anjing_1.jpg'
    gambar['burung'] = 'files/burung_1.jpg'
    gambar['bebek'] = 'files/bebek_1.jpg'

    return gambar

def download_gambar(url=None, tuliskefile=True, namabaru="Image"):
    global counter

    waktu_awal = datetime.datetime.now()

    if (url is None):
        return False

    ff = requests.get(url)
    tipe = dict()
    tipe['image/png']='png'
    tipe['image/jpg']='jpg'
    tipe['image/gif']='gif'
    tipe['image/jpeg']='jpg'
    # time.sleep(2) #untuk simulasi, diberi tambahan delay 2 detik

    content_type = ff.headers['Content-Type']
    logging.warning(content_type)
    if (content_type in list(tipe.keys())):
        ekstensi = tipe[content_type]
        namafile = "files" + "/" + namabaru + "_" + str(counter) + "." + ekstensi

        # jika folder belum dibuat
        if not os.path.exists('files'):
            os.mkdir('files')

        # jika nama file sudah ada, nama file increment
        while os.path.exists(namafile):
            counter += 1
            namafile = "files" + "/" + namabaru + "_" + str(counter) + "." + ekstensi

        if (tuliskefile):
            fp = open(f"{namafile}","wb")
            fp.write(ff.content)
            fp.close()

        waktu_process = datetime.datetime.now() - waktu_awal
        waktu_akhir = datetime.datetime.now()
        logging.warning(f"writing {namafile} dalam waktu {waktu_process} {waktu_awal} s/d {waktu_akhir}")

        return waktu_process
    else:
        return False

if __name__=='__main__':
    #check fungsi
    urls = get_url_list()

    for k in urls:
        download_gambar(urls[k], True, k)

    # test = save_gambar('https://loremflickr.com/cache/resized/65535_51257294588_35bcceb35a_320_240_nofilter.jpg')
    # test = download_gambar('https://loremflickr.com/320/240/kitten', True)
