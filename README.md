# MikroTik Router Provisioning with Netmiko

Proyek ini adalah skrip automasi berbasis Python menggunakan pustaka **Netmiko** untuk melakukan konfigurasi awal (*provisioning*) pada perangkat MikroTik RouterOS. Skrip ini dirancang untuk menyederhanakan dan menstandardisasi implementasi jaringan, menggantikan konfigurasi manual.

## Fitur Utama
1. Melakukan distribusi VLAN (Services, CCTV, IoT, Private, Guest, Management).
2. Mengonfigurasi IP Addressing untuk setiap antarmuka.
3. Menerapkan *Security Hardening* dengan mematikan layanan tidak aman (Telnet, FTP, SMB).
4. Auto detiksi versi mayor (v6/v7) routeros
5. dry-run, mode simulasi tanpa eksikusi nyata.
6. Idempotensi, sebagai pencegahan error duplikasi.
7. Logging, sebagai catatan aktivitas.

## Persyaratan (Prerequisites)
- MikroTik RouterOS (Diuji pada versi 6.49 / 7.22).
- Akses SSH ke router harus sudah aktif.
- Python 3.11.2 atau lebih baru.
  - netmiko
  - python-dotenv
  - pyyaml 
## Cara Instalasi
## Menjalankan
- DRY_RUN=True python3 script/provision_core.py
- python3 script/provision_core.py
