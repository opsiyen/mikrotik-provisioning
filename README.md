# MikroTik Core Router Provisioning with Netmiko

Proyek ini adalah skrip automasi berbasis Python menggunakan pustaka **Netmiko** untuk melakukan konfigurasi awal (*provisioning*) pada perangkat MikroTik RouterOS. Skrip ini dirancang untuk menyederhanakan dan menstandardisasi implementasi jaringan inti, menggantikan konfigurasi manual.

## Fitur Utama
Automasi ini akan mengeksekusi perintah CLI MikroTik untuk:
1. Membuat Bridge untuk WAN dan LAN.
2. Melakukan distribusi VLAN (Services, CCTV, IoT, Private, Public, Management).
3. Mengonfigurasi IP Addressing untuk setiap antarmuka.
4. Menerapkan pengerasan keamanan (*Security Hardening*) dengan mematikan layanan tidak aman (Telnet, FTP, SMB).
5. Konfigurasi NTP dan Manajemen Pengguna lokal.

## Persyaratan (Prerequisites)
- Python 3.11.2 atau lebih baru.
- MikroTik RouterOS (Diuji pada versi 6.x / 7.x).
- Akses SSH ke router harus sudah aktif (menggunakan user default atau admin sementara).

## Cara Instalasi
