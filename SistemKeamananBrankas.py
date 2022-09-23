import cv2
import numpy as np
import datetime
from datetime import timedelta
import time
import serial
import os
import glob
import telepot
import adafruit_fingerprint
import RPi.GPIO as GPIO
from PIL import *
from time import sleep

# Wilayah Inisialisasi
samplenum = int()
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21, GPIO.OUT) # Relay
GPIO.setup(26, GPIO.OUT) # Buzzer
# Akhir Inisialisasi

# Wilayah def/functions/class
class sistemKeamananBrankas:
    def __init__(self, file_location):
        # ttyS0: Kabel GPIO Raspberry
        # ttyUSB0: Kabel USB
        uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
        self.finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        self.file_location = file_location

    def mendeteksi_fingerprint(self):
        if self.finger.get_image() != adafruit_fingerprint.OK:
            sleep(1)
            return "Menunggu"
        if self.finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return "Tidak dapat membaca"
        print("Mencari...")
        if self.finger.finger_search() != adafruit_fingerprint.OK:
            return "Tidak ditemukan"
        print("Mendeteksi #", self.finger.finger_id, "dengan konfidensi", self.finger.confidence)
        return "Ditemukan kecocokan"

def handle(msg):
    global telegramText
    global chat_id
    global receiveTelegramMessage
        
    chat_id = msg['chat']['id']
    command = msg['text']
    getUser = bot.getChat(chat_id)
    user = str(getUser['username'])

    print('Mendapatkan command: %s' % command)
        
    if(len(user) > 8):
        user = user[:8]
    elif(len(user) < 6):
        user = "user_" + user
        print(user)
        
        start = "‒‒‒‒‒‒‒‒◈ Selamat datang ◈‒‒‒‒‒‒‒‒\n"
        start += "                          " + user + "\n"
        start += "\n"
        start += "‒‒‒‒‒‒‒◈ Infomasi Perintah ◈‒‒‒‒‒‒‒\n"
        start += "                          【/start】\n"
        start += "                  Untuk memulai BOT\n"
        start += "                          【/info】\n"
        start += "              Informasi mengenai BOT"
        
        bot.sendMessage(chat_id, start)
            
    elif command == '/uptime':
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(timedelta(seconds=uptime_seconds))
            bot.sendMessage(chat_id, uptime_string)
            print("%s said it want the uptime" % chat_id)

chat_id = '#CHAT_ID'
bot = telepot.Bot('#TOKEN')
bot.message_loop(handle)

receiveTelegramMessage = False
sendTelegramMessage = False

statusText = ""

