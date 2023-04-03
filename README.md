# ◈ Sistem Keamanan Brankas ◈

### Tentang Alat
Alat Sistem Keamanan Brankas merupakan Tugas Akhir

Hardware yang dipakai :
```◈ AS608 Fingerprint Sensor\
◈ Buzzer\
◈ Camera OV5647\
◈ Raspberry Pi 4\
◈ Relay\
◈ Solenoid

Software yang dipakai :\
◈ OpenCV\
◈ Python\
◈ Telepot\
◈ ThonnyIDE
```



## ◈ FAQ ◈

#### 1. Cara Kerja Alat?

Alat mempunyai 4 Kondisi, yaitu :

```ⅰ. Sidik jari dan Wajah dikenali
Output: Buzzer mengeluarkan suara 2 kali dan Solenoid terbuka
Telegram:
▸ Sidik jari dan Wajah sesuai
▸ Brankas terbuka dengan aman

ⅱ. Sidik jari sesuai tapi Wajah tidak dikenali
Output: Buzzer mengeluarkan suara 1 kali dan Solenoid tertutup
Telegram :
▸ Sidik jari sesuai tapi Wajah tidak dikenali
▸ bila terdapat indikasi ketidak sesuaian data, harap hubungi pihak keamanan!

ⅲ. Sidik jari tidak sesuai tapi Wajah dikenali
Output: Buzzer mengeluarkan suara 1 kali dan Solenoid tertutup
Telegram:
▸ Sidik jari tidak sesuai tapi Wajah dikenali
▸ bila terdapat indikasi ketidak sesuaian data, harap hubungi pihak keamanan!

ⅳ. Sidik jari dan Wajah tidak dikenali
Output: Buzzer mengeluarkan suara 1 kali dan Solenoid tertutup
Telegram:
▸ Sidik jari dan Wajah tidak dikenali
▸ bila terdapat indikasi ketidak sesuaian data, harap hubungi pihak keamanan!
```
