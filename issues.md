# [Feature] Provisioning Awal Konfigurasi Router Core (MikroTik) via Netmiko

## Deskripsi Proyek
Issue ini bertujuan untuk membuat script automasi Python menggunakan *library* **Netmiko** untuk melakukan konfigurasi dasar (provisioning) pada perangkat MikroTik RouterOS. Script harus mengeksekusi perintah CLI MikroTik secara berurutan sesuai dengan daftar tugas di bawah ini. 

**Catatan untuk Developer/AI:** - Gunakan sintaks CLI standar MikroTik RouterOS (contoh: `/interface bridge add name=...`).
- Pastikan script memiliki error handling dasar jika koneksi SSH terputus atau perintah gagal dieksekusi.

---

## Daftar Tugas (Task List)

### [cite_start]1. Konfigurasi Bridge dan Port [cite: 1, 2]
- [ ] [cite_start]Buat interface bridge baru bernama `bridge-wan`.
- [ ] [cite_start]Buat interface bridge baru bernama `bridge-lan`.
- [ ] [cite_start]Masukkan interface `ether1` ke dalam port `bridge-wan`.
- [ ] [cite_start]Masukkan interface `ether2`, `ether3`, `ether4`, dan `ether5` ke dalam port `bridge-lan`.
[cite_start]*(Catatan: Pemisahan ini menggantikan ide awal menggabungkan semua ether ke satu bridge, demi memisahkan traffic WAN dan LAN secara logikal [cite: 1, 2])*

### [cite_start]2. Konfigurasi VLAN pada Bridge LAN 
Buat VLAN berikut dengan *parent interface* `bridge-lan`:
- [ ] [cite_start]`vlan10-services` (VLAN ID: 10) 
- [ ] [cite_start]`vlan11-cctv` (VLAN ID: 11) 
- [ ] [cite_start]`vlan12-iot` (VLAN ID: 12) 
- [ ] [cite_start]`vlan13-private` (VLAN ID: 13) 
- [ ] [cite_start]`vlan14-public` (VLAN ID: 14) 
- [ ] [cite_start]`vlan15-management` (VLAN ID: 15) 

### [cite_start]3. Pengalamatan IP (IP Addressing) [cite: 2, 3]
Tambahkan IP Address berikut ke masing-masing interface VLAN (Subnet /28):
- [ ] [cite_start]`192.168.101.1/28` pada interface `vlan10-services` 
- [ ] [cite_start]`192.168.101.17/28` pada interface `vlan11-cctv` 
- [ ] [cite_start]`192.168.101.33/28` pada interface `vlan12-iot` 
- [ ] [cite_start]`192.168.101.49/28` pada interface `vlan13-private` [cite: 3]
- [ ] [cite_start]`192.168.101.65/28` pada interface `vlan14-public` [cite: 3]
- [ ] [cite_start]`192.168.101.81/28` pada interface `vlan15-management` [cite: 3]

### [cite_start]4. Keamanan dan Interface List [cite: 3]
- [ ] [cite_start]Buat *Interface List* baru dengan nama `allow`[cite: 3].
- [ ] [cite_start]Tambahkan interface `vlan13-private` dan `vlan15-management` ke dalam *Interface List* `allow`[cite: 3].
- [ ] [cite_start]Konfigurasi *Neighbor Discovery* agar hanya aktif pada *Interface List* `allow`[cite: 3].

### [cite_start]5. Hardening & Optimalisasi Sistem [cite: 3, 4]
Lakukan eksekusi perintah untuk mematikan layanan yang tidak aman/tidak perlu:
- [ ] [cite_start]Matikan fitur MAC Server (MAC Telnet, MAC Winbox, dan MAC Ping)[cite: 3].
- [ ] [cite_start]Matikan fitur IPv6[cite: 4].
- [ ] [cite_start]Matikan Btest server (Bandwidth Test)[cite: 4].
- [ ] [cite_start]Matikan Proxy server[cite: 4].
- [ ] [cite_start]Matikan layanan SMB[cite: 4].
- [ ] [cite_start]Matikan IP Services yang tidak digunakan: `ftp`, `telnet`, `www-ssl`, `api-ssl`[cite: 4]. (Catatan: Pastikan SSH dan Winbox tetap menyala untuk akses remote).
- [ ] [cite_start]Ubah *Identity* router menjadi `router-core`[cite: 4].

### [cite_start]6. Waktu dan NTP (Network Time Protocol) [cite: 3, 4]
- [ ] [cite_start]Atur zona waktu (Timezone) router ke `Asia/Jakarta`[cite: 3].
- [ ] [cite_start]Aktifkan NTP Client dan arahkan ke NTP Server: `0.id.pool.ntp.org`[cite: 4].

### [cite_start]7. Manajemen User (User Management) [cite: 4]
- [ ] [cite_start]Buat user baru: Nama = `opsiyen`, Group = `full`, Password = `opsiyen`[cite: 4].
- [ ] [cite_start]Buat user baru: Nama = `netmikowrite`, Group = `write`, Password = `netmikowrite`[cite: 4].
- [ ] [cite_start]Verifikasi keberadaan default user `admin`, lalu hapus atau nonaktifkan user tersebut[cite: 4].