videocam = cv2.VideoCapture(0)
videocam.set(cv2.CAP_PROP_FPS, 30)
videocam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
face_cascade = cv2.CascadeClassifier('face-detect.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('recognizer/dataTraining.yml')
id=0
count = 0
font=cv2.FONT_HERSHEY_SIMPLEX

GPIO.output(21, GPIO.HIGH) # Kondisi Relay Awal Mati
GPIO.output(26, GPIO.LOW) # Kondisi Buzzer Awal Mati

sistemKeamanan = sistemKeamananBrankas("#DirektoriFolderProject")
        
while True:
    if receiveTelegramMessage == True:
            receiveTelegramMessage = False
        
            statusText = ""
            sendTelegramMessage = True
        
    if sendTelegramMessage == True:
            sendTelegramMessage = False
            bot.sendMessage(chat_id, statusText)
    
    # Relay/Brankas Menutup
    fingerprint_sta = sistemKeamanan.mendeteksi_fingerprint()
    if(fingerprint_sta == "Menunggu"):
        print("Menunggu untuk mengambil gambar..")
    elif(fingerprint_sta == "Ditemukan kecocokan"):
        cand, frame = videocam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        muka = face_cascade.detectMultiScale(gray, 1.5, 5)
        for (x,y,w,h) in muka:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 5)
            id,conf=recognizer.predict(gray[y:y+h, x:x+w])
            
            if(id==1):
                id = "#Nama"
            
            # Conf semakin kecil semakin cocok
            if(conf<=50):
                # Kondisi 1
                confid =" {0}%".format(round(100-conf))
                cv2.putText(frame, str(id), (x-5,y-5),font,2, (0,255,255),2, cv2.LINE_AA)
                cv2.putText(frame,str(confid), (x,y+h), font, 2, (0,255,255), 2, cv2.LINE_AA)
                cv2.imwrite("dikenal/img"+str(samplenum)+".jpg", frame)
                if not cv2.imwrite(r"dikenal/img"+str(samplenum)+".jpg", frame):
                    print("Foto tidak berhasil disimpan")
                    cv2.imwrite("dikenal/img"+str(samplenum)+".jpg", frame)
                print("Sidik jari sesuai dan Wajah dikenali")
                list_of_files = glob.glob('#DirektoriFolderProject/*') # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getctime)
                bot.sendPhoto(chat_id, photo=open(latest_file, 'rb'))
                bot.sendMessage(chat_id, "Sidik jari dan Wajah sesuai")
                brankasTerbuka = "Brankas terbuka dengan aman \n"
                brankasTerbuka += "Selama 5 detik..."
                bot.sendMessage(chat_id, brankasTerbuka)
                # Relay/Brankas Membuka
                GPIO.output(21, GPIO.LOW)
                GPIO.output(26, GPIO.HIGH)
                print("Beep")
                sleep(0.5)
                GPIO.output(26, GPIO.LOW)
                sleep(0.5)
                GPIO.output(26, GPIO.HIGH)
                print("Beep")
                sleep(0.5)
                GPIO.output(26, GPIO.LOW)
                print("Brankas terbuka dengan aman")
                samplenum = samplenum+1
                videocam.release() # VideoCam berhenti merekam
                sleep(5)
                videocam = cv2.VideoCapture(0)
                videocam.set(cv2.CAP_PROP_FPS, 30)
                videocam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
                GPIO.output(21, GPIO.HIGH)
                bot.sendMessage(chat_id, "Solenoid terkunci")
            else:
                # Kondisi 2
                confid =" {0}%".format(round(100-conf))
                cv2.putText(frame, "Tidak Dikenal" , (x-5,y-5),font,2, (0,255,255),2, cv2.LINE_AA)
                cv2.putText(frame,str(confid), (x,y+h), font, 2, (0,255,255), 2, cv2.LINE_AA)
                cv2.imwrite("tidakkenal/img"+str(samplenum)+".jpg", frame)
                if not cv2.imwrite(r"tidakkenal/img"+str(samplenum)+".jpg", frame):
                    print("Foto tidak berhasil disimpan")
                    cv2.imwrite("tidakkenal/img"+str(samplenum)+".jpg", frame)
                print("Sidik jari sesuai dan Wajah tidak dikenali")
                list_of_files = glob.glob('#DirektoriFolderProject/*') # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getctime)
                bot.sendPhoto(chat_id, photo=open(latest_file, 'rb'))
                GPIO.output(26, GPIO.HIGH)
                print("Beep")
                sleep(3)
                GPIO.output(26, GPIO.LOW)
                bot.sendMessage(chat_id, "Sidik jari sesuai tapi Wajah tidak dikenali")
                bot.sendMessage(chat_id, "bila terdapat indikasi ketidak sesuaian data, harap hubungi pihak keamanan!")
                samplenum = samplenum+1
                videocam.release() # VideoCam berhenti merekam
                sleep(5)
                videocam = cv2.VideoCapture(0)
                videocam.set(cv2.CAP_PROP_FPS, 30)
                videocam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cv2.waitKey(5000)
        
    elif(fingerprint_sta == "Tidak ditemukan"):
        cand, frame = videocam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        muka = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in muka:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 5)
            id,conf=recognizer.predict(gray[y:y+h, x:x+w])
            if(id==1):
                id = "Arai"

            if(conf<=50):
                # Kondisi 3
                confid =" {0}%".format(round(100-conf))
                cv2.putText(frame, str(id), (x-5,y-5),font,2, (0,255,255),2, cv2.LINE_AA)
                cv2.putText(frame,str(confid), (x,y+h), font, 2, (0,255,255), 2, cv2.LINE_AA)
                cv2.imwrite("dikenal/img"+str(samplenum)+".jpg", frame)
                if not cv2.imwrite(r"dikenal/img"+str(samplenum)+".jpg", frame):
                    print("Foto tidak berhasil disimpan")
                    cv2.imwrite("dikenal/img"+str(samplenum)+".jpg", frame)
                print("Sidik jari tidak sesuai tapi Wajah dikenali")
                list_of_files = glob.glob('#DirektoriFolderProject/*') # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getctime)
                bot.sendPhoto(chat_id, photo=open(latest_file, 'rb'))
                GPIO.output(26, GPIO.HIGH)
                print("Beep")
                sleep(3)
                GPIO.output(26, GPIO.LOW)
                bot.sendMessage(chat_id, "Sidik jari tidak sesuai tapi Wajah dikenali")
                bot.sendMessage(chat_id, "bila terdapat indikasi ketidak sesuaian data, harap hubungi pihak keamanan!")
                samplenum = samplenum+1
                videocam.release() # VideoCam berhenti merekam
                sleep(5)
                videocam = cv2.VideoCapture(0)
                videocam.set(cv2.CAP_PROP_FPS, 30)
                videocam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        
            else:
                # Kondisi 4
                confid =" {0}%".format(round(100-conf))
                cv2.putText(frame, "Tidak Dikenal" , (x-5,y-5),font,2, (0,255,255),2, cv2.LINE_AA)
                cv2.putText(frame,str(confid), (x,y+h), font, 2, (0,255,255), 2, cv2.LINE_AA)
                cv2.imwrite("tidakkenal/img"+str(samplenum)+".jpg", frame)
                if not cv2.imwrite(r"tidakkenal/img"+str(samplenum)+".jpg", frame):
                    print("Foto tidak berhasil disimpan")
                    cv2.imwrite("tidakkenal/img"+str(samplenum)+".jpg", frame)
                print("Sidik jari tidak sesuai dan Wajah tidak dikenali")
                list_of_files = glob.glob('#DirektoriFolderProject/*') # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getctime)
                bot.sendPhoto(chat_id, photo=open(latest_file, 'rb'))
                GPIO.output(26, GPIO.HIGH)
                print("Beep")
                sleep(3)
                GPIO.output(26, GPIO.LOW)
                bot.sendMessage(chat_id, "Sidik jari dan Wajah tidak sesuai")
                bot.sendMessage(chat_id, "bila terjadi tindakan mencurigakan. Harap hubungi pihak keamanan!")
                samplenum = samplenum+1
                videocam.release() # VideoCam berhenti merekam
                sleep(5)
                videocam = cv2.VideoCapture(0)
                videocam.set(cv2.CAP_PROP_FPS, 30)
                videocam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cv2.waitKey(5000)
        
bot.polling()
videocam.release()
cv2.destroyAllWindows

